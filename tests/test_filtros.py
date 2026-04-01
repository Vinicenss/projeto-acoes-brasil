"""
Testes de filtros da sidebar: atalhos de período, datas e seleção de operadoras.
Cobre: session state, validação de inputs, renderização condicional.
"""
import pytest
from playwright.sync_api import expect
from pages.dashboard import DashboardPage


class TestAtalhosDePeríodo:

    @pytest.mark.smoke
    def test_seis_botoes_de_atalho_presentes(self, dashboard: DashboardPage):
        for label in DashboardPage.PERIOD_SHORTCUTS:
            btn = dashboard.page.get_by_role("button", name=label).first
            expect(btn).to_be_visible()

    def test_atalho_1m_atualiza_status_bar(self, dashboard: DashboardPage):
        pregoes_antes = dashboard.get_pregoes_count()
        dashboard.click_period_shortcut("1M")
        pregoes_depois = dashboard.get_pregoes_count()
        # 1 mês tem menos pregões que o período padrão de 1 ano
        assert pregoes_depois < pregoes_antes

    def test_atalho_1a_atualiza_status_bar(self, dashboard: DashboardPage):
        dashboard.click_period_shortcut("1A")
        texto = dashboard.get_status_bar_text()
        assert "pregões carregados" in texto

    def test_atalho_ytd_carrega_dados(self, dashboard: DashboardPage):
        dashboard.click_period_shortcut("YTD")
        texto = dashboard.get_status_bar_text()
        assert "pregões carregados" in texto

    @pytest.mark.slow
    def test_atalho_2a_tem_mais_pregoes_que_1a(self, dashboard: DashboardPage):
        dashboard.click_period_shortcut("1A")
        pregoes_1a = dashboard.get_pregoes_count()

        dashboard.click_period_shortcut("2A")
        pregoes_2a = dashboard.get_pregoes_count()

        assert pregoes_2a > pregoes_1a

    def test_atalho_3m_tem_menos_pregoes_que_6m(self, dashboard: DashboardPage):
        dashboard.click_period_shortcut("3M")
        pregoes_3m = dashboard.get_pregoes_count()

        dashboard.click_period_shortcut("6M")
        pregoes_6m = dashboard.get_pregoes_count()

        assert pregoes_3m < pregoes_6m


class TestValidacaoDeDatas:

    def test_data_inicio_anterior_ao_fim_e_valida(self, dashboard: DashboardPage):
        # Estado padrão deve ser válido
        expect(dashboard.page.locator(".status-bar")).to_be_visible()

    def test_mensagem_de_erro_com_data_inicio_igual_ao_fim(self, dashboard: DashboardPage):
        dashboard.set_date_inicio("2025/06/01")
        dashboard.set_date_fim("2025/06/01")
        expect(
            dashboard.page.get_by_text("A data de início deve ser anterior")
        ).to_be_visible()

    def test_recovery_apos_corrigir_datas_invalidas(self, dashboard: DashboardPage):
        # Cria estado de erro
        dashboard.set_date_inicio("2025/06/10")
        dashboard.set_date_fim("2025/06/01")
        # Corrige
        dashboard.set_date_inicio("2025/01/01")
        dashboard.wait_for_app_ready()
        expect(dashboard.page.locator(".status-bar")).to_be_visible()


class TestSelecaoDeOperadoras:

    @pytest.mark.smoke
    def test_todas_operadoras_marcadas_por_padrao(self, dashboard: DashboardPage):
        for company in DashboardPage.COMPANIES:
            assert dashboard.is_company_checked(company)

    def test_desmarcar_oi_remove_seu_kpi_card(self, dashboard: DashboardPage):
        assert dashboard.get_kpi_card_count() == 3
        dashboard.toggle_company("Oi")
        assert dashboard.get_kpi_card_count() == 2

    def test_remarcar_oi_restaura_tres_kpi_cards(self, dashboard: DashboardPage):
        dashboard.toggle_company("Oi")
        assert dashboard.get_kpi_card_count() == 2
        dashboard.toggle_company("Oi")
        dashboard.wait_for_app_ready()
        assert dashboard.get_kpi_card_count() == 3

    def test_desmarcar_todas_exibe_aviso(self, dashboard: DashboardPage):
        dashboard.uncheck_all_companies()
        expect(
            dashboard.page.get_by_text("Selecione ao menos uma operadora")
        ).to_be_visible()

    def test_apenas_uma_operadora_exibe_um_kpi_card(self, dashboard: DashboardPage):
        dashboard.check_only("Vivo")
        dashboard.wait_for_app_ready()
        assert dashboard.get_kpi_card_count() == 1

    def test_status_bar_atualiza_contagem_de_operadoras(self, dashboard: DashboardPage):
        assert dashboard.get_operator_count() == 3
        dashboard.toggle_company("TIM")
        dashboard.wait_for_app_ready()
        assert dashboard.get_operator_count() == 2

    def test_desmarcar_oi_oculta_expander_de_aviso(self, dashboard: DashboardPage):
        dashboard.toggle_company("Oi")
        dashboard.click_tab("📋 Relatório")
        assert not dashboard.is_expander_visible("Situação da Oi")

    def test_com_oi_selecionada_expander_de_aviso_aparece(self, dashboard_relatorio: DashboardPage):
        assert dashboard_relatorio.is_expander_visible("Situação da Oi")
