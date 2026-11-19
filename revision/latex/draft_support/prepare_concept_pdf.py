"""Prepare the author-supplied concept slide for anonymous LaTeX inclusion.

Input: a PDF exported from 概念图.pptx. Keep slide content unchanged,
trim outer whitespace, and discard author metadata.
"""
import argparse
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

parser = argparse.ArgumentParser()
parser.add_argument("source")
parser.add_argument("destination")
parser.add_argument("--page", type=int, default=1, help="One-based PDF page")
parser.add_argument("--title", default="EvoForma conceptual overview",
                    help="Anonymous PDF title")
parser.add_argument("--crop", type=float, nargs=4, default=(5, 35, 955, 507),
                    metavar=("LEFT", "BOTTOM", "RIGHT", "TOP"))
args = parser.parse_args()
reader = PdfReader(args.source)
if not 1 <= args.page <= len(reader.pages):
    raise ValueError("Requested page is outside the exported presentation")
page = reader.pages[args.page - 1]
page.mediabox = RectangleObject(args.crop)
page.cropbox = RectangleObject(args.crop)
writer = PdfWriter()
writer.add_page(page)
writer.add_metadata({"/Title": args.title, "/Author": ""})
with open(args.destination, "wb") as stream:
    writer.write(stream)
