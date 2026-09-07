# Live smoke test. Run explicitly with:
# pytest -q tests/test_pagination.py -s

from scraper.vikaspedia import VikaspediaScraper


def test_vikaspedia_pagination_live():
    with VikaspediaScraper(headless=True) as scraper:
        scraper.open_listing_page()
        pages = scraper.get_pagination_numbers()
        assert pages == [1, 2, 3, 4, 5]

        all_titles = []
        for page_number in pages:
            scraper.open_listing_page()
            if page_number != 1:
                scraper.open_pagination_page(page_number)
            titles = scraper.get_scheme_titles()
            assert titles
            all_titles.extend(titles)

        assert len(set(all_titles)) >= 20
