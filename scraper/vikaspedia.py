"""
Vikaspedia scraper.

Responsibilities:
1. Open the Farmer Schemes listing page.
2. Handle pagination.
3. Extract the actual scheme names.
4. Click each scheme card.
5. Capture the individual scheme URL.

The PDF downloading itself is handled by downloader.py.
"""

from typing import List, Dict

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError


# -------------------------------------------------------------------
# Default Vikaspedia Farmer Schemes URL
# -------------------------------------------------------------------

DEFAULT_URL = (
    "https://schemes.vikaspedia.in/viewcontent/schemesall/"
    "schemes-for-farmers?lgn=en"
)


# -------------------------------------------------------------------
# These are UI elements that appear inside h6[title] but are NOT
# farmer schemes.
# -------------------------------------------------------------------

EXCLUDED_TITLES = {
    "Lets Connect",
    "Let's Connect",
    "menu",
}


class VikaspediaScraper:
    """
    Scraper class for Vikaspedia Farmer Schemes.

    Example:

        scraper = VikaspediaScraper(headless=False)

        schemes = scraper.get_all_schemes()

        for scheme in schemes:
            print(scheme["name"])
            print(scheme["url"])

        scraper.close()
    """

    def __init__(self, headless=True, timeout=30000):
        """
        Initialize Playwright.

        headless=True:
            Browser runs in the background.

        headless=False:
            Browser window is visible.
            Useful for debugging.
        """

        self.headless = headless
        self.timeout = timeout

        self.playwright = None
        self.browser = None
        self.page = None

    # ----------------------------------------------------------------
    # Browser handling
    # ----------------------------------------------------------------

    def start(self):
        """Start Playwright and open Chromium."""

        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=self.headless
        )

        self.page = self.browser.new_page(
            viewport={
                "width": 1440,
                "height": 1000,
            }
        )

        self.page.set_default_timeout(self.timeout)

    def close(self):
        """Close browser and Playwright safely."""

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
    # Open listing page
    # ----------------------------------------------------------------

    def open_listing_page(self, url: str):
        """
        Open the main Farmer Schemes page.
        """

        if not self.page:
            self.start()

        print(f"Opening: {url}")

        self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        # React/Material UI needs a little time to render.
        self.page.wait_for_timeout(2500)

        # Wait until scheme cards are available.
        self.page.wait_for_selector(
            'h6[title]',
            state="visible",
            timeout=self.timeout,
        )

    # ----------------------------------------------------------------
    # Extract scheme titles
    # ----------------------------------------------------------------

    def get_scheme_titles(self) -> List[str]:
        """
        Extract scheme names from the current listing page.

        The site displays the visible title in truncated text, but
        stores the complete scheme name in the HTML title attribute.

        Example:

            <h6 title="Pradhan Mantri Kisan Samman Nidhi">
        """

        self.page.wait_for_selector(
            'h6[title]',
            state="visible",
            timeout=self.timeout,
        )

        titles = self.page.locator(
            'h6[title]'
        ).evaluate_all(
            """
            els => els
                .map(el => (el.getAttribute('title') || '').trim())
                .filter(Boolean)
            """
        )

        # Remove duplicates while preserving order.
        titles = list(dict.fromkeys(titles))

        # Remove UI elements that are not schemes.
        titles = [
            title
            for title in titles
            if title not in EXCLUDED_TITLES
        ]

        return titles

    # ----------------------------------------------------------------
    # Find pagination controls
    # ----------------------------------------------------------------

    def get_pagination_numbers(self) -> List[int]:
        """
        Detect visible numeric pagination controls.

        The current website exposes:

            1 2 3 4 5

        We don't hard-code those values. Instead, we inspect the
        actual page.
        """

        controls = self.page.locator(
            "button, a, [role='button']"
        )

        numbers = []

        for i in range(controls.count()):

            try:
                control = controls.nth(i)

                if not control.is_visible():
                    continue

                text = control.inner_text().strip()

                if text.isdigit():
                    number = int(text)

                    if number not in numbers:
                        numbers.append(number)

            except Exception:
                continue

        return sorted(numbers)

    # ----------------------------------------------------------------
    # Click pagination page
    # ----------------------------------------------------------------

    def open_pagination_page(self, page_number: int):
        """
        Click a specific pagination number.
        """

        controls = self.page.locator(
            "button, a, [role='button']"
        )

        for i in range(controls.count()):

            try:
                control = controls.nth(i)

                if not control.is_visible():
                    continue

                text = control.inner_text().strip()

                if text == str(page_number):

                    control.click()

                    # Allow React to update the listing.
                    self.page.wait_for_timeout(1500)

                    self.page.wait_for_selector(
                        'h6[title]',
                        state="visible",
                        timeout=self.timeout,
                    )

                    return True

            except Exception:
                continue

        return False

    # ----------------------------------------------------------------
    # Find a specific scheme card
    # ----------------------------------------------------------------

    def find_scheme_card(self, scheme_name: str):
        """
        Find the Material UI card for a scheme.

        Important:
        The scheme card does not necessarily contain an href.

        The confirmed DOM structure is:

            h6[title="..."]
                 ↓
            ancestor div[@title]
                 ↓
            clickable Material UI card
        """

        title_locator = self.page.locator(
            f'h6[title="{scheme_name}"]'
        ).first

        title_locator.wait_for(
            state="visible",
            timeout=self.timeout,
        )

        # Find the nearest ancestor that contains the title attribute.
        card = title_locator.locator(
            "xpath=ancestor::div[@title][1]"
        )

        card.wait_for(
            state="visible",
            timeout=self.timeout,
        )

        return card

    # ----------------------------------------------------------------
    # Open individual scheme
    # ----------------------------------------------------------------

    def open_scheme(self, scheme_name: str) -> str:
        """
        Click a scheme card and return its individual URL.

        Example:

        https://schemes.vikaspedia.in/viewcontent/schemesall/
        schemes-for-farmers/pradhan-mantri-kisan-samman-nidhi?lgn=en
        """

        listing_url = self.page.url

        card = self.find_scheme_card(
            scheme_name
        )

        print(f"Opening scheme: {scheme_name}")

        card.click()

        # Wait until URL changes from the listing page.
        try:

            self.page.wait_for_url(
                lambda url: str(url) != listing_url,
                timeout=self.timeout,
            )

        except PlaywrightTimeoutError:

            # Sometimes React navigation takes longer.
            self.page.wait_for_timeout(2000)

        individual_url = self.page.url

        if individual_url == listing_url:

            raise RuntimeError(
                f"Could not open scheme: {scheme_name}"
            )

        print(f"Individual URL: {individual_url}")

        return individual_url

    # ----------------------------------------------------------------
    # Return to listing
    # ----------------------------------------------------------------

    def return_to_listing(self, listing_url: str):
        """
        Return to the main listing page.

        We navigate directly instead of relying on browser history.
        """

        self.page.goto(
            listing_url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        self.page.wait_for_timeout(2000)

        self.page.wait_for_selector(
            'h6[title]',
            state="visible",
            timeout=self.timeout,
        )

    # ----------------------------------------------------------------
    # Scan all schemes
    # ----------------------------------------------------------------

    def get_all_schemes(self, url: str = DEFAULT_URL) -> List[Dict]:
        """
        Scan all pagination pages and discover individual scheme URLs.

        Returns:

            [
                {
                    "name": "Pradhan Mantri Kisan Samman Nidhi",
                    "url": "https://..."
                },
                ...
            ]
        """

        self.open_listing_page(url)

        listing_url = self.page.url

        all_schemes = []

        # Detect pagination pages.
        pagination_numbers = self.get_pagination_numbers()

        if not pagination_numbers:
            pagination_numbers = [1]

        print(
            f"Pagination pages detected: {pagination_numbers}"
        )

        # ------------------------------------------------------------
        # Process every pagination page.
        # ------------------------------------------------------------

        for page_number in pagination_numbers:

            print(
                f"\nProcessing pagination page {page_number}"
            )

            # Page 1 is already open.
            if page_number != 1:

                self.return_to_listing(listing_url)

                success = self.open_pagination_page(
                    page_number
                )

                if not success:

                    print(
                        f"Could not open pagination page "
                        f"{page_number}"
                    )

                    continue

            scheme_names = self.get_scheme_titles()

            print(
                f"Found {len(scheme_names)} schemes "
                f"on page {page_number}"
            )

            # --------------------------------------------------------
            # Open every scheme on this page.
            # --------------------------------------------------------

            for scheme_name in scheme_names:

                try:

                    self.return_to_listing(
                        listing_url
                    )

                    # Re-open the required pagination page.
                    if page_number != 1:

                        success = self.open_pagination_page(
                            page_number
                        )

                        if not success:
                            raise RuntimeError(
                                f"Could not return to pagination "
                                f"page {page_number}"
                            )

                    individual_url = self.open_scheme(
                        scheme_name
                    )

                    all_schemes.append(
                        {
                            "name": scheme_name,
                            "url": individual_url,
                            "page": page_number,
                        }
                    )

                except Exception as exc:

                    print(
                        f"ERROR: {scheme_name} -> {exc}"
                    )

        # Remove duplicate URLs.
        unique_schemes = []
        seen_urls = set()

        for scheme in all_schemes:

            if scheme["url"] not in seen_urls:

                seen_urls.add(
                    scheme["url"]
                )

                unique_schemes.append(
                    scheme
                )

        print(
            f"\nTotal unique schemes: "
            f"{len(unique_schemes)}"
        )

        return unique_schemes