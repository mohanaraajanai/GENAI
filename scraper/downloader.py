"""
Vikaspedia PDF downloader.

Responsibilities:
1. Open an individual scheme page.
2. Locate "Download as PDF".
3. Click the button.
4. Save the generated PDF.
5. Retry failed downloads.
"""

from pathlib import Path
import re

from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


class PDFDownloader:
    """
    Download Vikaspedia scheme PDFs.

    Example:

        downloader = PDFDownloader(
            output_dir="downloads",
            headless=True
        )

        downloader.download(
            scheme_name="Pradhan Mantri Kisan Samman Nidhi",
            scheme_url="https://..."
        )

        downloader.close()
    """

    def __init__(
        self,
        output_dir="downloads",
        headless=True,
        timeout=30000,
        retries=3,
    ):

        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.headless = headless
        self.timeout = timeout
        self.retries = retries

        self.playwright = None
        self.browser = None
        self.page = None

    # ----------------------------------------------------------------
    # Start browser
    # ----------------------------------------------------------------

    def start(self):

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )

        self.page = self.browser.new_page(
            viewport={
                "width": 1440,
                "height": 1000,
            },
            accept_downloads=True,
        )

        self.page.set_default_timeout(
            self.timeout
        )

    # ----------------------------------------------------------------
    # Close browser
    # ----------------------------------------------------------------

    def close(self):

        try:

            if self.browser:
                self.browser.close()

        finally:

            if self.playwright:
                self.playwright.stop()

        self.browser = None
        self.page = None
        self.playwright = None

    # ----------------------------------------------------------------
    # Create safe filename
    # ----------------------------------------------------------------

    @staticmethod
    def safe_filename(name: str) -> str:
        """
        Convert scheme name into a Windows-safe filename.
        """

        filename = re.sub(
            r'[<>:"/\\|?*]',
            "_",
            name
        )

        filename = re.sub(
            r"\s+",
            "_",
            filename
        )

        return filename.strip("._ ")

    # ----------------------------------------------------------------
    # Download one PDF
    # ----------------------------------------------------------------

    def download(
        self,
        scheme_name: str,
        scheme_url: str,
    ) -> dict:
        """
        Download one scheme PDF.

        Returns:

            {
                "success": True,
                "name": "...",
                "path": "...",
                "error": None
            }
        """

        if not self.page:
            self.start()

        filename = (
            self.safe_filename(scheme_name)
            + ".pdf"
        )

        output_file = (
            self.output_dir
            / filename
        )

        for attempt in range(
            1,
            self.retries + 1
        ):

            try:

                print(
                    f"\nDownloading: {scheme_name}"
                )

                print(
                    f"Attempt {attempt}/"
                    f"{self.retries}"
                )

                # ----------------------------------------------------
                # Open individual scheme page.
                # ----------------------------------------------------

                self.page.goto(
                    scheme_url,
                    wait_until="domcontentloaded",
                    timeout=60000,
                )

                self.page.wait_for_timeout(
                    2000
                )

                # ----------------------------------------------------
                # Confirm the PDF button.
                # ----------------------------------------------------

                pdf_button = self.page.locator(
                    'button[title="Download as PDF"]'
                ).first

                pdf_button.wait_for(
                    state="visible",
                    timeout=self.timeout,
                )

                # ----------------------------------------------------
                # Click and capture browser download.
                # ----------------------------------------------------

                with self.page.expect_download(
                    timeout=self.timeout
                ) as download_info:

                    pdf_button.click()

                download = download_info.value

                print(
                    "Suggested filename:",
                    download.suggested_filename
                )

                # ----------------------------------------------------
                # Save PDF.
                # ----------------------------------------------------

                download.save_as(
                    str(output_file)
                )

                # ----------------------------------------------------
                # Verify file.
                # ----------------------------------------------------

                if (
                    output_file.exists()
                    and output_file.stat().st_size > 0
                ):

                    print(
                        "Download successful:",
                        output_file
                    )

                    return {
                        "success": True,
                        "name": scheme_name,
                        "path": str(
                            output_file
                        ),
                        "error": None,
                    }

                raise RuntimeError(
                    "Downloaded PDF is empty."
                )

            except PlaywrightTimeoutError as exc:

                error = (
                    f"Timeout while downloading "
                    f"{scheme_name}: {exc}"
                )

                print(error)

            except Exception as exc:

                error = (
                    f"Error downloading "
                    f"{scheme_name}: {exc}"
                )

                print(error)

            # --------------------------------------------------------
            # Retry
            # --------------------------------------------------------

            if attempt < self.retries:

                print(
                    "Retrying..."
                )

                self.page.wait_for_timeout(
                    2000
                )

        return {
            "success": False,
            "name": scheme_name,
            "path": None,
            "error": error,
        }