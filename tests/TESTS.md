# TESTS.md

Este arquivo documenta a estrutura, decisões e convenções da suíte de testes E2E do dashboard Telecom Brasil.

## Pré-requisitos

O app deve estar rodando antes de executar os testes:
```bash
python3 -m streamlit run projeto_acoes/app.py
```

Instalar dependências de teste (apenas uma vez):
```bash
python3 -m pip install -r requirements-test.txt
python3 -m playwright install chromium
```

## Como executar

```bash
# Suíte completa
python3 -m pytest

# Apenas testes smoke (rápidos, sem dependência de dados externos)
python3 -m pytest -m smoke

# Apenas testes lentos (envolvem múltiplas chamadas à API do Yahoo Finance)
python3 -m pytest -m slow

# Um arquivo específico
python3 -m pytest tests/test_navegacao.py

# Uma classe ou teste específico
python3 -m pytest tests/test_filtros.py::TestAtalhosDePeríodo::test_atalho_1m_atualiza_status_bar

# Com browser visível (útil para depurar falhas)
python3 -m pytest --headed

# Com browser visível e execução lenta
python3 -m pytest --headed --slowmo=800
```

## Estrutura de arquivos

```
tests/
├── TESTS.md                  ← este arquivo
├── conftest.py               ← fixtures globais e marcadores
├── pages/
│   └── dashboard.py          ← Page Object Model
├── test_navegacao.py         ← carregamento, tabs, KPI cards
├── test_filtros.py           ← período, datas, operadoras
├── test_graficos.py          ← charts, média móvel, relatório
└── test_exportacao.py        ← CSV download, expanders
```

---

## Page Object Model — `pages/dashboard.py`

Toda interação com o DOM está encapsulada na classe `DashboardPage`. Os arquivos de teste nunca acessam seletores diretamente — eles chamam métodos do Page Object.

### Grupos de métodos

| Grupo | Métodos principais |
|---|---|
| Navegação | `goto()`, `click_tab(name)`, `get_active_tab_name()` |
| Sincronização | `wait_for_app_ready()`, `wait_for_rerun()` |
| Atalhos de período | `click_period_shortcut(label)` |
| Datas | `get_date_inicio()`, `get_date_fim()`, `set_date_inicio(v)`, `set_date_fim(v)` |
| Operadoras | `is_company_checked(name)`, `toggle_company(name)`, `check_only(name)`, `uncheck_all_companies()` |
| Status bar | `get_status_bar_text()`, `get_pregoes_count()`, `get_operator_count()` |
| KPI cards | `get_kpi_card_count()`, `kpi_card_has_medal(medal)` |
| Média móvel | `is_ma_toggle_checked()`, `click_ma_toggle()`, `is_ma_slider_visible()`, `set_ma_period(value)`, `get_ma_period_value()` |
| Export | `is_export_button_visible()`, `click_export_csv()` |
| Expanders | `is_expander_visible(text)`, `is_expander_open(text)`, `toggle_expander(text)` |
| Alertas | `has_warning(text)`, `has_error(text)` |

### Estratégia de sincronização com o Streamlit

O Streamlit re-executa o script inteiro a cada interação do usuário. Para garantir que os testes não leiam estado desatualizado:

- **`wait_for_app_ready()`** — aguarda o elemento `.status-bar` ficar visível. Esse elemento só aparece após o carregamento completo dos dados. Usado após `goto()` e interações que causam recarregamento.
- **`wait_for_rerun()`** — aguarda o indicador de status do Streamlit (`stStatusWidget`) aparecer e desaparecer. Usado após cliques em botões de período.
- **`page.wait_for_timeout(ms)`** — usado pontualmente após interações de UI que não causam rerun completo (ex: trocar de aba, toggle de MA).

---

## Fixtures — `conftest.py`

| Fixture | Escopo | Descrição |
|---|---|---|
| `page` | function | Fornecida pelo `pytest-playwright`. Instância limpa do browser por teste. |
| `set_default_timeout` | function (autouse) | Define timeout padrão de 20s para todos os testes. |
| `dashboard` | function | Navega para o app e aguarda carregamento completo. Ponto de entrada padrão. |
| `dashboard_relatorio` | function | `dashboard` já posicionado na aba **Relatório**. |
| `dashboard_tecnica` | function | `dashboard` já posicionado na aba **Análise Técnica**. |

As fixtures `dashboard_relatorio` e `dashboard_tecnica` herdam de `dashboard` — evitam repetição de navegação nos testes que precisam de uma aba específica.

---

## Marcadores

| Marcador | Quando usar |
|---|---|
| `@pytest.mark.smoke` | Testes de sanidade rápidos que validam o funcionamento básico sem depender de dados externos. Devem passar sempre. |
| `@pytest.mark.slow` | Testes que fazem múltiplas chamadas à API (ex: comparar contagem de pregões entre períodos). Podem ser lentos em conexões ruins. |

---

## Cobertura por arquivo

### `test_navegacao.py` — 14 testes

| Classe | O que valida |
|---|---|
| `TestCarregamentoInicial` | Título, subtítulo, status bar presente e com conteúdo correto |
| `TestAbas` | Presença das 4 tabs, tab padrão ativa, navegação entre todas |
| `TestConteudoPorAba` | Cada aba exibe seu conteúdo exclusivo (chart, toggle, tabela, botão de export) |
| `TestKpiCards` | 3 cards com todas operadoras, presença das 3 medalhas |

### `test_filtros.py` — 16 testes

| Classe | O que valida |
|---|---|
| `TestAtalhosDePeríodo` | 6 botões presentes; 1M reduz pregões; ordenação 3M < 6M < 1A < 2A |
| `TestValidacaoDeDatas` | Estado válido padrão; erro ao início = fim; recovery após correção |
| `TestSelecaoDeOperadoras` | Todas marcadas por padrão; desmarcar reduz cards; aviso ao desmarcar todas; status bar atualiza contagem; expander da Oi some quando ela é desmarcada |

### `test_graficos.py` — 14 testes

| Classe | O que valida |
|---|---|
| `TestGraficoDePrecos` | Chart visível na aba Preços; título da seção |
| `TestMediaMovel` | Toggle off por padrão; slider oculto sem toggle; toggle liga/desliga slider; valor padrão 20; incremento e decremento via teclado; chart visível com MA ativo |
| `TestGraficoRetornoAcumulado` | Chart visível; título da seção |
| `TestRelatorioDeAnalise` | Resumo do período presente; textos de melhor desempenho e volatilidade; tabela comparativa; legenda da tabela |

### `test_exportacao.py` — 12 testes

| Classe | O que valida |
|---|---|
| `TestExportacaoCSV` | Botão visível só na aba Relatório; download disparado ao clicar; extensão `.csv`; nome contém "metricas" e datas |
| `TestExpanders` | Aviso Legal presente, fechado por padrão, abre/fecha ao clicar, conteúdo com "CVM" e "educacional" |
| `TestExpanders_Oi` | Expander da Oi presente quando selecionada, fechado por padrão, abre ao clicar, conteúdo menciona recuperação judicial, some ao desmarcar Oi, reaparece ao remarcar |

---

## Convenções adotadas

- **Um `assert` por teste** — cada teste valida uma única condição. Falhas são fáceis de localizar.
- **Nomes descritivos** — o nome do teste descreve o comportamento esperado, não a implementação.
- **Sem dados hardcoded de negócio** — testes não verificam valores de preço ou variação (mudam a cada dia). Verificam estrutura, presença e comportamento.
- **Isolamento por fixture** — cada teste recebe um browser limpo. Não há dependência de ordem de execução.
