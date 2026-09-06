from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

SCHEME_URL = (
    "https://schemes.vikaspedia.in/viewcontent/schemesall/"
    "schemes-for-farmers/pradhan-mantri-kisan-samman-nidhi?lgn=en"
)

DOWNLOAD_DIR = Path(__file__).resolve().parents[1] / "downloads"
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = DOWNLOAD_DIR / "Pradhan_Mantri_Kisan_Samman_Nidhi.pdf"


def download_pdf(page, output_file, retries=3):
    """Click Download as PDF and save the generated file."""
    for attempt in range(1, retries + 1):
        try:
            print(f"\nDownload attempt {attempt}/{retries}")

            button = page.locator('button[title="Download as PDF"]').first
            button.wait_for(state="visible", timeout=30000)

            with page.expect_download(timeout=30000) as info:
                button.click()

            download = info.value
            print("Suggested filename:", download.suggested_filename)
            download.save_as(str(output_file))

            if output_file.exists() and output_file.stat().st_size > 0:
                print("\nSUCCESS!")
                print("PDF:", output_file)
                print(f"Size: {output_file.stat().st_size:,} bytes")
                return True

        except PlaywrightTimeoutError as exc:
            print("TIMEOUT:", exc)
        except Exception as exc:
            print("ERROR:", exc)

        if attempt < retries:
            print("Retrying...")
            page.wait_for_timeout(2000)

    return False


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(
            viewport={"width": 1440, "height": 1000},
            accept_downloads=True,
        )

        print("\nOpening individual scheme page...")
        page.goto(SCHEME_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(2500)

        print("PAGE TITLE:", page.title())
        print("CURRENT URL:", page.url)

        try:
            h1 = page.locator("h1").first
            h1.wait_for(state="visible", timeout=30000)
            print("H1:", h1.inner_text().strip())
        except Exception:
            print("WARNING: H1 not found.")

        print("\nLooking for Download as PDF...")
        success = download_pdf(page, OUTPUT_FILE)

        print("\nRESULT:", "PASSED" if success else "FAILED")
        input("\nPress Enter to close the browser...")
        browser.close()


if __name__ == "__main__":
    main()
