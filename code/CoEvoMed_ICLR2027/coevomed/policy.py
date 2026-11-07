from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass

import torch
from torch import nn

ACTIONS = ("balanced", "repair_heavy", "weakness_focus", "retention_heavy")
REPAIR = dict(zip(ACTIONS, (0.65, 0.80, 0.70, 0.50)))


class ActorCritic(nn.Module):
    def __init__(self):
        super().__init__()
        self.shared = nn.Sequential(nn.Linear(40, 128), nn.Tanh(), nn.Linear(128, 64), nn.Tanh())
        self.actor = nn.Linear(64, 4)
        self.critic = nn.Linear(64, 1)

    def forward(self, state):
        hidden = self.shared(state)
        return self.actor(hidden), self.critic(hidden).squeeze(-1)


@dataclass(frozen=True)
class Decision:
    episode: int
    update_index: int
    action: int
    probabilities: list[float]
    old_logp: float
    old_value: float

    @property
    def name(self):
        return ACTIONS[self.action]


class Controller:
    def __init__(self, seed=42):
        self.seed = int(seed)
        with torch.random.fork_rng(devices=[]):
            torch.manual_seed(self.seed)
            self.model = ActorCritic()
        nn.init.zeros_(self.model.critic.weight)
        nn.init.zeros_(self.model.critic.bias)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=3e-4)
        self.update_index = 0

    def distribution(self, state):
        x = torch.as_tensor(state, dtype=torch.float32)
        if x.shape[-1] != 40 or not torch.isfinite(x).all():
            raise ValueError("Expected finite 40-dimensional states")
        logits, value = self.model(x)
        return 0.8 * logits.softmax(dim=-1) + 0.05, value

    def sample(self, state, episode):
        with torch.no_grad():
            probs, value = self.distribution(state)
        material = f"{self.seed}:{episode}:{self.update_index}"
        seed = int(hashlib.sha256(material.encode()).hexdigest()[:16], 16)
        generator = torch.Generator().manual_seed(seed)
        action = int(torch.multinomial(probs, 1, generator=generator).item())
        return Decision(episode, self.update_index, action, probs.tolist(),
                        math.log(float(probs[action])), float(value))

    def update(self, state, decision, reward, next_state, *, terminal=False):
        if decision.update_index != self.update_index:
            raise ValueError("Stale/off-policy transition or duplicate completion")
        if not math.isfinite(reward):
            raise ValueError("Non-finite reward")
        with torch.no_grad():
            current, _ = self.distribution(state)
            if abs(math.log(float(current[decision.action])) - decision.old_logp) > 1e-5:
                raise ValueError("Stored behavior likelihood does not match this controller")
            _, next_value = self.distribution(next_state)
            target = torch.tensor(reward) + 0.9 * next_value * (not terminal)
            advantage = target - decision.old_value
        old_logp = torch.tensor(decision.old_logp)
        epochs = []
        before = self.weights_digest()
        for _ in range(4):
            mu, value = self.distribution(state)
            ratio = torch.exp(torch.log(mu[decision.action]) - old_logp)
            policy_loss = -torch.minimum(ratio * advantage, ratio.clamp(0.8, 1.2) * advantage)
            value_loss = (value - target).square()
            entropy = -(mu * mu.log()).sum()
            loss = policy_loss + 0.5 * value_loss - 0.01 * entropy
            if not torch.isfinite(loss):
                raise FloatingPointError("PPO loss is non-finite")
            self.optimizer.zero_grad(set_to_none=True)
            loss.backward()
            grad = nn.utils.clip_grad_norm_(self.model.parameters(), 0.5)
            if not torch.isfinite(grad):
                raise FloatingPointError("PPO gradient is non-finite")
            self.optimizer.step()
            epochs.append({"ratio": float(ratio.detach()), "loss": float(loss.detach()),
                           "policy_loss": float(policy_loss.detach()), "value_loss": float(value_loss.detach()),
                           "entropy": float(entropy.detach())})
        self.update_index += 1
        return {"update_index": self.update_index, "reward": reward, "advantage": float(advantage),
                "value_target": float(target), "terminal": terminal, "old_logp": decision.old_logp,
                "epochs": epochs, "weights_before": before, "weights_after": self.weights_digest()}

    def weights_digest(self):
        h = hashlib.sha256()
        for name, value in sorted(self.model.state_dict().items()):
            h.update(name.encode()); h.update(value.detach().numpy().tobytes())
        return h.hexdigest()

    def save(self, path):
        torch.save({"model": self.model.state_dict(), "optimizer": self.optimizer.state_dict(),
                    "seed": self.seed, "update_index": self.update_index}, path)

    def load(self, path):
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        self.model.load_state_dict(checkpoint["model"])
        self.optimizer.load_state_dict(checkpoint["optimizer"])
        self.seed = checkpoint["seed"]
        self.update_index = checkpoint["update_index"]

    def load_actor(self, path, active_tasks=None):
        state = torch.load(path, map_location="cpu", weights_only=True)
        if active_tasks is not None and set(state.get("active_tasks", ())) != set(active_tasks):
            raise ValueError("BC Actor active-task profile is missing or incompatible")
        state = state.get("model_state_dict", state.get("model", state))
        required = {k for k in self.model.state_dict() if not k.startswith("critic.")}
        actor = {k: state[k] for k in required if k in state}
        if set(actor) != required:
            raise ValueError("Warm start must contain every shared/Actor parameter")
        self.model.load_state_dict(actor, strict=False)
        nn.init.zeros_(self.model.critic.weight); nn.init.zeros_(self.model.critic.bias)
