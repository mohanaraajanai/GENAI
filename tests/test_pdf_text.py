from pathlib import Path
from pypdf import PdfReader


pdf_path = Path("downloads/Crop_insurance_schemes.pdf")

reader = PdfReader(str(pdf_path))

print("=" * 70)
print("PDF TEXT EXTRACTION TEST")
print("=" * 70)

print(f"File       : {pdf_path}")
print(f"Pages      : {len(reader.pages)}")

for i, page in enumerate(reader.pages[:3]):

    print()
    print("=" * 70)
    print(f"PAGE {i + 1}")
    print("=" * 70)

    text = page.extract_text() or ""

    print(f"Characters : {len(text)}")
    print()
    print(text[:2000])