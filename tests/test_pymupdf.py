from pathlib import Path
import fitz


pdf_path = Path("downloads/Crop_insurance_schemes.pdf")

doc = fitz.open(pdf_path)

print("=" * 70)
print("PYMUPDF TEXT EXTRACTION TEST")
print("=" * 70)

print(f"File  : {pdf_path}")
print(f"Pages : {len(doc)}")

for page_number, page in enumerate(doc):

    text = page.get_text("text").strip()

    print()
    print("=" * 70)
    print(f"PAGE {page_number + 1}")
    print("=" * 70)

    print(f"Characters : {len(text)}")
    print()

    print(text[:2000])

    if page_number == 2:
        break

doc.close()