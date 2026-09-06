from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

LISTING_URL = "https://schemes.vikaspedia.in/viewcontent/schemesall/schemes-for-farmers?lgn=en"


def get_scheme_titles(page):
    """Extract full scheme names from the title attribute used by the listing cards."""
    page.wait_for_selector('h6[title]', state="visible", timeout=30000)
    titles = page.locator('h6[title]').evaluate_all(
        """els => els.map(e => (e.getAttribute('title') || '').trim()).filter(Boolean)"""
    )
    return list(dict.fromkeys(titles))


def get_numeric_controls(page):
    """Find visible button/link/role-button controls whose text is a page number."""
    controls = page.locator("button, a, [role='button']")
    found = []
    for i in range(controls.count()):
        try:
            item = controls.nth(i)
            if item.is_visible():
                text = item.inner_text().strip()
                if text.isdigit():
                    found.append((text, i))
        except Exception:
            pass
    return found


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})

        print("\nOpening Farmer Schemes page...")
        page.goto(LISTING_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        print("\nPAGE TITLE:", page.title())
        print("CURRENT URL:", page.url)

        all_schemes = []
        controls = get_numeric_controls(page)
        page_numbers = sorted({int(text) for text, _ in controls})

        print("\nVISIBLE NUMERIC PAGINATION CONTROLS:", page_numbers)

        if not page_numbers:
            print("WARNING: No numeric pagination controls found. Extracting page 1 only.")

        # Always extract the currently displayed first page.
        titles = get_scheme_titles(page)
        print(f"\nPAGE 1 - {len(titles)} schemes")
        for title in titles:
            print("  -", title)
        all_schemes.extend(titles)

        for number in page_numbers:
            if number == 1:
                continue

            print(f"\nOpening pagination page {number}...")
            controls = get_numeric_controls(page)
            match = next(((text, i) for text, i in controls if text == str(number)), None)

            if not match:
                print(f"WARNING: Page button {number} not found.")
                continue

            try:
                page.locator("button, a, [role='button']").nth(match[1]).click()
                page.wait_for_timeout(1500)
                page.wait_for_selector('h6[title]', state="visible", timeout=30000)

                titles = get_scheme_titles(page)
                print(f"PAGE {number} - {len(titles)} schemes")
                for title in titles:
                    print("  -", title)
                all_schemes.extend(titles)

            except PlaywrightTimeoutError as exc:
                print(f"TIMEOUT on page {number}: {exc}")
            except Exception as exc:
                print(f"ERROR on page {number}: {exc}")

        unique = list(dict.fromkeys(all_schemes))
        print("\n" + "=" * 70)
        print(f"TOTAL UNIQUE SCHEMES FOUND: {len(unique)}")
        print("=" * 70)
        for n, title in enumerate(unique, 1):
            print(f"{n:02d}. {title}")

        input("\nPress Enter to close the browser...")
        browser.close()


if __name__ == "__main__":
    main()
