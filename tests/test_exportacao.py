"""
Testes de exportação CSV, expanders e aviso legal.
Cobre: download de arquivo, expand/collapse, renderização condicional.
"""
import re
import pytest
from playwright.sync_api import expect
from pages.dashboard import DashboardPage


class TestExportacaoCSV:

    @pytest.mark.smoke
    def test_botao_exportar_visivel_na_aba_relatorio(self, dashboard_relatorio: DashboardPage):
        assert dashboard_relatorio.is_export_button_visible()

    def test_botao_exportar_ausente_em_outras_abas(self, dashboard: DashboardPage):
        for tab_name in ["📊 Preços", "📈 Análise Técnica", "💹 Retorno Acumulado"]:
            dashboard.click_tab(tab_name)
            assert not dashboard.page.get_by_role(
                "button", name=re.compile("Exportar métricas")
            ).is_visible()

    def test_download_csv_disparado_ao_clicar(self, dashboard_relatorio: DashboardPage):
        with dashboard_relatorio.page.expect_download() as download_info:
            dashboard_relatorio.click_export_csv().click()
        download = download_info.value
        assert download.suggested_filename.endswith(".csv")

    def test_nome_do_arquivo_csv_contem_metricas(self, dashboard_relatorio: DashboardPage):
        with dashboard_relatorio.page.expect_download() as download_info:
            dashboard_relatorio.click_export_csv().click()
        download = download_info.value
        assert "metricas" in download.suggested_filename

    def test_nome_do_arquivo_csv_contem_datas(self, dashboard_relatorio: DashboardPage):
        with dashboard_relatorio.page.expect_download() as download_info:
            dashboard_relatorio.click_export_csv().click()
        download = download_info.value
        # Padrão: metricas_telecom_YYYY-MM-DD_YYYY-MM-DD.csv
        assert re.search(r"\d{4}-\d{2}-\d{2}", download.suggested_filename)


class TestExpanders:

    @pytest.mark.smoke
    def test_expander_aviso_legal_presente(self, dashboard_relatorio: DashboardPage):
        assert dashboard_relatorio.is_expander_visible("Aviso Legal")

    def test_expander_aviso_legal_fechado_por_padrao(self, dashboard_relatorio: DashboardPage):
        assert not dashboard_relatorio.is_expander_open("Aviso Legal")

    def test_expander_aviso_legal_abre_ao_clicar(self, dashboard_relatorio: DashboardPage):
        dashboard_relatorio.toggle_expander("Aviso Legal")
        assert dashboard_relatorio.is_expander_open("Aviso Legal")

    def test_expander_aviso_legal_fecha_ao_clicar_novamente(self, dashboard_relatorio: DashboardPage):
        dashboard_relatorio.toggle_expander("Aviso Legal")   # abre
        dashboard_relatorio.toggle_expander("Aviso Legal")   # fecha
        assert not dashboard_relatorio.is_expander_open("Aviso Legal")

    def test_conteudo_aviso_legal_exibe_disclaimer(self, dashboard_relatorio: DashboardPage):
        dashboard_relatorio.toggle_expander("Aviso Legal")
        expect(
            dashboard_relatorio.page.get_by_text("exclusivamente educacional")
        ).to_be_visible()

    def test_conteudo_aviso_legal_menciona_cvm(self, dashboard_relatorio: DashboardPage):
        dashboard_relatorio.toggle_expander("Aviso Legal")
        expect(dashboard_relatorio.page.get_by_text("CVM")).to_be_visible()


class TestExpanders_Oi:

    @pytest.mark.smoke
    def test_expander_oi_presente_quando_selecionada(self, dashboard_relatorio: DashboardPage):
        assert dashboard_relatorio.is_expander_visible("Situação da Oi")

    def test_expander_oi_fechado_por_padrao(self, dashboard_relatorio: DashboardPage):
        assert not dashboard_relatorio.is_expander_open("Situação da Oi")

    def test_expander_oi_abre_ao_clicar(self, dashboard_relatorio: DashboardPage):
        dashboard_relatorio.toggle_expander("Situação da Oi")
        assert dashboard_relatorio.is_expander_open("Situação da Oi")

    def test_conteudo_oi_menciona_recuperacao_judicial(self, dashboard_relatorio: DashboardPage):
        dashboard_relatorio.toggle_expander("Situação da Oi")
        expect(
            dashboard_relatorio.page.get_by_text("recuperação judicial")
        ).to_be_visible()

    def test_expander_oi_ausente_quando_oi_desmarcada(self, dashboard: DashboardPage):
        dashboard.toggle_company("Oi")
        dashboard.click_tab("📋 Relatório")
        assert not dashboard.is_expander_visible("Situação da Oi")

    def test_expander_oi_reaparece_ao_remarcar_oi(self, dashboard: DashboardPage):
        dashboard.toggle_company("Oi")   # desmarca
        dashboard.toggle_company("Oi")   # remarca
        dashboard.wait_for_app_ready()
        dashboard.click_tab("📋 Relatório")
        assert dashboard.is_expander_visible("Situação da Oi")
