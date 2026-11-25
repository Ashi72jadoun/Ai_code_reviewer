import os
import subprocess
import tempfile
from pathlib import Path

import streamlit as st
from llm_reviewer import generate_code_review


st.set_page_config(
    page_title="AURA REview",
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize session state
if "aura_theme" not in st.session_state:
    st.session_state.aura_theme = "Light Mode"

if "repo_path" not in st.session_state:
    st.session_state.repo_path = "../sample-target-repo"

if "repo_path_edited" not in st.session_state:
    st.session_state.repo_path_edited = False

if "review_source" not in st.session_state:
    st.session_state.review_source = "Local repository"

# Keep the review and any error across Streamlit reruns, including theme changes.
if "review_result" not in st.session_state:
    st.session_state.review_result = None

if "review_error" not in st.session_state:
    st.session_state.review_error = None


SUPPORTED_UPLOAD_TYPES = [
    "py", "js", "jsx", "ts", "tsx", "java", "go", "rs",
    "c", "h", "cpp", "hpp", "cs", "php", "rb", "swift",
    "kt", "scala", "sh", "sql", "html", "css", "json",
    "xml", "yaml", "yml", "toml", "md", "txt",
]


def mark_repo_path_edited():
    """Show the clear button after the repository path is changed."""
    st.session_state.repo_path_edited = True


def clear_repo_path():
    """Clear the repository path and hide the clear button."""
    st.session_state.repo_path = ""
    st.session_state.repo_path_edited = False


def create_uploaded_repository(uploaded_files, repo_dir):
    """
    Create a temporary Git repository for uploaded files.

    Empty files are committed as a baseline, then the uploaded contents
    are written as uncommitted changes for the existing review function.
    """
    files_to_write = []
    used_names = set()

    for uploaded_file in uploaded_files:
        name = uploaded_file.name.replace("\\", "/").rsplit("/", 1)[-1]
        name = name.replace("\x00", "").strip()

        if name in ("", ".", ".."):
            name = "uploaded_file"

        original = Path(name)
        stem = original.stem or "uploaded_file"
        suffix = original.suffix
        candidate = name
        counter = 2

        while candidate.casefold() in used_names:
            candidate = f"{stem}_{counter}{suffix}"
            counter += 1

        used_names.add(candidate.casefold())
        files_to_write.append(
            (repo_dir / candidate, uploaded_file.getvalue())
        )

    if not files_to_write:
        raise ValueError("Select at least one source file to upload.")

    for file_path, _ in files_to_write:
        file_path.write_bytes(b"")

    def run_git(*args):
        result = subprocess.run(
            ["git", *args],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            message = result.stderr.strip() or result.stdout.strip()
            raise RuntimeError(message or "A Git command failed.")

    run_git("init")
    run_git("config", "user.name", "AURA REview")
    run_git("config", "user.email", "aura-review@localhost")
    run_git("config", "commit.gpgsign", "false")
    run_git("add", "--all", "--force")
    run_git("commit", "--quiet", "-m", "Uploaded files baseline")

    # Leave uploaded changes unstaged so a standard `git diff` can see them.
    for file_path, contents in files_to_write:
        file_path.write_bytes(contents)


def display_review(review_output):
    """Display the review while keeping its existing content unchanged."""
    output = str(review_output or "").strip()

    if not output or "no uncommitted changes found" in output.lower():
        st.info(
            "ℹ️ No uncommitted changes were detected. "
            "Modify code in the repository and run the review again."
        )
        return

    st.success("✅ AURA REview completed!")

    st.markdown(
        """
        <div class="review-banner">
            <div class="review-banner-icon">🧡</div>
            <div>
                <div class="review-banner-kicker">ANALYSIS COMPLETE</div>
                <div class="review-banner-title">
                    Findings &amp; Refactoring Plan
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # The review container is styled independently from code blocks.
    with st.container(key="review_content"):
        st.markdown(output)


# Theme colors
if st.session_state.aura_theme == "Dark Mode":
    theme_values = {
        "__APP_BG__": (
            "radial-gradient(circle at 85% 8%, rgba(249, 115, 22, 0.16), transparent 34%), "
            "radial-gradient(circle at 12% 75%, rgba(251, 146, 60, 0.10), transparent 38%), "
            "linear-gradient(135deg, #191511 0%, #211a14 55%, #17130f 100%)"
        ),
        "__SIDEBAR_BG__": (
            "linear-gradient(180deg, #211a14 0%, #191511 100%)"
        ),
        "__TEXT__": "#fff7ed",
        "__MUTED__": "#c5b5a5",
        "__PANEL__": "rgba(43, 33, 25, 0.88)",
        "__INPUT__": "rgba(29, 23, 18, 0.96)",
        "__BORDER__": "rgba(251, 146, 60, 0.28)",
        "__CODE_BG__": "#1b1713",
        "__STRONG__": "#fdba74",
        "__DROPZONE__": "rgba(249, 115, 22, 0.08)",
        "__REVIEW_BG__": (
            "linear-gradient(135deg, "
            "rgba(55, 37, 25, 0.96), "
            "rgba(37, 29, 22, 0.96))"
        ),
    }
else:
    theme_values = {
        "__APP_BG__": (
            "radial-gradient(circle at 86% 8%, rgba(251, 146, 60, 0.16), transparent 34%), "
            "radial-gradient(circle at 12% 78%, rgba(253, 186, 116, 0.20), transparent 38%), "
            "linear-gradient(135deg, #fffaf4 0%, #fff1e2 52%, #fff8f0 100%)"
        ),
        "__SIDEBAR_BG__": (
            "linear-gradient(180deg, #fff3e6 0%, #fffaf5 100%)"
        ),
        "__TEXT__": "#332317",
        "__MUTED__": "#78685b",
        "__PANEL__": "rgba(255, 255, 255, 0.88)",
        "__INPUT__": "#ffffff",
        "__BORDER__": "rgba(194, 65, 12, 0.18)",
        "__CODE_BG__": "#fff8f1",
        "__STRONG__": "#b93808",
        "__DROPZONE__": "rgba(251, 146, 60, 0.08)",
        "__REVIEW_BG__": (
            "linear-gradient(135deg, "
            "#fff1df 0%, "
            "#fffaf3 54%, "
            "#fff2e3 100%)"
        ),
    }


css = """
<style>
    :root {
        --app-bg: __APP_BG__;
        --sidebar-bg: __SIDEBAR_BG__;
        --text-color: __TEXT__;
        --muted-color: __MUTED__;
        --panel-bg: __PANEL__;
        --input-bg: __INPUT__;
        --border-color: __BORDER__;
        --code-bg: __CODE_BG__;
        --strong-color: __STRONG__;
        --dropzone-bg: __DROPZONE__;
        --review-bg: __REVIEW_BG__;
        --accent: #c2410c;
        --accent-bright: #f97316;
        --peach: #fdba74;
    }

    .stApp {
        background: var(--app-bg);
        color: var(--text-color);
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }

    .main .block-container {
        max-width: 1380px;
        padding-top: 1rem;
        padding-bottom: 2.5rem;
    }

    section[data-testid="stSidebar"] {
        background: var(--sidebar-bg) !important;
        border-right: 1px solid var(--border-color);
    }

    section[data-testid="stSidebar"] > div {
        background: transparent;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--text-color);
    }

    section[data-testid="stSidebar"] hr {
        border-color: var(--border-color);
    }

    .brand-mark {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 54px;
        height: 54px;
        margin: 0.2rem 0 0.5rem;
        border-radius: 17px;
        background: linear-gradient(135deg, #fed7aa, #fb923c);
        box-shadow: 0 8px 20px rgba(194, 65, 12, 0.16);
        font-size: 1.8rem;
    }

    .hero-shell {
        position: relative;
        overflow: hidden;
        margin: 0.4rem 0 1.4rem;
        padding: 2.7rem 2rem;
        border: 1px solid var(--border-color);
        border-radius: 26px;
        background:
            linear-gradient(
                135deg,
                var(--panel-bg),
                rgba(253, 186, 116, 0.14)
            );
        box-shadow: 0 14px 36px rgba(100, 55, 20, 0.08);
        text-align: center;
    }

    .hero-shell::before {
        content: "";
        position: absolute;
        top: -100px;
        right: -75px;
        width: 280px;
        height: 280px;
        border-radius: 50%;
        background:
            radial-gradient(
                circle,
                rgba(251, 146, 60, 0.22),
                transparent 70%
            );
        pointer-events: none;
    }

    .hero-kicker {
        display: inline-block;
        margin-bottom: 0.85rem;
        padding: 0.42rem 0.85rem;
        border: 1px solid rgba(194, 65, 12, 0.20);
        border-radius: 999px;
        background: rgba(255, 237, 213, 0.76);
        color: #9a3412;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.09em;
    }

    .hero-title {
        margin: 0;
        background: linear-gradient(
            100deg,
            #9a3412 0%,
            #ea580c 55%,
            #fb923c 100%
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: clamp(2.5rem, 5vw, 3.8rem);
        font-weight: 850;
        letter-spacing: -0.045em;
        line-height: 1.1;
    }

    .hero-subtitle {
        max-width: 760px;
        margin: 0.9rem auto 0;
        color: var(--muted-color);
        font-size: 1.08rem;
        line-height: 1.7;
    }

    .metric-card {
        position: relative;
        overflow: hidden;
        min-height: 140px;
        padding: 1.15rem 1rem;
        border: 1px solid var(--border-color);
        border-radius: 18px;
        background: var(--panel-bg);
        box-shadow: 0 8px 22px rgba(100, 55, 20, 0.07);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .metric-card::before {
        content: "";
        position: absolute;
        inset: 0 0 auto;
        height: 4px;
        background: linear-gradient(
            90deg,
            #c2410c,
            #f97316,
            #fdba74
        );
    }

    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(194, 65, 12, 0.13);
    }

    .metric-icon {
        margin-bottom: 0.25rem;
        font-size: 1.45rem;
    }

    .metric-value {
        color: var(--strong-color);
        font-size: 1.7rem;
        font-weight: 850;
    }

    .metric-label {
        margin-top: 0.15rem;
        color: var(--muted-color);
        font-size: 0.9rem;
    }

    .action-panel {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin: 1.5rem 0 0.6rem;
        padding: 1rem 1.2rem;
        border: 1px solid var(--border-color);
        border-radius: 16px;
        background: linear-gradient(
            100deg,
            var(--panel-bg),
            rgba(253, 186, 116, 0.15)
        );
    }

    .action-icon {
        display: flex;
        flex: 0 0 48px;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 15px;
        background: linear-gradient(135deg, #fed7aa, #fb923c);
        font-size: 1.45rem;
    }

    .action-title {
        color: var(--text-color);
        font-size: 1.12rem;
        font-weight: 800;
    }

    .action-copy {
        color: var(--muted-color);
        font-size: 0.92rem;
    }

    /* High-contrast buttons */
    [data-testid="stButton"] button,
    .stButton button {
        min-height: 2.8rem;
        border: 1px solid #b93808 !important;
        border-radius: 12px !important;
        background: linear-gradient(
            100deg,
            #b93808 0%,
            #c2410c 100%
        ) !important;
        box-shadow: 0 7px 18px rgba(194, 65, 12, 0.22) !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 800 !important;
        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease !important;
    }

    [data-testid="stButton"] button:hover,
    .stButton button:hover {
        transform: translateY(-2px);
        background: linear-gradient(
            100deg,
            #9a3412 0%,
            #c2410c 100%
        ) !important;
        box-shadow: 0 10px 23px rgba(194, 65, 12, 0.30) !important;
        color: #ffffff !important;
    }

    [data-testid="stButton"] button p,
    [data-testid="stButton"] button span,
    .stButton button p,
    .stButton button span {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Theme toggle */
    [class*="st-key-theme_toggle"] button {
        width: 2.8rem !important;
        min-height: 2.8rem !important;
        padding: 0 !important;
        border: 1px solid var(--border-color) !important;
        background: var(--panel-bg) !important;
        box-shadow: 0 4px 12px rgba(100, 55, 20, 0.08) !important;
        color: var(--accent) !important;
    }

    [class*="st-key-theme_toggle"] button p,
    [class*="st-key-theme_toggle"] button span {
        color: var(--accent) !important;
    }

    /* Clear icon appears only after the repository path is edited */
    [class*="st-key-clear_repo_path"] button {
        width: 100% !important;
        min-height: 2.55rem !important;
        padding: 0 !important;
        border: 1px solid rgba(194, 65, 12, 0.22) !important;
        background: #ffedd5 !important;
        box-shadow: none !important;
        color: #9a3412 !important;
        font-size: 1.45rem !important;
    }

    [class*="st-key-clear_repo_path"] button p,
    [class*="st-key-clear_repo_path"] button span {
        color: #9a3412 !important;
    }

    [data-testid="stTextInput"] input {
        min-height: 2.65rem;
        border: 1px solid var(--border-color) !important;
        border-radius: 10px !important;
        background: var(--input-bg) !important;
        color: var(--text-color) !important;
    }

    [data-testid="stTextInput"] input:focus {
        border-color: #f97316 !important;
        box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.18) !important;
    }

    [data-testid="stRadio"] input {
        accent-color: #c2410c;
    }

    [data-testid="stFileUploaderDropzone"] {
        border: 1px dashed rgba(194, 65, 12, 0.42) !important;
        border-radius: 14px !important;
        background: var(--dropzone-bg) !important;
    }

    [data-testid="stFileUploader"] p {
        color: var(--muted-color) !important;
    }

    [data-testid="stFileUploader"] button {
        border: 1px solid rgba(194, 65, 12, 0.24) !important;
        border-radius: 9px !important;
        background: #ffedd5 !important;
        color: #9a3412 !important;
    }

    [data-testid="stFileUploader"] button p,
    [data-testid="stFileUploader"] button span {
        color: #9a3412 !important;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--muted-color);
    }

    /* General review heading styling */
    .main [data-testid="stMarkdownContainer"] h1,
    .main [data-testid="stMarkdownContainer"] h2,
    .main [data-testid="stMarkdownContainer"] h3,
    .main [data-testid="stMarkdownContainer"] h4 {
        color: var(--text-color);
        font-weight: 800;
    }

    .main [data-testid="stMarkdownContainer"] h2 {
        margin-top: 1.4rem;
        padding: 0.65rem 0.9rem;
        border-left: 4px solid #f97316;
        border-radius: 0 12px 12px 0;
        background: linear-gradient(
            90deg,
            rgba(251, 146, 60, 0.18),
            rgba(253, 186, 116, 0.10),
            transparent
        );
    }

    .main [data-testid="stMarkdownContainer"] h3 {
        margin-top: 1.1rem;
        padding: 0.4rem 0.75rem;
        border-left: 3px solid #fb923c;
        border-radius: 0 9px 9px 0;
        background: linear-gradient(
            90deg,
            rgba(251, 146, 60, 0.12),
            transparent
        );
    }

    .main [data-testid="stMarkdownContainer"] strong {
        color: var(--strong-color);
    }

    .main [data-testid="stMarkdownContainer"] li {
        margin: 0.3rem 0;
        padding-left: 0.15rem;
        line-height: 1.65;
    }

    .main [data-testid="stMarkdownContainer"] li::marker {
        color: #f97316;
    }

    .main [data-testid="stMarkdownContainer"] :not(pre) > code {
        padding: 0.14rem 0.38rem;
        border: 1px solid rgba(194, 65, 12, 0.13);
        border-radius: 6px;
        background: rgba(251, 146, 60, 0.12);
        color: var(--strong-color);
        font-size: 0.9em;
    }

    /* Existing code-block styling, intentionally unchanged */
    .main [data-testid="stMarkdownContainer"] pre {
        overflow-x: auto;
        margin: 0.8rem 0 1.2rem;
        padding: 1rem 1.2rem !important;
        border: 1px solid var(--border-color) !important;
        border-left: 4px solid #f97316 !important;
        border-radius: 13px !important;
        background: var(--code-bg) !important;
        box-shadow: 0 7px 20px rgba(100, 55, 20, 0.08);
    }

    .review-banner {
        display: flex;
        align-items: center;
        gap: 0.9rem;
        margin: 1.25rem 0;
        padding: 1rem 1.15rem;
        border: 1px solid var(--border-color);
        border-radius: 16px;
        background: linear-gradient(
            100deg,
            rgba(251, 146, 60, 0.17),
            rgba(253, 186, 116, 0.10)
        );
    }

    .review-banner-icon {
        font-size: 1.8rem;
    }

    .review-banner-kicker {
        color: var(--strong-color);
        font-size: 0.74rem;
        font-weight: 850;
        letter-spacing: 0.1em;
    }

    .review-banner-title {
        color: var(--text-color);
        font-size: 1.15rem;
        font-weight: 850;
    }

    /* Review panel and text styles; code blocks are left unchanged */
    [class*="st-key-review_content"] {
        margin-top: 0.9rem;
        padding: clamp(1rem, 2vw, 1.7rem);
        border: 1px solid var(--border-color);
        border-radius: 18px;
        background: var(--review-bg);
        box-shadow: 0 8px 24px rgba(100, 55, 20, 0.07);
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] p,
    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] li,
    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] blockquote,
    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] td {
        color: var(--text-color) !important;
        font-size: clamp(1.1rem, 1.2vw, 1.22rem) !important;
        line-height: 1.8 !important;
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] li {
        margin: 0.45rem 0;
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] strong {
        color: var(--strong-color) !important;
        font-weight: 800;
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] h1,
    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] h2,
    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] h3,
    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] h4 {
        color: var(--text-color) !important;
        font-weight: 800;
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] h1 {
        font-size: 1.8rem !important;
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] h2 {
        margin: 1.5rem 0 0.8rem;
        padding: 0.7rem 0.95rem;
        border-left: 5px solid #f97316;
        border-radius: 0 12px 12px 0;
        background: linear-gradient(
            90deg,
            rgba(251, 146, 60, 0.20),
            rgba(253, 186, 116, 0.08),
            transparent
        );
        color: var(--strong-color) !important;
        font-size: 1.6rem !important;
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] h3 {
        margin: 1.2rem 0 0.6rem;
        padding: 0.45rem 0.75rem;
        border-left: 3px solid #fb923c;
        border-radius: 0 9px 9px 0;
        background: rgba(251, 146, 60, 0.08);
        color: var(--text-color) !important;
        font-size: 1.32rem !important;
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] h4 {
        font-size: 1.15rem !important;
    }

    /* Warm peach highlights for inline code such as filenames and locations */
    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"]
    :not(pre) > code {
        padding: 0.18rem 0.45rem;
        border: 1px solid rgba(194, 65, 12, 0.18);
        border-radius: 6px;
        background: rgba(251, 146, 60, 0.16) !important;
        color: var(--strong-color) !important;
        font-size: 0.95em !important;
        font-weight: 600;
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] blockquote {
        padding: 0.8rem 1rem;
        border-left: 4px solid #fb923c;
        border-radius: 0 12px 12px 0;
        background: rgba(251, 146, 60, 0.08);
    }

    [class*="st-key-review_content"]
    [data-testid="stMarkdownContainer"] hr {
        border-color: var(--border-color);
    }

    /* Centered footer */
    .aura-footer {
        width: 100%;
        margin-top: 3rem;
        padding: 1.15rem 0 1.5rem;
        border-top: 1px solid var(--border-color);
        color: var(--muted-color);
        text-align: center;
        font-size: 0.95rem;
        line-height: 1.6;
    }

    .aura-footer .footer-brand {
        color: var(--strong-color);
        font-weight: 800;
    }

    @media (max-width: 700px) {
        .hero-shell {
            padding: 2rem 1rem;
        }

        .hero-subtitle {
            font-size: 0.98rem;
        }
    }
