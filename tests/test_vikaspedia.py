from playwright.sync_api import sync_playwright


URL = (
    "https://schemes.vikaspedia.in/viewcontent/"
    "schemesall/schemes-for-farmers?lgn=en"
)


with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page(
        viewport={
            "width": 1920,
            "height": 1080
        }
    )

    print("Opening page...")

    page.goto(
        URL,
        wait_until="domcontentloaded",
        timeout=60000
    )

    # Allow JavaScript application to render
    page.wait_for_timeout(5000)

    print("\nPAGE TITLE:")
    print(page.title())

    print("\nURL:")
    print(page.url)

    # ========================================================
    # Print body text
    # ========================================================

    print("\n========================================")
    print("BODY TEXT")
    print("========================================")

    body_text = page.locator("body").inner_text()

    print(body_text[:6000])

    # ========================================================
    # Search the complete HTML
    # ========================================================

    print("\n========================================")
    print("SEARCHING HTML FOR SCHEME NAME")
    print("========================================")

    html = page.content()

    search_text = "Pradhan Mantri Kisan"

    position = html.lower().find(
        search_text.lower()
    )

    print(
        "Position in HTML:",
        position
    )

    if position >= 0:

        print("\nHTML AROUND SCHEME NAME:\n")

        start = max(
            0,
            position - 3000
        )

        end = min(
            len(html),
            position + 5000
        )

        print(
            html[start:end]
        )

    else:

        print(
            "Scheme name NOT found in page HTML."
        )

    # ========================================================
    # Find all elements containing partial text
    # using JavaScript directly
    # ========================================================

    print("\n========================================")
    print("JAVASCRIPT DOM SEARCH")
    print("========================================")

    matches = page.evaluate(
        """
        () => {

            const search =
                "Pradhan Mantri Kisan";

            const elements =
                Array.from(
                    document.querySelectorAll("*")
                );

            return elements
                .filter(el => {

                    const text =
                        (el.innerText || "")
                        .trim();

                    return text
                        .toLowerCase()
                        .includes(
                            search.toLowerCase()
                        );

                })
                .slice(0, 20)
                .map(el => ({

                    tag: el.tagName,

                    text:
                        (el.innerText || "")
                        .trim()
                        .substring(0, 500),

                    html:
                        el.outerHTML
                        .substring(0, 2000)

                }));

        }
        """
    )

    print(
        f"DOM matches: {len(matches)}"
    )

    for index, item in enumerate(matches):

        print(
            f"\n========== MATCH {index} =========="
        )

        print(
            "TAG:",
            item["tag"]
        )

        print(
            "TEXT:",
            item["text"]
        )

        print(
            "HTML:"
        )

        print(
            item["html"]
        )

    # ========================================================
    # Save complete HTML
    # ========================================================

    with open(
        "vikaspedia_main.html",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html)

    print(
        "\nComplete HTML saved as:"
        " vikaspedia_main.html"
    )

    # ========================================================
    # Screenshot
    # ========================================================

    page.screenshot(
        path="vikaspedia_main.png",
        full_page=True
    )

    print(
        "Screenshot saved as:"
        " vikaspedia_main.png"
    )

    #input("\nPress ENTER to close..." )#

    browser.close()