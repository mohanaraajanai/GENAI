"""
test_scraper.py

Basic automated tests for the scraper helper functions.

These tests don't need to open Vikaspedia.

This is important because unit tests should ideally be:
    - fast
    - predictable
    - independent from external websites
"""

from scraper.vikaspedia import (
    is_valid_http_url,
    make_absolute_url,
    looks_like_pdf_link,
)

from scraper.downloader import (
    clean_filename,
)


# ============================================================
# URL VALIDATION TESTS
# ============================================================

def test_valid_http_url():

    assert is_valid_http_url(
        "https://example.com"
    )


def test_valid_http_url_with_path():

    assert is_valid_http_url(
        "https://example.com/page/test"
    )


def test_invalid_url():

    assert not is_valid_http_url(
        "not-a-url"
    )


def test_invalid_ftp_url():

    assert not is_valid_http_url(
        "ftp://example.com/file.pdf"
    )


# ============================================================
# URL CONVERSION TESTS
# ============================================================

def test_make_absolute_url():

    result = make_absolute_url(
        "https://example.com/page",
        "/documents/test.pdf",
    )

    assert result == (
        "https://example.com/documents/test.pdf"
    )


def test_absolute_url_remains_same():

    result = make_absolute_url(
        "https://example.com/page",
        "https://example.com/test.pdf",
    )

    assert result == (
        "https://example.com/test.pdf"
    )


# ============================================================
# PDF DETECTION TESTS
# ============================================================

def test_pdf_url_detected():

    assert looks_like_pdf_link(
        "Scheme",
        "https://example.com/file.pdf",
    )


def test_pdf_text_detected():

    assert looks_like_pdf_link(
        "Download PDF",
        "https://example.com/document",
    )


def test_download_text_detected():

    assert looks_like_pdf_link(
        "Download",
        "https://example.com/document",
    )


def test_normal_page_not_detected():

    assert not looks_like_pdf_link(
        "Home",
        "https://example.com/about",
    )


# ============================================================
# FILENAME TESTS
# ============================================================

def test_filename_removes_invalid_characters():

    result = clean_filename(
        'PM-KISAN: "Guidelines"/2026'
    )

    assert ":" not in result
    assert '"' not in result
    assert "/" not in result


def test_filename_keeps_normal_text():

    result = clean_filename(
        "PM KISAN Guidelines"
    )

    assert result == (
        "PM KISAN Guidelines"
    )