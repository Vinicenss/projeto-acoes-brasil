"""
Testes de navegação entre abas do dashboard.
Cobre: presença das tabs, navegação, conteúdo exclusivo por aba.
"""
import pytest
from playwright.sync_api import expect
from pages.dashboard import DashboardPage


class TestCarregamentoInicial:

    @pytest.mark.smoke
    def test_titulo_principal_visivel(self, dashboard: DashboardPage):
        expect(dashboard.page.get_by_text("Telecom Brasil — Análise de Ações")).to_be_visible()

    @pytest.mark.smoke
    def test_subtitulo_visivel(self, dashboard: DashboardPage):
        expect(dashboard.page.locator(".main-subtitle")).to_contain_text("Yahoo Finance")

    @pytest.mark.smoke
    def test_status_bar_carregada(self, dashboard: DashboardPage):
        texto = dashboard.get_status_bar_text()
        assert "pregões carregados" in texto

    def test_status_bar_exibe_operadoras(self, dashboard: DashboardPage):
        texto = dashboard.get_status_bar_text()
        assert "operadora" in texto

    def test_status_bar_exibe_intervalo_de_datas(self, dashboard: DashboardPage):
        texto = dashboard.get_status_bar_text()
        assert "/" in texto  # formato dd/mm/yyyy


class TestAbas:

    @pytest.mark.smoke
    def test_quatro_tabs_presentes(self, dashboard: DashboardPage):
        for nome in DashboardPage.TABS.values():
            expect(dashboard.page.get_by_role("tab", name=nome)).to_be_visible()

    @pytest.mark.smoke
    def test_tab_precos_ativa_por_padrao(self, dashboard: DashboardPage):
        assert "Preços" in dashboard.get_active_tab_name()

    def test_navegar_para_analise_tecnica(self, dashboard: DashboardPage):
        dashboard.click_tab("📈 Análise Técnica")
        assert "Análise Técnica" in dashboard.get_active_tab_name()

    def test_navegar_para_retorno_acumulado(self, dashboard: DashboardPage):
        dashboard.click_tab("💹 Retorno Acumulado")
        assert "Retorno Acumulado" in dashboard.get_active_tab_name()

    def test_navegar_para_relatorio(self, dashboard: DashboardPage):
        dashboard.click_tab("📋 Relatório")
        assert "Relatório" in dashboard.get_active_tab_name()

    def test_ciclo_completo_entre_abas(self, dashboard: DashboardPage):
        for nome in DashboardPage.TABS.values():
            dashboard.click_tab(nome)
            assert nome.split()[-1] in dashboard.get_active_tab_name()

    def test_retornar_para_precos_apos_navegar(self, dashboard: DashboardPage):
        dashboard.click_tab("📋 Relatório")
        dashboard.click_tab("📊 Preços")
        assert "Preços" in dashboard.get_active_tab_name()


class TestConteudoPorAba:

    def test_aba_precos_exibe_grafico(self, dashboard: DashboardPage):
        dashboard.click_tab("📊 Preços")
        expect(dashboard.page.locator('[data-testid="stPlotlyChart"]').first).to_be_visible()

    def test_aba_tecnica_exibe_toggle_ma(self, dashboard_tecnica: DashboardPage):
        expect(dashboard_tecnica.page.get_by_label("Exibir Média Móvel")).to_be_visible()

    def test_aba_retorno_exibe_grafico(self, dashboard: DashboardPage):
        dashboard.click_tab("💹 Retorno Acumulado")
        expect(dashboard.page.locator('[data-testid="stPlotlyChart"]').first).to_be_visible()

    def test_aba_relatorio_exibe_tabela(self, dashboard_relatorio: DashboardPage):
        expect(dashboard_relatorio.page.locator('[data-testid="stDataFrame"]')).to_be_visible()

    def test_aba_relatorio_exibe_botao_export(self, dashboard_relatorio: DashboardPage):
        assert dashboard_relatorio.is_export_button_visible()

    def test_aba_relatorio_exibe_expander_disclaimer(self, dashboard_relatorio: DashboardPage):
        assert dashboard_relatorio.is_expander_visible("Aviso Legal")


class TestKpiCards:

    @pytest.mark.smoke
    def test_tres_kpi_cards_com_todas_operadoras(self, dashboard: DashboardPage):
        assert dashboard.get_kpi_card_count() == 3

    def test_kpi_card_exibe_medalha_ouro(self, dashboard: DashboardPage):
        assert dashboard.kpi_card_has_medal("🥇")

    def test_kpi_card_exibe_medalha_prata(self, dashboard: DashboardPage):
        assert dashboard.kpi_card_has_medal("🥈")

    def test_kpi_card_exibe_medalha_bronze(self, dashboard: DashboardPage):
        assert dashboard.kpi_card_has_medal("🥉")
