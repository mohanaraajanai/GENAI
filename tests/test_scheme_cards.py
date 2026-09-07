from playwright.sync_api import sync_playwright

LISTING_URL = (
    "https://schemes.vikaspedia.in/"
    "viewcontent/schemesall/"
    "schemes-for-farmers?lgn=en"
)

SCHEME_TITLE = "Pradhan Mantri Kisan Samman Nidhi"


with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("Opening Farmer Schemes page...")
    page.goto(LISTING_URL, wait_until="domcontentloaded")

    page.wait_for_timeout(5000)

    print("\nPAGE TITLE:")
    print(page.title())

    print("\nCURRENT URL:")
    print(page.url)

    # ---------------------------------------------------------
    # Find the scheme card using its TITLE attribute.
    # ---------------------------------------------------------
    card = page.locator(
        f'div[title="{SCHEME_TITLE}"]'
    ).first

    print("\nCARD COUNT:")
    print(card.count())

    if card.count() == 0:
        print("❌ Scheme card not found.")

    else:
        print("✅ Scheme card found.")

        print("\nCARD HTML:")
        print(card.evaluate("(el) => el.outerHTML"))

        # Scroll card into view
        card.scroll_into_view_if_needed()

        print("\nClicking scheme card...")

        old_url = page.url

        try:
            card.click(timeout=15000)

            # Give React/Next.js time to navigate
            page.wait_for_timeout(5000)

            print("\nAFTER CLICK")
            print("------------------------------")

            print("PAGE TITLE:")
            print(page.title())

            print("\nCURRENT URL:")
            print(page.url)

            # -------------------------------------------------
            # Verify whether we reached the individual page.
            # -------------------------------------------------
            if page.url != old_url:

                print("\n✅ URL CHANGED")

                if "pradhan-mantri-kisan-samman-nidhi" in page.url.lower():
                    print("✅ SUCCESS!")
                    print("Individual scheme page opened.")

                else:
                    print("⚠️ URL changed, but unexpected scheme URL.")

            else:
                print("\n❌ URL DID NOT CHANGE")
                print("The card may require a different click target.")

        except Exception as e:

            print("\n❌ CLICK FAILED")
            print(type(e).__name__)
            print(str(e))

  #  input("\nPress ENTER to close browser...")#

    browser.close()