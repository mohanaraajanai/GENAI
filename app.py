"""
Streamlit application for downloading Vikaspedia Farmer Scheme PDFs.

Features:
- Enter Vikaspedia URL
- Scan all pagination pages
- Discover individual scheme URLs
- Select schemes using checkboxes
- Download individual PDF
- Download selected PDFs
- Download all PDFs
- Progress bar
- Retry handling
- Error reporting
"""

import os
from pathlib import Path

import streamlit as st

from scraper.vikaspedia import (
    VikaspediaScraper,
    DEFAULT_URL,
)

from scraper.downloader import (
    PDFDownloader,
)


# ===================================================================
# Application configuration
# ===================================================================

st.set_page_config(
    page_title="Vikaspedia Farmer Schemes",
    page_icon="📚",
    layout="wide",
)


# ===================================================================
# Paths
# ===================================================================

BASE_DIR = Path(__file__).resolve().parent

DOWNLOAD_DIR = (
    BASE_DIR / "downloads"
)


DOWNLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ===================================================================
# Session state
# ===================================================================

if "schemes" not in st.session_state:
    st.session_state.schemes = []

if "scan_completed" not in st.session_state:
    st.session_state.scan_completed = False


# ===================================================================
# Header
# ===================================================================

st.title(
    "📚 Vikaspedia Farmer Schemes Downloader"
)

st.markdown(
    """
Download Farmer Scheme PDFs directly from Vikaspedia.

The application:

**Farmer Schemes → Pagination → Scheme → Individual Scheme Page → PDF**
"""
)


# ===================================================================
# URL input
# ===================================================================

st.subheader(
    "1️⃣ Vikaspedia Farmer Schemes URL"
)

url = st.text_input(
    "Enter the Vikaspedia Farmer Schemes page URL",
    value=DEFAULT_URL,
)


# ===================================================================
# Browser option
# ===================================================================

show_browser = st.checkbox(
    "Show browser while scraping",
    value=False,
    help=(
        "Enable this if you want to see Playwright "
        "working in the browser."
    ),
)


# ===================================================================
# Scan schemes
# ===================================================================

st.subheader(
    "2️⃣ Scan Schemes"
)

if st.button(
    "🔎 Scan All Schemes",
    type="primary",
    use_container_width=True,
):

    if not url.strip():

        st.error(
            "Please enter a Vikaspedia URL."
        )

    else:

        progress = st.progress(
            0
        )

        status = st.empty()

        scraper = None

        try:

            status.info(
                "Starting Playwright..."
            )

            progress.progress(
                10
            )

            scraper = VikaspediaScraper(
                headless=not show_browser
            )

            status.info(
                "Opening Farmer Schemes page..."
            )

            progress.progress(
                20
            )

            schemes = scraper.get_all_schemes(
                url.strip()
            )

            progress.progress(
                100
            )

            st.session_state.schemes = schemes
            st.session_state.scan_completed = True

            status.success(
                f"Scan completed. "
                f"{len(schemes)} schemes found."
            )

        except Exception as exc:

            st.session_state.schemes = []
            st.session_state.scan_completed = False

            st.error(
                f"Scanning failed: {exc}"
            )

        finally:

            if scraper:
                scraper.close()


# ===================================================================
# Display results
# ===================================================================

