import pytest
from playwright.sync_api import Page
from pages.dashboard import DashboardPage

BASE_URL = "http://localhost:8501"


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "smoke: testes rápidos de sanidade básica"
    )
    config.addinivalue_line(
        "markers", "slow: testes que envolvem carregamento de dados externos"
    )


@pytest.fixture(autouse=True)
def set_default_timeout(page: Page):
    page.set_default_timeout(20_000)


@pytest.fixture
def dashboard(page: Page) -> DashboardPage:
    dp = DashboardPage(page, BASE_URL)
    dp.goto()
    return dp


@pytest.fixture
def dashboard_relatorio(dashboard: DashboardPage) -> DashboardPage:
    """Dashboard já na aba Relatório."""
    dashboard.click_tab("📋 Relatório")
    return dashboard


@pytest.fixture
def dashboard_tecnica(dashboard: DashboardPage) -> DashboardPage:
    """Dashboard já na aba Análise Técnica."""
    dashboard.click_tab("📈 Análise Técnica")
    return dashboard