</style>
"""

for token, value in theme_values.items():
    css = css.replace(token, value)

st.markdown(css, unsafe_allow_html=True)


# Sidebar controls
with st.sidebar:
    st.markdown(
        '<div class="brand-mark">⚡</div>',
        unsafe_allow_html=True,
    )
    st.title("AURA REview")
    st.markdown("---")

    st.markdown("### ⚡ AURA Features")
    st.markdown("- 🔍 **Git Diff Extraction**")
    st.markdown("- 🛡️ **Bandit Security Audit**")
    st.markdown("- 🎨 **Ruff Linter Checks**")
    st.markdown("- 🤖 **Context-Aware AI Review**")

    st.markdown("---")
    st.markdown("### Review Source")

    review_source = st.radio(
        "Choose what to analyze",
        ["Local repository", "Uploaded files"],
        key="review_source",
        label_visibility="collapsed",
    )

    st.markdown("**Repository path**")

    show_clear_button = bool(
        st.session_state.repo_path_edited
        and st.session_state.repo_path.strip()
    )

    if show_clear_button:
        path_col, clear_col = st.columns([0.84, 0.16])
    else:
        path_col = st.container()
        clear_col = None

    with path_col:
        repo_path = st.text_input(
            "Repository path",
            key="repo_path",
            placeholder="../sample-target-repo",
            label_visibility="collapsed",
            on_change=mark_repo_path_edited,
        )

    if clear_col is not None:
        with clear_col:
            st.button(
                "×",
                key="clear_repo_path",
                type="secondary",
                on_click=clear_repo_path,
                use_container_width=True,
            )

    st.markdown("**Upload source files**")
    uploaded_files = st.file_uploader(
        "Select one or more code files",
        type=SUPPORTED_UPLOAD_TYPES,
        accept_multiple_files=True,
        key="uploaded_sources",
    )

    st.caption(
        "Choose “Uploaded files” above to review the selected files."
    )

    st.markdown("---")
    st.success("System Status: Ready 🟢")


# Theme toggle
header_spacer, theme_column = st.columns([0.90, 0.10])

with theme_column:
    theme_icon = (
        "🌙"
        if st.session_state.aura_theme == "Light Mode"
        else "☀️"
    )

    if st.button(
        theme_icon,
        key="theme_toggle",
        type="secondary",
    ):
        st.session_state.aura_theme = (
            "Dark Mode"
            if st.session_state.aura_theme == "Light Mode"
            else "Light Mode"
        )
        st.rerun()


# Hero section
st.markdown(
    """
    <div class="hero-shell">
        <div class="hero-kicker">AI-POWERED CODE REVIEW</div>
        <div class="hero-title">AURA REview</div>
        <div class="hero-subtitle">
            Find bugs, security issues, and code-quality improvements with
            contextual AI feedback, Bandit security scans, and Ruff checks.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Summary cards
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-icon">🧠</div>
            <div class="metric-value">100%</div>
            <div class="metric-label">Context-Aware Analysis</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-icon">🛡️</div>
            <div class="metric-value">Real-Time</div>
            <div class="metric-label">Security &amp; Bug Detection</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="metric-card">
            <div class="metric-icon">⚡</div>
            <div class="metric-value">Zero</div>
            <div class="metric-label">Manual Setup Required</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Analyze panel
