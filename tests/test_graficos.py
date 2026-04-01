"""
Testes de gráficos e análise técnica.
Cobre: visibilidade dos charts, média móvel (toggle + slider), relatório textual.
"""
import pytest
from playwright.sync_api import expect
from pages.dashboard import DashboardPage


class TestGraficoDePrecos:

    @pytest.mark.smoke
    def test_grafico_visivel_na_aba_precos(self, dashboard: DashboardPage):
        dashboard.click_tab("📊 Preços")
        expect(
            dashboard.page.locator('[data-testid="stPlotlyChart"]').first
        ).to_be_visible(timeout=15_000)

    def test_titulo_secao_precos_historicos(self, dashboard: DashboardPage):
        dashboard.click_tab("📊 Preços")
        expect(dashboard.page.get_by_text("Preços Históricos")).to_be_visible()


class TestMediaMovel:

    @pytest.mark.smoke
    def test_toggle_ma_desligado_por_padrao(self, dashboard_tecnica: DashboardPage):
        assert not dashboard_tecnica.is_ma_toggle_checked()

    @pytest.mark.smoke
    def test_slider_oculto_com_toggle_desligado(self, dashboard_tecnica: DashboardPage):
        assert not dashboard_tecnica.is_ma_slider_visible()

    def test_toggle_liga_exibe_slider(self, dashboard_tecnica: DashboardPage):
        dashboard_tecnica.click_ma_toggle()
        assert dashboard_tecnica.is_ma_toggle_checked()
        assert dashboard_tecnica.is_ma_slider_visible()

    def test_toggle_desliga_oculta_slider(self, dashboard_tecnica: DashboardPage):
        dashboard_tecnica.click_ma_toggle()   # liga
        dashboard_tecnica.click_ma_toggle()   # desliga
        assert not dashboard_tecnica.is_ma_slider_visible()

    def test_slider_ma_valor_padrao_e_20(self, dashboard_tecnica: DashboardPage):
        dashboard_tecnica.click_ma_toggle()
        assert dashboard_tecnica.get_ma_period_value() == 20

    def test_slider_ma_incrementa_com_seta_direita(self, dashboard_tecnica: DashboardPage):
        dashboard_tecnica.click_ma_toggle()
        dashboard_tecnica.set_ma_period(25)
        assert dashboard_tecnica.get_ma_period_value() == 25

    def test_slider_ma_decrementa_com_seta_esquerda(self, dashboard_tecnica: DashboardPage):
        dashboard_tecnica.click_ma_toggle()
        dashboard_tecnica.set_ma_period(10)
        assert dashboard_tecnica.get_ma_period_value() == 10

    def test_grafico_tecnica_visivel_com_ma_ativo(self, dashboard_tecnica: DashboardPage):
        dashboard_tecnica.click_ma_toggle()
        expect(
            dashboard_tecnica.page.locator('[data-testid="stPlotlyChart"]').first
        ).to_be_visible()

    def test_grafico_volatilidade_visivel_na_aba_tecnica(self, dashboard_tecnica: DashboardPage):
        titulo = dashboard_tecnica.page.get_by_text("Volatilidade")
        expect(titulo).to_be_visible()


class TestGraficoRetornoAcumulado:

    def test_grafico_retorno_visivel(self, dashboard: DashboardPage):
        dashboard.click_tab("💹 Retorno Acumulado")
        expect(
            dashboard.page.locator('[data-testid="stPlotlyChart"]').first
        ).to_be_visible()

    def test_titulo_secao_retorno_acumulado(self, dashboard: DashboardPage):
        dashboard.click_tab("💹 Retorno Acumulado")
        expect(dashboard.page.get_by_text("Retorno Acumulado")).to_be_visible()


class TestRelatorioDeAnalise:

    def test_titulo_resumo_do_periodo_visivel(self, dashboard_relatorio: DashboardPage):
        expect(
            dashboard_relatorio.page.get_by_text("Resumo do Período")
        ).to_be_visible()

    def test_relatorio_menciona_melhor_desempenho(self, dashboard_relatorio: DashboardPage):
        expect(
            dashboard_relatorio.page.get_by_text("melhor desempenho")
        ).to_be_visible()

    def test_relatorio_menciona_volatilidade(self, dashboard_relatorio: DashboardPage):
        expect(
            dashboard_relatorio.page.get_by_text("mais volátil")
        ).to_be_visible()

    def test_tabela_comparativa_presente(self, dashboard_relatorio: DashboardPage):
        expect(
            dashboard_relatorio.page.locator('[data-testid="stDataFrame"]')
        ).to_be_visible()

    def test_legenda_da_tabela_presente(self, dashboard_relatorio: DashboardPage):
        expect(
            dashboard_relatorio.page.get_by_text("melhor desempenho no período")
        ).to_be_visible()
