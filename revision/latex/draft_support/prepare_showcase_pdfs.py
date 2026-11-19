"""Prepare native PowerPoint PDF exports for the appendix without rasterizing."""
from pathlib import Path
import argparse
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

ROOT = Path(__file__).resolve().parents[1]


def save(pages, destination, title):
    writer = PdfWriter()
    for page in pages:
        writer.add_page(page)
    writer.add_metadata({"/Title": title, "/Author": ""})
    with destination.open("wb") as handle:
        writer.write(handle)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only-3d", action="store_true", help="Preserve all existing 2D exports")
    args = parser.parse_args()
    three_d = PdfReader(ROOT / "showcase/medical_vqa_3d_editable.pdf")
    assert len(three_d.pages) == 3
    if not args.only_3d:
        two_d = PdfReader(ROOT / "tmp/pdfs/showcase_latest/medical_vqa_editable.pdf")
        assert len(two_d.pages) == 3
        save(two_d.pages, ROOT / "showcase/medical_vqa_editable.pdf", "CoEvoMed 2D dialogue examples")
        save(two_d.pages, ROOT / "figures/showcase/medical_vqa_2d.pdf", "CoEvoMed 2D dialogue examples")
    # Keep source typography and images as native PDF content, with two
    # benchmark panels stacked in source order and no duplicated examples.
    width = float(three_d.pages[0].mediabox.width)
    height = float(three_d.pages[0].mediabox.height)
    gap = 12
    pair = PageObject.create_blank_page(width=width, height=height * 2 + gap)
    pair.merge_transformed_page(three_d.pages[0], Transformation().translate(0, height + gap))
    pair.merge_page(three_d.pages[1])
    save([pair, three_d.pages[2]], ROOT / "figures/showcase/medical_vqa_3d_pairs.pdf", "CoEvoMed 3D dialogue examples")
    print("Prepared 2 3D pages (2 + 1 benchmarks)." if args.only_3d else "Prepared 3 two-benchmark 2D pages and 2 3D pages (2 + 1 benchmarks).")


if __name__ == "__main__":
    main()
