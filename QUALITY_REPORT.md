# QUALITY_REPORT.md

Registro de erros encontrados, estratégias de correção aplicadas, melhorias implementadas na aplicação e reflexão sobre o valor desse processo na rotina de um profissional de QA.

---

## 1. Erros encontrados e estratégias de correção

### 1.1 `ModuleNotFoundError: No module named 'pages'`

**Contexto:** Primeira execução da suíte. O `conftest.py` importava `from pages.dashboard import DashboardPage`, mas o pytest não sabia onde encontrar o módulo `pages`.

**Causa raiz:** O pytest executa a partir da raiz do projeto (`/projeto_claude_code`), mas o diretório `tests/` não estava no `sys.path`. O módulo `pages` existe dentro de `tests/pages/`, portanto era invisível para o Python.

**Estratégia de correção:** Adicionar `pythonpath = tests` ao `pytest.ini`. Isso instrui o pytest a incluir o diretório `tests/` no `sys.path` antes de coletar os testes, tornando `from pages.dashboard import DashboardPage` válido.

```ini
# pytest.ini
[pytest]
testpaths = tests
pythonpath = tests   ← linha adicionada
addopts = -v --tb=short
```

**Categoria:** Configuração de ambiente — erro clássico em projetos que separam testes em subdiretórios com Page Objects.

---

### 1.2 `AssertionError: Locator expected to be visible` — gráfico Plotly

**Contexto:** Todos os testes que verificavam a presença de um gráfico falhavam com timeout, mesmo após aguardar 15 segundos.

**Causa raiz:** O seletor utilizado era `[data-testid="stPlotlyChart"]`, baseado na documentação do Streamlit. Porém, no Streamlit 1.32.0 (versão usada no projeto), esse `data-testid` **não é adicionado ao DOM** pelo componente de gráfico. O Streamlit injetou o gráfico diretamente via iframe ou sem esse atributo nessa versão.

**Estratégia de correção:** Substituir pelo seletor `.js-plotly-plot`, que é a classe CSS nativa adicionada pelo próprio Plotly ao renderizar qualquer gráfico. Esse seletor é independente do framework que o embute (Streamlit, Dash, etc.) e portanto mais estável a mudanças de versão.

```python
# Antes
dashboard.page.locator('[data-testid="stPlotlyChart"]').first

# Depois
dashboard.page.locator('.js-plotly-plot').first
```

**Lição:** Seletores baseados em `data-testid` de frameworks de UI são frágeis entre versões. Seletores baseados em comportamento da biblioteca subjacente (Plotly, no caso) são mais duráveis.

---

### 1.3 `strict mode violation` — texto "Yahoo Finance" com múltiplas ocorrências

**Contexto:** O teste `test_subtitulo_visivel` falhava com erro de violação de modo estrito: `get_by_text("Yahoo Finance")` resolvia para 2 elementos.

**Causa raiz:** O texto "Yahoo Finance" aparecia tanto no subtítulo do dashboard quanto no texto do Disclaimer (seção de aviso legal), que estava colapsado mas presente no DOM.

**Estratégia de correção:** Usar `locator(".main-subtitle")` para restringir a busca ao elemento correto antes de verificar o texto.

```python
# Antes — não especifica contexto
expect(dashboard.page.get_by_text("Yahoo Finance")).to_be_visible()

# Depois — âncora no elemento correto
expect(dashboard.page.locator(".main-subtitle")).to_contain_text("Yahoo Finance")
```

**Lição:** `get_by_text` em modo estrito falha se o texto existir em múltiplos lugares do DOM — inclusive em elementos ocultos. Sempre ancorar buscas de texto em um contexto de elemento pai quando o texto for genérico.

---

### 1.4 `wait_for_rerun` — estratégia de sincronização com `stStatusWidget` não confiável

**Contexto:** Os testes de filtros e atalhos de período eventualmente falhavam ou passavam por sorte, dependendo da velocidade do fetch de dados.

**Causa raiz:** A estratégia original usava `[data-testid="stStatusWidget"]` para detectar quando o Streamlit estava re-executando. Esse elemento não existe de forma consistente no Streamlit 1.32.0 — foi renomeado ou removido em alguma versão. Como o seletor nunca aparecia, o `try/except` silenciava o erro e o teste prosseguia sem esperar, lendo dados desatualizados.

**Estratégia de correção:** Substituir por `page.wait_for_timeout(4_000)` — um timeout fixo conservador. Para interações que não buscam dados externos (toggle de MA, troca de aba), valores menores (1s, 3s) foram aplicados proporcionalmente.

```python
# Antes — dependia de elemento que não existia
def wait_for_rerun(self):
    try:
        self.page.wait_for_selector("[data-testid='stStatusWidget']", state="visible", timeout=3_000)
    except Exception:
        pass
    self.page.wait_for_selector("[data-testid='stStatusWidget']", state="hidden", timeout=20_000)

# Depois — pragmático e confiável
def wait_for_rerun(self):
    self.page.wait_for_timeout(4_000)
```

**Lição:** Estratégias de sincronização baseadas em indicadores de UI são preferíveis a timeouts fixos em teoria — mas dependem de que esses indicadores existam e sejam estáveis. Quando não existem, o timeout fixo é a alternativa honesta e documentada.

---

### 1.5 Interação com inputs de data (`set_date_inicio`, `set_date_fim`)

**Contexto:** Testes de validação de datas podiam falhar dependendo do estado interno do campo.

**Causa raiz:** O método original usava `select_all()` + `type()`. Em componentes de formulário React (como os que o Streamlit usa internamente), `select_all()` não garante que o conteúdo anterior seja substituído antes da digitação — o evento de seleção pode não propagar corretamente para o estado do componente.

