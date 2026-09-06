from playwright.sync_api import sync_playwright


URL = (
    "https://schemes.vikaspedia.in/viewcontent/"
    "schemesall/schemes-for-farmers?lgn=en"
)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    print("Opening MAIN page...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    print("\nCURRENT URL:")
    print(page.url)

    print("\nPAGE TITLE:")
    print(page.title())

    # ========================================================
    # Find all matching scheme title elements
    # ========================================================

    title = "Pradhan Mantri Kisan Samman Nidhi"

    matches = page.get_by_text(
        title,
        exact=False
    )

    print("\n========================================")
    print("MATCHES")
    print("========================================")

    print(
        "Number of matching elements:",
        matches.count()
    )

    for i in range(matches.count()):

        element = matches.nth(i)

        print(
            f"\n========== MATCH {i} =========="
        )

        try:

            print(
                "Visible:",
                element.is_visible()
            )

            print(
                "Tag:",
                element.evaluate(
                    "el => el.tagName"
                )
            )

            print(
                "Text:",
                element.inner_text()
            )

            print(
                "\nHTML:"
            )

            html = element.evaluate(
                "el => el.outerHTML"
            )

            print(
                html[:3000]
            )

            print(
                "\nPARENT:"
            )

            parent = element.evaluate(
                "el => el.parentElement.outerHTML"
            )

            print(
                parent[:5000]
            )

        except Exception as e:

            print(
                "ERROR:",
                e
            )

    input(
        "\nPress ENTER to close..."
    )

    browser.close()