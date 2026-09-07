from pathlib import Path

import pymupdf
import pytesseract
from PIL import Image


PDF_PATH = Path("downloads/Crop_insurance_schemes.pdf")


print("=" * 70)
print("OCR PDF EXTRACTION TEST")
print("=" * 70)

print(f"PDF: {PDF_PATH}")

pdf = pymupdf.open(PDF_PATH)

print(f"Pages: {len(pdf)}")

for page_number, page in enumerate(pdf):

    print()
    print("=" * 70)
    print(f"PAGE {page_number + 1}")
    print("=" * 70)

    # Render PDF page as an image
    pixmap = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2),
        alpha=False,
    )

    # Convert PyMuPDF image to PIL image
    image = Image.frombytes(
        "RGB",
        [pixmap.width, pixmap.height],
        pixmap.samples,
    )

    # OCR
    text = pytesseract.image_to_string(
        image,
        lang="eng",
    ).strip()

    print(f"OCR characters: {len(text)}")
    print()

    print(text[:3000])

    # Test first 3 pages only
    if page_number >= 2:
        break

pdf.close()