**Estratégia de correção:** Substituir por `fill()`, que no Playwright limpa o campo e insere o valor em uma única operação atômica, respeitando o ciclo de eventos do React.

```python
# Antes
field.click()
field.select_all()
field.type(value)
field.press("Enter")

# Depois
field.click()
field.fill(value)
field.press("Enter")
```

---

## 2. Melhorias implementadas na aplicação

Além da suíte de testes, o projeto evoluiu em diversas frentes durante o processo de desenvolvimento.

### 2.1 Tema claro com maior contraste

A interface foi redesenhada do tema escuro original para um tema claro com paleta coerente:

| Elemento | Antes | Depois |
|---|---|---|
| Fundo geral | `#0e1117` (escuro) | `#f8f9fa` (off-white) |
| Texto principal | `#f0f6fc` | `#1a1a2e` |
| Cards | `#1c2128` | `#ffffff` com sombra |
| Cores das empresas | Claro sobre escuro | Escuro sobre claro (violeta, azul, âmbar) |

Os gráficos Plotly também foram alinhados ao novo tema: fundo branco, grade sutil e cores das empresas recalibradas para manter contraste adequado no novo contexto.

### 2.2 Tabs de navegação

O conteúdo foi organizado em 4 abas distintas, eliminando o scroll longo de página única:

- **Preços** — gráfico histórico de fechamento
- **Análise Técnica** — gráfico com suporte a média móvel + volatilidade
- **Retorno Acumulado** — gráfico base-100
- **Relatório** — tabela comparativa, análise textual e exportação

### 2.3 Atalhos de período

Seis botões de acesso rápido (`1M`, `3M`, `6M`, `YTD`, `1A`, `2A`) foram adicionados à sidebar, integrados ao `session_state` do Streamlit para atualizar os date inputs automaticamente sem recarregamento manual.

### 2.4 Média móvel configurável

Na aba Análise Técnica, um toggle ativa a exibição de médias móveis sobre o gráfico de preços. Um slider (5 a 60 dias, padrão 20) controla o período. As linhas são exibidas tracejadas com opacidade reduzida para não poluir o gráfico principal.

### 2.5 Status bar

Uma barra de status acima dos KPI cards exibe em tempo real: quantidade de pregões carregados, intervalo de datas e número de operadoras selecionadas. É o principal indicador de "saúde" do dashboard — e se tornou o ancora de sincronização da suíte de testes.

### 2.6 Ranking de performance nos KPI cards

Cada card exibe uma medalha (🥇 🥈 🥉) indicando a posição relativa de cada empresa no período. O ranking é calculado dinamicamente com base na variação total (%).

### 2.7 Exportação de dados (CSV)

Botão de download na aba Relatório gera um arquivo `.csv` com as métricas do período selecionado. O nome do arquivo inclui as datas do intervalo para rastreabilidade.

### 2.8 Expanders para avisos

Os blocos de aviso da Oi (recuperação judicial) e o Disclaimer legal foram movidos para `st.expander()`. A interface fica mais limpa por padrão e o usuário expande quando necessário. Também simplifica os testes: a presença/ausência e o estado aberto/fechado se tornaram cenários distintos e verificáveis.

### 2.9 Publicação automatizada no GitHub

Um hook `post-commit` (`.git/hooks/post-commit`) executa `git push origin main` automaticamente após cada commit. Qualquer alteração no projeto é publicada sem etapa manual adicional.

---

## 3. Valor para a rotina de QA — melhoria contínua na prática

Este projeto ilustra, em escala reduzida, um ciclo que se repete no trabalho de qualidade de software profissional.

### O ciclo que aconteceu aqui

```
Construir → Testar → Falhar → Diagnosticar → Corrigir → Testar novamente
```

Cada falha revelou algo que não era óbvio antes de executar: um `data-testid` que não existia na versão do framework, um seletor ambíguo que resolvia para múltiplos elementos, uma estratégia de espera que dependia de um indicador inexistente. Nenhum desses problemas teria sido encontrado lendo o código — só aparecem em execução.

### Por que isso é valioso no dia a dia de QA

**1. Testes automatizados tornam a regressão barata.**
Cada nova feature adicionada ao dashboard poderia quebrar comportamentos existentes. Com a suíte em execução, basta rodar `pytest -m smoke` após qualquer alteração para saber em segundos se algo regrediu.

**2. Falhas de teste são especificações vivas.**
Quando `test_desmarcar_oi_oculta_expander_de_aviso` falha, ele não está dizendo apenas "algo quebrou" — está dizendo exatamente *o que* quebrou: a lógica condicional que oculta o expander quando a Oi não está selecionada. Isso acelera o diagnóstico.

**3. O Page Object protege os testes de mudanças de UI.**
Quando o tema foi alterado de escuro para claro, nenhum teste precisou ser reescrito. Os seletores estavam todos encapsulados em `DashboardPage`. Isso é o princípio DRY aplicado a automação de testes.

**4. Documentar as falhas é parte do trabalho de QA.**
Este relatório existe porque erros não documentados se repetem. A próxima vez que alguém usar `data-testid` de um framework sem verificar se aquela versão o suporta, esse histórico serve de referência. Em equipes, esse conhecimento vive em wikis, relatórios de bug e post-mortems.

**5. Qualidade não é uma fase — é um loop.**
O projeto não foi construído e depois testado. Features foram adicionadas *para criar testabilidade*: tabs tornam a navegação testável, a status bar se tornou o indicador de sincronização dos testes, os expanders criaram cenários de expand/collapse. Desenvolvimento e qualidade aconteceram em paralelo, cada um informando o outro.
