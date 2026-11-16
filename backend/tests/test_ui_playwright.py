"""
Playwright End-to-End Tests for CycloneSense Next.js UI via pytest-playwright.
Tests critical scientific pages, dark mode theme tokens, navigation, and model metadata.
"""
import pytest
from playwright.sync_api import Page, expect

# Playwright E2E tests against running or test-instantiated Next.js server (port 3000)
BASE_URL = "http://localhost:3000"


@pytest.mark.playwright
def test_home_dashboard_layout(page: Page):
    try:
        page.goto(f"{BASE_URL}/", timeout=10000)
    except Exception:
        pytest.skip("Next.js web server is not running on localhost:3000")

    expect(page).to_have_title(r".*CycloneSense.*")
    # Verify dark theme
    html = page.locator("html")
    expect(html).to_have_class(r".*dark.*")


@pytest.mark.playwright
def test_models_operational_baselines_page(page: Page):
    try:
        page.goto(f"{BASE_URL}/models", timeout=10000)
    except Exception:
        pytest.skip("Next.js web server is not running on localhost:3000")

    heading = page.get_by_role("heading", name=r".*Model Registry.*")
    expect(heading).to_be_visible()
    content = page.text_content("body")
    assert any(term in content for term in ["CLIPER", "Persistence", "Climatology", "Baseline"])


@pytest.mark.playwright
def test_impact_intelligence_page(page: Page):
    try:
        page.goto(f"{BASE_URL}/impact", timeout=10000)
    except Exception:
        pytest.skip("Next.js web server is not running on localhost:3000")

    heading = page.get_by_role("heading", name=r".*Impact Intelligence.*")
    expect(heading).to_be_visible()
    content = page.text_content("body")
    assert any(term in content for term in ["Sentinel", "Optical", "SAR", "Change"])


@pytest.mark.playwright
def test_explainability_gradcam_page(page: Page):
    try:
        page.goto(f"{BASE_URL}/explainability", timeout=10000)
    except Exception:
        pytest.skip("Next.js web server is not running on localhost:3000")

    heading = page.get_by_role("heading", name=r".*Explainability.*")
    expect(heading).to_be_visible()
