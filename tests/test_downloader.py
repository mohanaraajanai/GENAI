from scraper.downloader import PDFDownloader


def test_safe_filename():
    name = PDFDownloader.safe_filename("Pradhan Mantri Kisan Samman Nidhi")
    assert name == "Pradhan_Mantri_Kisan_Samman_Nidhi"
