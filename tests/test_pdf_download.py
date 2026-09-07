# Live smoke test. Requires internet and Chromium.
# Run explicitly with:
# pytest -q tests/test_pdf_download.py -s

from scraper.downloader import PDFDownloader


SCHEME_NAME = "Pradhan Mantri Kisan Samman Nidhi"
SCHEME_URL = (
    "https://schemes.vikaspedia.in/viewcontent/schemesall/"
    "schemes-for-farmers/pradhan-mantri-kisan-samman-nidhi?lgn=en"
)


def test_pdf_download(tmp_path):
    with PDFDownloader(tmp_path, headless=True, retries=3) as downloader:
        result = downloader.download(SCHEME_NAME, SCHEME_URL)
        assert result["success"] is True
        assert result["path"].endswith("Pradhan_Mantri_Kisan_Samman_Nidhi.pdf")