if st.session_state.schemes:

    schemes = st.session_state.schemes

    st.divider()

    st.subheader(
        f"3️⃣ Available Schemes ({len(schemes)})"
    )

    st.info(
        "Select the schemes you want to download."
    )

    # ---------------------------------------------------------------
    # Select all checkbox
    # ---------------------------------------------------------------

    select_all = st.checkbox(
        "☑️ Select All Schemes"
    )

    st.divider()

    # ---------------------------------------------------------------
    # Individual scheme list
    # ---------------------------------------------------------------

    selected_schemes = []

    for index, scheme in enumerate(
        schemes
    ):

        scheme_name = scheme["name"]
        scheme_url = scheme["url"]

        col1, col2 = st.columns(
            [0.75, 0.25]
        )

        with col1:

            selected = st.checkbox(
                scheme_name,
                value=select_all,
                key=f"scheme_{index}",
            )

            if selected:

                selected_schemes.append(
                    scheme
                )

        with col2:

            # Individual download button.
            if st.button(
                "⬇️ Download",
                key=f"download_{index}",
            ):

                status = st.empty()

                downloader = None

                try:

                    status.info(
                        f"Downloading {scheme_name}..."
                    )

                    downloader = PDFDownloader(
                        output_dir=DOWNLOAD_DIR,
                        headless=not show_browser,
                        retries=3,
                    )

                    result = downloader.download(
                        scheme_name=scheme_name,
                        scheme_url=scheme_url,
                    )

                    if result["success"]:

                        status.success(
                            f"Downloaded: "
                            f"{result['path']}"
                        )

                    else:

                        status.error(
                            result["error"]
                        )

                except Exception as exc:

                    status.error(
                        f"Download failed: {exc}"
                    )

                finally:

                    if downloader:
                        downloader.close()


    # =================================================================
    # Bulk download buttons
    # =================================================================

    st.divider()

    st.subheader(
        "4️⃣ Bulk Download"
    )

    col1, col2 = st.columns(2)

    # -----------------------------------------------------------------
    # Download selected
    # -----------------------------------------------------------------

    with col1:

        if st.button(
            "⬇️ Download Selected",
            use_container_width=True,
        ):

            if not selected_schemes:

                st.warning(
                    "Please select at least one scheme."
                )

            else:

                downloader = None

                progress = st.progress(
                    0
                )

                status = st.empty()

                success_count = 0
                failed_count = 0

                try:

                    downloader = PDFDownloader(
                        output_dir=DOWNLOAD_DIR,
                        headless=not show_browser,
                        retries=3,
                    )

                    total = len(
                        selected_schemes
                    )

                    for index, scheme in enumerate(
                        selected_schemes
                    ):

                        status.info(
                            f"Downloading "
                            f"{index + 1}/{total}: "
                            f"{scheme['name']}"
                        )

                        result = downloader.download(
                            scheme_name=scheme["name"],
                            scheme_url=scheme["url"],
                        )

                        if result["success"]:

                            success_count += 1

                        else:

                            failed_count += 1

                            st.error(
                                f"{scheme['name']}: "
                                f"{result['error']}"
                            )

                        progress.progress(
                            int(
                                ((index + 1) / total)
                                * 100
                            )
                        )

                    status.success(
                        f"Completed: "
                        f"{success_count} downloaded, "
                        f"{failed_count} failed."
                    )

                except Exception as exc:

                    st.error(
                        f"Bulk download failed: {exc}"
                    )

                finally:

                    if downloader:
                        downloader.close()

    # -----------------------------------------------------------------
    # Download all
    # -----------------------------------------------------------------

    with col2:

        if st.button(
            "⬇️ Download All",
            use_container_width=True,
        ):

            downloader = None

            progress = st.progress(
                0
            )

            status = st.empty()

            success_count = 0
            failed_count = 0

            try:

                downloader = PDFDownloader(
                    output_dir=DOWNLOAD_DIR,
                    headless=not show_browser,
                    retries=3,
                )

                total = len(
                    schemes
                )

                for index, scheme in enumerate(
                    schemes
                ):

                    status.info(
                        f"Downloading "
                        f"{index + 1}/{total}: "
                        f"{scheme['name']}"
                    )

                    result = downloader.download(
                        scheme_name=scheme["name"],
                        scheme_url=scheme["url"],
                    )

                    if result["success"]:

                        success_count += 1

                    else:

                        failed_count += 1

                        st.error(
                            f"{scheme['name']}: "
                            f"{result['error']}"
                        )

                    progress.progress(
                        int(
                            ((index + 1) / total)
                            * 100
                        )
                    )

                status.success(
                    f"Completed: "
                    f"{success_count} downloaded, "
                    f"{failed_count} failed."
                )

            except Exception as exc:

                st.error(
                    f"Download All failed: {exc}"
                )

            finally:

                if downloader:
                    downloader.close()


# ===================================================================
# Download folder information
# ===================================================================

st.divider()

st.subheader(
    "📁 Download Folder"
)

pdf_files = list(
    DOWNLOAD_DIR.glob("*.pdf")
)

if pdf_files:

    st.success(
        f"{len(pdf_files)} PDF file(s) currently in downloads."
    )

    for pdf in sorted(pdf_files):

        size_kb = (
            pdf.stat().st_size / 1024
        )

        st.write(
            f"📄 {pdf.name} "
            f"({size_kb:.1f} KB)"
        )

else:

    st.info(
        "No PDFs downloaded yet."
    )


# ===================================================================
# Footer
# ===================================================================

st.divider()

st.caption(
    "Vikaspedia Farmer Schemes Downloader • "
    "Playwright + Streamlit"
)