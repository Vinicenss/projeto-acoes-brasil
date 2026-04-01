import re
from playwright.sync_api import Page, expect


class DashboardPage:
    """Page Object para o dashboard Telecom Brasil."""

    TABS = {
        "precos": "📊 Preços",
        "tecnica": "📈 Análise Técnica",
        "retorno": "💹 Retorno Acumulado",
        "relatorio": "📋 Relatório",
    }

    COMPANIES = ["Vivo", "TIM", "Oi"]

    PERIOD_SHORTCUTS = ["1M", "3M", "6M", "YTD", "1A", "2A"]

    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url

    # ── Navegação ────────────────────────────────────────────────────────────

    def goto(self):
        self.page.goto(self.base_url)
        self.wait_for_app_ready()

    def wait_for_app_ready(self):
        """Aguarda o dashboard carregar completamente (status bar visível)."""
        self.page.wait_for_selector(".status-bar", timeout=30_000)

    def wait_for_rerun(self):
        """Aguarda o Streamlit terminar de re-executar após uma interação.

        Usa timeout fixo: o Streamlit não expõe um indicador de rerun estável
        em todas as versões. 4s é suficiente para reruns com fetch de dados.
        """
        self.page.wait_for_timeout(4_000)

    def click_tab(self, name: str):
        self.page.get_by_role("tab", name=name).click()
        self.page.wait_for_timeout(1_000)

    def get_active_tab_name(self) -> str:
        return self.page.locator('[role="tab"][aria-selected="true"]').inner_text()

    # ── Sidebar — atalhos de período ─────────────────────────────────────────

    def click_period_shortcut(self, label: str):
        self.page.get_by_role("button", name=re.compile(rf"^{label}$")).first.click()
        self.wait_for_rerun()

    # ── Sidebar — filtros de data ─────────────────────────────────────────────

    def get_date_inicio(self) -> str:
        return self.page.get_by_label("Data de início").input_value()

    def get_date_fim(self) -> str:
        return self.page.get_by_label("Data de fim").input_value()

    def set_date_inicio(self, value: str):
        """value no formato YYYY/MM/DD."""
        field = self.page.get_by_label("Data de início")
        field.click()
        field.fill(value)
        field.press("Enter")
        self.wait_for_rerun()

    def set_date_fim(self, value: str):
        field = self.page.get_by_label("Data de fim")
        field.click()
        field.fill(value)
        field.press("Enter")
        self.wait_for_rerun()

    # ── Sidebar — operadoras ──────────────────────────────────────────────────

    def is_company_checked(self, name: str) -> bool:
        return self.page.get_by_label(name).is_checked()

    def toggle_company(self, name: str):
        self.page.get_by_label(name).click()
        self.page.wait_for_timeout(3_000)

    def uncheck_all_companies(self):
        for company in self.COMPANIES:
            if self.is_company_checked(company):
                self.toggle_company(company)

    def check_only(self, name: str):
        for company in self.COMPANIES:
            checked = self.is_company_checked(company)
            if company == name and not checked:
                self.toggle_company(company)
            elif company != name and checked:
                self.toggle_company(company)

    # ── Status bar ───────────────────────────────────────────────────────────

    def get_status_bar_text(self) -> str:
        return self.page.locator(".status-bar").inner_text()

    def get_pregoes_count(self) -> int:
        text = self.get_status_bar_text()
        match = re.search(r"(\d+)\s+pregões", text)
        return int(match.group(1)) if match else 0

    def get_operator_count(self) -> int:
        text = self.get_status_bar_text()
        match = re.search(r"(\d+)\s+operadora", text)
        return int(match.group(1)) if match else 0

    # ── KPI cards ────────────────────────────────────────────────────────────

    def get_kpi_cards(self):
        return self.page.locator(".kpi-card").all()

    def get_kpi_card_count(self) -> int:
        return self.page.locator(".kpi-card").count()

    def kpi_card_has_medal(self, medal: str) -> bool:
        return self.page.locator(f'.kpi-rank:has-text("{medal}")').count() > 0

    # ── Aba Análise Técnica ───────────────────────────────────────────────────

    def is_ma_toggle_checked(self) -> bool:
        return self.page.get_by_label("Exibir Média Móvel").is_checked()

    def click_ma_toggle(self):
        self.page.get_by_label("Exibir Média Móvel").click()
        self.page.wait_for_timeout(1_000)

    def is_ma_slider_visible(self) -> bool:
        return self.page.get_by_text("Período da Média Móvel (dias)").is_visible()

    def set_ma_period(self, value: int):
        """Define o período da MA via teclado (posição relativa ao valor atual)."""
        slider = self.page.locator('[data-testid="stSlider"] input[type="range"]')
        slider.click()
        current = int(slider.input_value())
        diff = value - current
        key = "ArrowRight" if diff > 0 else "ArrowLeft"
        for _ in range(abs(diff)):
            slider.press(key)
        self.page.wait_for_timeout(500)

    def get_ma_period_value(self) -> int:
        slider = self.page.locator('[data-testid="stSlider"] input[type="range"]')
        return int(slider.input_value())

    # ── Aba Relatório — export ────────────────────────────────────────────────

    def is_export_button_visible(self) -> bool:
        return self.page.get_by_role(
            "button", name=re.compile("Exportar métricas")
        ).is_visible()

    def click_export_csv(self):
        return self.page.get_by_role(
            "button", name=re.compile("Exportar métricas")
        )

    # ── Expanders ────────────────────────────────────────────────────────────

    def is_expander_visible(self, partial_text: str) -> bool:
        return self.page.locator(f"summary:has-text('{partial_text}')").count() > 0

    def is_expander_open(self, partial_text: str) -> bool:
        details = self.page.locator(
            f"details:has(summary:has-text('{partial_text}'))"
        )
        return details.get_attribute("open") is not None

    def toggle_expander(self, partial_text: str):
        self.page.locator(f"summary:has-text('{partial_text}')").click()
        self.page.wait_for_timeout(400)

    # ── Alertas e mensagens ───────────────────────────────────────────────────

    def has_warning(self, text: str) -> bool:
        return self.page.locator(f'[data-testid="stAlert"]:has-text("{text}")').count() > 0

    def has_error(self, text: str) -> bool:
        return self.page.locator(f'[data-testid="stAlert"]:has-text("{text}")').count() > 0

    def has_chart(self) -> bool:
        return self.page.locator(".js-plotly-plot").count() > 0