st.markdown(
    """
    <div class="action-panel">
        <div class="action-icon">🚀</div>
        <div>
            <div class="action-title">Ready to review?</div>
            <div class="action-copy">
                Choose a repository or upload source files in the sidebar,
                then start your AURA analysis.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if review_source == "Uploaded files":
    if uploaded_files:
        st.caption(f"{len(uploaded_files)} file(s) selected for review.")
    else:
        st.caption(
            "Upload one or more source files in the sidebar to begin."
        )


# Start a new review
analyze_clicked = st.button(
    "🚀 Analyze Code with AURA REview",
    key="analyze_code",
    type="primary",
    use_container_width=True,
)

if analyze_clicked:
    # Clear old output only when a new analysis is requested.
    st.session_state.review_result = None
    st.session_state.review_error = None

    try:
        if review_source == "Local repository":
            target_path = repo_path.strip()

            if not target_path:
                st.session_state.review_error = (
                    "Enter a repository path in the sidebar."
                )
            elif not os.path.isdir(target_path):
                st.session_state.review_error = (
                    f"❌ Repository folder not found: `{target_path}`"
                )
            else:
                with st.spinner(
                    "🔍 AURA is analyzing your repository..."
                ):
                    review_output = generate_code_review(target_path)

                # Store the result so it survives theme-toggle reruns.
                st.session_state.review_result = str(review_output or "")

        else:
            if not uploaded_files:
                st.session_state.review_error = (
                    "Upload at least one source file in the sidebar."
                )
            else:
                with st.spinner(
                    "🔍 Preparing uploaded files and running the AURA review..."
                ):
                    with tempfile.TemporaryDirectory(
                        prefix="aura-review-"
                    ) as temp_dir:
                        temporary_repo = Path(temp_dir)
                        create_uploaded_repository(
                            uploaded_files,
                            temporary_repo,
                        )
                        review_output = generate_code_review(temp_dir)

                # Store the result so it survives theme-toggle reruns.
                st.session_state.review_result = str(review_output or "")

    except Exception as error:
        st.session_state.review_error = f"❌ Review failed: {error}"


# Render the stored result and error on every run.
if st.session_state.review_error:
    st.error(st.session_state.review_error)

if st.session_state.review_result is not None:
    display_review(st.session_state.review_result)


# Centered footer
st.markdown(
    """
    <div class="aura-footer">
        <span class="footer-brand">AURA REview</span>:
        Engineered with Python, Streamlit, and Groq Cloud &amp; AJ :)
    </div>
    """,
    unsafe_allow_html=True,
)