"""StudyFlow — interface principal."""

import html
import json
from datetime import date, datetime, timedelta

import streamlit as st

import db
from ai import ErroIA, gerar_plano


# ---------- Configuração ----------

st.set_page_config(
    page_title="StudyFlow",
    page_icon=":material/menu_book:",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.inicializar()


# ---------- Ícones (SVG inline, traço estilo Lucide) ----------

ICONES = {
    "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
    "list": '<rect x="8" y="2" width="8" height="4" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "sparkles": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.7 1.8 1.8.7-1.8.7L19 20l-.7-1.8-1.8-.7 1.8-.7z"/>',
    "target": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "alert": '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    "info": '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
}


def svg(nome: str, tamanho: int = 18, cor: str = "currentColor") -> str:
    """Retorna um ícone SVG inline em uma única linha."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{tamanho}" height="{tamanho}" '
        f'viewBox="0 0 24 24" fill="none" stroke="{cor}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" '
        f'style="vertical-align:-0.2em;flex-shrink:0">{ICONES[nome]}</svg>'
    )


PAGINAS = {
    "Painel": "dashboard",
    "Atividades": "checklist",
    "Histórico": "history",
}


# ---------- Estilização ----------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --sf-ink: #1f2e2e;
    --sf-surface: #e0ebeb;
    --sf-accent: #75a3a3;
    --sf-accent-dark: #3f6666;
    --sf-tint: #cadcdc;
    --sf-mist: #f0f5f5;
    --sf-line: #c2d4d4;
    --sf-radio: #94b8b8;
    --sf-muted: #5b7171;
    --sf-hot: #c93c41;
    --sf-warn: #a56a00;
    --sf-ok: #1a7f55;
}

html, body, .stApp, [class*="st-"] {
    font-family: 'Plus Jakarta Sans', 'Segoe UI', system-ui, sans-serif;
}

/* Mantém a fonte dos ícones Material (sem isso aparece o texto "add", "delete"...) */
[data-testid="stIconMaterial"],
[class*="material-symbols"] {
    font-family: "Material Symbols Rounded", "Material Symbols Outlined" !important;
}

.stApp { background: var(--sf-mist); }

#MainMenu, footer, .stAppDeployButton, [data-testid="stDeployButton"] { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }

.block-container {
    max-width: 1280px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

h1, h2, h3, h4 { color: var(--sf-ink); letter-spacing: -0.02em; }

/* ----- Barra lateral ----- */
[data-testid="stSidebar"] {
    background: var(--sf-ink);
    border-right: none;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }

.sf-brand { display: flex; align-items: center; gap: 12px; padding: 4px 8px 22px; }
.sf-logo {
    width: 42px; height: 42px; border-radius: 12px;
    background: var(--sf-accent); color: var(--sf-ink);
    display: grid; place-items: center;
}
.sf-brand-name { color: var(--sf-surface); font-weight: 800; font-size: 1.2rem; letter-spacing: -0.02em; }
.sf-brand-sub { color: #8fb0b0; font-size: 0.78rem; }

[data-testid="stSidebar"] [role="radiogroup"] { gap: 4px; }
[data-testid="stSidebar"] [role="radiogroup"] label {
    display: flex; align-items: center; gap: 12px;
    padding: 11px 14px;
    border-radius: 12px;
    width: 100%;
    cursor: pointer;
    transition: background 0.15s ease;
}
[data-testid="stSidebar"] [role="radiogroup"] label > div:not(:has(p)) { display: none; }
[data-testid="stSidebar"] [role="radiogroup"] label p {
    color: #a9c4c4; font-weight: 600; font-size: 0.95rem; margin: 0;
}
[data-testid="stSidebar"] [role="radiogroup"] label [data-testid="stMarkdownContainer"] { display: flex; align-items: center; }
[data-testid="stSidebar"] [role="radiogroup"] label:hover { background: rgba(224,235,235,0.07); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) { background: var(--sf-accent); }
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p { color: var(--sf-ink); }

/* ----- Cabeçalho de página ----- */
.sf-page-title { font-size: 1.9rem; font-weight: 800; color: var(--sf-ink); letter-spacing: -0.03em; margin: 0; }
.sf-page-sub { color: var(--sf-muted); margin: 4px 0 18px; font-size: 0.97rem; }

/* ----- Cartões ----- */
[class*="st-key-sfcard"] {
    background: var(--sf-surface);
    border: 1px solid var(--sf-line);
    border-radius: 18px;
    padding: 1.15rem 1.3rem;
    box-shadow: 0 1px 2px rgba(31, 46, 46, 0.05);
}
[data-testid="stForm"] { border: none; padding: 0; }

.sf-card-title { font-weight: 700; color: var(--sf-ink); font-size: 1.02rem; margin-bottom: 2px; }
.sf-card-sub { color: var(--sf-muted); font-size: 0.85rem; margin-bottom: 14px; }

/* ----- Indicadores ----- */
.sf-stat {
    background: var(--sf-surface); border: 1px solid var(--sf-line); border-radius: 18px;
    padding: 16px 18px; display: flex; align-items: center; gap: 14px;
}
.sf-stat-icon {
    width: 46px; height: 46px; border-radius: 13px;
    display: grid; place-items: center; background: var(--sf-tint); color: var(--sf-accent-dark);
}
.sf-stat-num { font-size: 1.55rem; font-weight: 800; color: var(--sf-ink); line-height: 1.1; letter-spacing: -0.03em; }
.sf-stat-label { color: var(--sf-muted); font-size: 0.82rem; font-weight: 500; }

/* ----- Etiquetas ----- */
.sf-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.sf-tag {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px; border-radius: 999px;
    font-size: 0.74rem; font-weight: 700; white-space: nowrap;
}
.sf-tag-neutral { background: var(--sf-tint); color: var(--sf-accent-dark); }
.sf-tag-ok { background: #c9e8da; color: var(--sf-ok); }
.sf-tag-warn { background: #f1e2bd; color: var(--sf-warn); }
.sf-tag-hot { background: #f2d3d4; color: var(--sf-hot); }

/* ----- Cartões de atividade ----- */
.sf-task {
    background: var(--sf-surface); border: 1px solid var(--sf-line); border-radius: 18px;
    padding: 18px; height: 100%; display: flex; flex-direction: column; gap: 10px;
}
.sf-task-title { font-weight: 700; color: var(--sf-ink); font-size: 1.02rem; line-height: 1.3; }
.sf-task-desc { color: var(--sf-muted); font-size: 0.87rem; line-height: 1.5; flex: 1; }
.sf-due { display: inline-flex; align-items: center; gap: 6px; font-size: 0.8rem; font-weight: 700; color: var(--sf-muted); }
.sf-due-hot { color: var(--sf-hot); }
.sf-due-warn { color: var(--sf-warn); }

.sf-act-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; }
.sf-act-title { font-weight: 700; font-size: 1.12rem; color: var(--sf-ink); margin: 8px 0 4px; }
.sf-act-desc { color: var(--sf-muted); font-size: 0.92rem; line-height: 1.55; margin-bottom: 4px; }

/* ----- Gráficos ----- */
.sf-donut-wrap { display: flex; flex-wrap: wrap; align-items: center; gap: 14px 22px; padding: 6px 0; }
.sf-donut { width: 128px; height: 128px; border-radius: 50%; display: grid; place-items: center; flex-shrink: 0; }
.sf-donut-hole {
    width: 90px; height: 90px; border-radius: 50%; background: var(--sf-surface);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.sf-donut-hole b { font-size: 1.35rem; color: var(--sf-ink); letter-spacing: -0.03em; }
.sf-donut-hole span { font-size: 0.7rem; color: var(--sf-muted); }
.sf-legend { display: flex; flex-direction: column; gap: 8px; font-size: 0.88rem; color: var(--sf-ink); }
.sf-dot { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }

.sf-bars { display: flex; align-items: flex-end; justify-content: space-between; gap: 10px; height: 150px; padding-top: 6px; }
.sf-bar-col { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; gap: 4px; }
.sf-bar { width: 100%; max-width: 34px; border-radius: 8px 8px 4px 4px; background: var(--sf-accent); }
.sf-bar-empty { background: var(--sf-line); }
.sf-bar-val { font-size: 0.78rem; font-weight: 700; color: var(--sf-ink); }
.sf-bar-day { font-size: 0.74rem; color: var(--sf-muted); }

/* ----- Agenda ----- */
.sf-agenda-item {
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid var(--sf-line);
}
.sf-agenda-item:last-child { border-bottom: none; }
.sf-date {
    min-width: 48px; border-radius: 12px; background: var(--sf-tint);
    text-align: center; padding: 6px 0; display: flex; flex-direction: column;
}
.sf-date b { color: var(--sf-accent-dark); font-size: 1.1rem; line-height: 1.1; }
.sf-date span { color: var(--sf-accent-dark); font-size: 0.68rem; font-weight: 600; }
.sf-agenda-body { flex: 1; min-width: 0; }
.sf-agenda-title { font-weight: 600; color: var(--sf-ink); font-size: 0.9rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sf-agenda-meta { color: var(--sf-muted); font-size: 0.78rem; }

.sf-empty { text-align: center; padding: 28px 12px; color: var(--sf-muted); font-size: 0.92rem; }
.sf-empty b { display: block; color: var(--sf-ink); font-size: 1rem; margin-bottom: 4px; }

/* ----- Plano de execução ----- */
.sf-analysis { color: var(--sf-ink); line-height: 1.65; font-size: 0.97rem; }
.sf-step { display: flex; gap: 14px; padding: 14px 0; border-bottom: 1px solid var(--sf-line); }
.sf-step:last-child { border-bottom: none; }
.sf-step-n {
    width: 32px; height: 32px; border-radius: 50%; flex-shrink: 0;
    background: var(--sf-accent); color: var(--sf-ink); font-weight: 800; font-size: 0.88rem;
    display: grid; place-items: center;
}
.sf-step-body { flex: 1; }
.sf-step-head { display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }
.sf-step-title { font-weight: 700; color: var(--sf-ink); }
.sf-step-body p { color: var(--sf-muted); font-size: 0.9rem; line-height: 1.55; margin: 4px 0 0; }
.sf-rec { display: flex; gap: 10px; padding: 7px 0; color: var(--sf-ink); font-size: 0.93rem; line-height: 1.5; }
.sf-rec i { color: var(--sf-ok); display: inline-flex; padding-top: 3px; }

/* ----- Botões e campos ----- */
.stButton > button, .stFormSubmitButton > button {
    border-radius: 11px; min-height: 2.6rem; font-weight: 600;
    border: 1px solid var(--sf-line); background: var(--sf-surface); color: var(--sf-ink);
    transition: 0.15s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover {
    border-color: var(--sf-accent-dark); color: var(--sf-accent-dark);
}
.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"],
button[data-testid="stBaseButton-primary"], button[data-testid="stBaseButton-primaryFormSubmit"] {
    background: var(--sf-accent); border-color: var(--sf-accent); color: var(--sf-ink);
}
.stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover, button[data-testid="stBaseButton-primaryFormSubmit"]:hover {
    background: var(--sf-accent-dark); border-color: var(--sf-accent-dark); color: var(--sf-surface);
}

/* Campos: cores explícitas, independentes do tema claro/escuro do navegador */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] * { color: var(--sf-ink) !important; }

[data-testid="stTextInputRootElement"],
[data-testid="stTextAreaRootElement"],
[data-testid="stSelectbox"] [role="group"],
[data-testid="stDateInputField"] {
    background: var(--sf-mist) !important;
    border: 1px solid var(--sf-line) !important;
    border-radius: 11px !important;
}
[data-testid="stTextInputRootElement"]:focus-within,
[data-testid="stTextAreaRootElement"]:focus-within,
[data-testid="stSelectbox"] [role="group"]:focus-within,
[data-testid="stDateInputField"]:focus-within {
    border-color: var(--sf-accent-dark) !important;
    box-shadow: 0 0 0 1px var(--sf-accent-dark);
}
[data-testid="stTextInputRootElement"] input,
[data-testid="stTextAreaRootElement"] textarea,
[data-testid="stSelectbox"] input,
[data-testid="stDateInputField"] *,
[data-testid="stSelectbox"] [role="group"] * {
    color: var(--sf-ink) !important;
    background-color: transparent;
}
[data-testid="stTextInputRootElement"] input::placeholder,
[data-testid="stTextAreaRootElement"] textarea::placeholder {
    color: var(--sf-muted) !important;
    opacity: 1;
}
[data-testid="stSelectbox"] svg, [data-testid="stDateInputField"] svg { fill: var(--sf-ink) !important; }

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid var(--sf-line) !important;
    border-radius: 14px;
    background: var(--sf-surface) !important;
    overflow: hidden;
}
[data-testid="stExpander"] details { background: transparent !important; border: none !important; }
[data-testid="stExpander"] summary { background: var(--sf-tint) !important; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: var(--sf-ink) !important; }

/* Botões de abrir/recolher a barra lateral */
[data-testid="stExpandSidebarButton"] {
    background: var(--sf-ink) !important;
    border-radius: 10px;
    padding: 6px 8px;
}
[data-testid="stExpandSidebarButton"] * { color: var(--sf-surface) !important; }
[data-testid="stSidebarCollapseButton"] * { color: #a9c4c4 !important; }

/* Seletor (rádio) do menu: #94b8b8 no lugar do vermelho padrão */
[data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child {
    background: transparent !important;
    border: 2px solid var(--sf-radio) !important;
}
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] > div > div:first-child {
    background: var(--sf-radio) !important;
    border-color: var(--sf-ink) !important;
}
[data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] > div > div:first-child > div {
    background: var(--sf-ink) !important;
}

/* Spinner e avisos independentes do tema do navegador */
[data-testid="stSpinner"], [data-testid="stSpinner"] * { color: var(--sf-ink) !important; }

.sf-alert {
    display: flex; align-items: flex-start; gap: 10px;
    padding: 12px 16px; border-radius: 12px; border: 1px solid;
    font-size: 0.92rem; line-height: 1.5; margin: 4px 0;
}
.sf-alert svg { margin-top: 2px; }
.sf-alert-hot { background: #f2d3d4; border-color: #e3b0b2; color: #8f2429; }
.sf-alert-warn { background: #f1e2bd; border-color: #e0cb94; color: #7a4f00; }
.sf-alert-ok { background: #c9e8da; border-color: #a5d3bd; color: #14603f; }
.sf-alert-neutral { background: var(--sf-tint); border-color: var(--sf-line); color: var(--sf-ink); }

/* Gráficos do painel com a mesma altura */
.st-key-sfcard-graf-cobertura, .st-key-sfcard-graf-semana { min-height: 265px; }
.sf-legend div { white-space: nowrap; }

@media (max-width: 768px) {
    .sf-donut-wrap { flex-direction: column; align-items: flex-start; }
}
</style>
""", unsafe_allow_html=True)

# ---------- Constantes e utilitários ----------

COR_ACENTO = "#75a3a3"
COR_LINHA = "#c2d4d4"

MESES = ["jan", "fev", "mar", "abr", "mai", "jun",
         "jul", "ago", "set", "out", "nov", "dez"]

MESES_LONGOS = ["janeiro", "fevereiro", "março", "abril", "maio", "junho",
                "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

DIAS_SEMANA = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def h(texto) -> str:
    """Escapa texto para uso seguro em HTML (conteúdo do usuário e da IA)."""
    return html.escape(str(texto)).replace("\n", "<br>")


def render(markup: str):
    """Renderiza HTML sem que o Markdown o interprete como bloco de código."""
    linhas = (linha.strip() for linha in markup.splitlines())
    st.markdown("".join(linhas), unsafe_allow_html=True)


def resumo(texto, limite: int = 110) -> str:
    texto = " ".join(str(texto).split())
    if len(texto) <= limite:
        return texto
    return texto[: limite - 1].rstrip() + "…"


def tag(texto, classe: str = "neutral", icone: str | None = None) -> str:
    símbolo = svg(icone, 13) if icone else ""
    return f'<span class="sf-tag sf-tag-{classe}">{símbolo}{h(texto)}</span>'


def parse_data(valor):
    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


def parse_datahora(valor):
    try:
        return datetime.fromisoformat(str(valor).replace("T", " "))
    except ValueError:
        return None


def formatar_data(data) -> str:
    return data.strftime("%d/%m/%Y") if data else "—"


def formatar_datahora(valor) -> str:
    momento = parse_datahora(valor)
    return momento.strftime("%d/%m/%Y %H:%M") if momento else str(valor)


def formatar_minutos(minutos: int) -> str:
    if minutos < 60:
        return f"{minutos} min"
    return f"{minutos // 60}h{minutos % 60:02d}"


def rotulo_prazo(data) -> tuple[str, str]:
    """Retorna (texto, classe de urgência) para um prazo."""
    if not data:
        return "Sem prazo", ""
    dias = (data - date.today()).days
    if dias < 0:
        return f"Atrasada há {-dias} dia(s)", "sf-due-hot"
    if dias == 0:
        return "Vence hoje", "sf-due-hot"
    if dias == 1:
        return "Vence amanhã", "sf-due-hot"
    if dias <= 3:
        return f"Em {dias} dias", "sf-due-warn"
    return f"Em {dias} dias", ""


def linha_prazo(data) -> str:
    """HTML da linha de prazo (ícone + data + urgência)."""
    texto, classe = rotulo_prazo(data)
    return (
        f'<div class="sf-due {classe}">{svg("calendar", 15)}'
        f'{formatar_data(data)} · {texto}</div>'
    )


def classe_dificuldade(nome) -> str:
    n = str(nome).lower()
    if n.startswith(("fác", "fac")):
        return "ok"
    if n.startswith(("méd", "med")):
        return "warn"
    if n.startswith("dif"):
        return "hot"
    return "neutral"


def classe_prioridade(nome) -> str:
    n = str(nome).lower()
    if n.startswith("alta"):
        return "hot"
    if n.startswith(("méd", "med")):
        return "warn"
    if n.startswith("baixa"):
        return "ok"
    return "neutral"


def alerta(tipo: str, texto):
    """Aviso próprio (hot = erro, warn = atenção, ok = sucesso, neutral = info)."""
    icone = {"hot": "alert", "warn": "alert", "ok": "check", "neutral": "info"}[tipo]
    render(f'<div class="sf-alert sf-alert-{tipo}">{svg(icone, 18)}<span>{h(texto)}</span></div>')


def card(chave: str):
    """Cartão estilizado: container com chave, que o CSS localiza por classe."""
    return st.container(key=f"sfcard-{chave}")


def ir_para(pagina: str):
    st.session_state["pagina"] = pagina


def cabecalho(titulo: str, subtitulo: str):
    render(
        f'<div class="sf-page-title">{h(titulo)}</div>'
        f'<div class="sf-page-sub">{h(subtitulo)}</div>'
    )


def card_indicador(icone: str, valor, rotulo: str):
    render(f"""
        <div class="sf-stat">
            <div class="sf-stat-icon">{svg(icone, 22)}</div>
            <div>
                <div class="sf-stat-num">{h(valor)}</div>
                <div class="sf-stat-label">{h(rotulo)}</div>
            </div>
        </div>
    """)


def minutos_do_plano(conteudo) -> int:
    try:
        plano = json.loads(conteudo)
        return sum(e["tempo_estimado_min"] for e in plano["etapas"])
    except (json.JSONDecodeError, KeyError, TypeError):
        return 0


# ---------- Componentes ----------

def exibir_plano(plano: dict):
    """Apresenta um plano de execução na interface."""

    tempo_total = sum(e["tempo_estimado_min"] for e in plano["etapas"])

    col1, col2 = st.columns(2)

    with col1:
        render(f"""
            <div class="sf-stat">
                <div class="sf-stat-icon">{svg("target", 22)}</div>
                <div>
                    <div class="sf-stat-num">{tag(plano["prioridade"], classe_prioridade(plano["prioridade"]))}</div>
                    <div class="sf-stat-label" style="margin-top:6px">Prioridade</div>
                </div>
            </div>
        """)

    with col2:
        card_indicador("clock", formatar_minutos(tempo_total), "Tempo estimado")

    render('<div class="sf-card-title" style="margin-top:18px">Análise da atividade</div>')
    render(f'<div class="sf-analysis">{h(plano["analise"])}</div>')

    render('<div class="sf-card-title" style="margin-top:22px">Etapas de execução</div>')
    etapas = "".join(
        f"""
        <div class="sf-step">
            <div class="sf-step-n">{indice}</div>
            <div class="sf-step-body">
                <div class="sf-step-head">
                    <span class="sf-step-title">{h(etapa["titulo"])}</span>
                    {tag(f"{etapa['tempo_estimado_min']} min", icone="clock")}
                </div>
                <p>{h(etapa["descricao"])}</p>
            </div>
        </div>
        """
        for indice, etapa in enumerate(plano["etapas"], start=1)
    )
    render(f"<div>{etapas}</div>")

    render('<div class="sf-card-title" style="margin-top:22px">Recomendações</div>')
    recomendacoes = "".join(
        f'<div class="sf-rec"><i>{svg("check", 16)}</i><span>{h(r)}</span></div>'
        for r in plano["recomendacoes"]
    )
    render(f"<div>{recomendacoes}</div>")


# ---------- Barra lateral ----------

with st.sidebar:
    render(f"""
        <div class="sf-brand">
            <div class="sf-logo">{svg("book", 22)}</div>
            <div>
                <div class="sf-brand-name">StudyFlow</div>
                <div class="sf-brand-sub">Planejador de estudos com IA</div>
            </div>
        </div>
    """)

    pagina = st.radio(
        "Navegação",
        list(PAGINAS),
        format_func=lambda p: f":material/{PAGINAS[p]}: {p}",
        key="pagina",
        label_visibility="collapsed",
    )


# ==================================================
# PÁGINA 1 — PAINEL
# ==================================================

def pagina_painel():

    atividades = db.listar_atividades()

    if st.session_state.pop("mensagem_plano_gerado", False):
        alerta("ok", "Plano gerado e salvo com sucesso!")

    planos = db.listar_planos()
    hoje = date.today()

    nomes_com_plano = {p["atividade"] for p in planos}
    itens = sorted(
        ((a, parse_data(a["prazo"])) for a in atividades),
        key=lambda par: par[1] or date.max,
    )

    # Último plano de cada atividade, para somar o tempo planejado
    ultimo_por_atividade = {}
    for p in planos:
        atual = ultimo_por_atividade.get(p["atividade"])
        if atual is None or str(p["criado_em"]) > str(atual["criado_em"]):
            ultimo_por_atividade[p["atividade"]] = p
    minutos_planejados = sum(
        minutos_do_plano(p["conteudo"]) for p in ultimo_por_atividade.values()
    )

    prazos_7_dias = sum(
        1 for _, d in itens if d and 0 <= (d - hoje).days <= 7
    )
    com_plano = sum(1 for a in atividades if a["nome"] in nomes_com_plano)

    # ---------- Cabeçalho ----------

    topo_esq, topo_dir = st.columns([4, 1], vertical_alignment="center")

    with topo_esq:
        cabecalho(
            "Painel",
            f"Hoje, {hoje.day} de {MESES_LONGOS[hoje.month - 1]} — "
            "veja o que precisa de atenção primeiro.",
        )

    with topo_dir:
        st.button(
            "Nova atividade",
            icon=":material/add:",
            type="primary",
            on_click=ir_para,
            args=("Atividades",),
            key="btn_nova_atividade",
        )

    # ---------- Indicadores ----------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        card_indicador("list", len(atividades), "Atividades")
    with c2:
        card_indicador("sparkles", len(planos), "Planos gerados")
    with c3:
        card_indicador("calendar", prazos_7_dias, "Prazos em 7 dias")
    with c4:
        card_indicador("clock", formatar_minutos(minutos_planejados), "Tempo planejado")

    st.write("")

    if not atividades:
        with card("c1"):
            render("""
                <div class="sf-empty">
                    <b>Nenhuma atividade por aqui ainda</b>
                    Cadastre sua primeira atividade para gerar um plano de execução com IA.
                </div>
            """)
            st.button(
                "Cadastrar atividade",
                icon=":material/add:",
                type="primary",
                on_click=ir_para,
                args=("Atividades",),
                key="btn_vazio_cadastrar",
            )
        return

    esquerda, direita = st.columns([2.3, 1], gap="large")

    # ---------- Coluna principal ----------

    with esquerda:

        render('<div class="sf-card-title">Prazos mais próximos</div>')
        render('<div class="sf-card-sub">As atividades que vencem primeiro.</div>')

        destaque = itens[:3]
        colunas = st.columns(len(destaque))

        for coluna, (atividade, prazo) in zip(colunas, destaque):
            status = (
                tag("Plano gerado", "ok", "check")
                if atividade["nome"] in nomes_com_plano
                else tag("Sem plano", "neutral")
            )
            with coluna:
                render(f"""
                    <div class="sf-task">
                        <div class="sf-tags">
                            {tag(atividade["dificuldade"], classe_dificuldade(atividade["dificuldade"]))}
                            {status}
                        </div>
                        <div class="sf-task-title">{h(atividade["nome"])}</div>
                        <div class="sf-task-desc">{h(resumo(atividade["descricao"]))}</div>
                        {linha_prazo(prazo)}
                    </div>
                """)

        st.write("")

        graf1, graf2 = st.columns(2, gap="medium")

        # Rosca: cobertura de planejamento
        with graf1:
            with card("graf-cobertura"):
                render('<div class="sf-card-title">Cobertura de planejamento</div>')
                render('<div class="sf-card-sub">Atividades que já têm plano gerado.</div>')

                total = len(atividades)
                pct = round(com_plano / total * 100)
                sem_plano = total - com_plano

                render(f"""
                    <div class="sf-donut-wrap">
                        <div class="sf-donut" style="background: conic-gradient({COR_ACENTO} 0 {pct}%, {COR_LINHA} {pct}% 100%);">
                            <div class="sf-donut-hole"><b>{pct}%</b><span>planejado</span></div>
                        </div>
                        <div class="sf-legend">
                            <div><span class="sf-dot" style="background:{COR_ACENTO}"></span>Com plano: {com_plano}</div>
                            <div><span class="sf-dot" style="background:{COR_LINHA}"></span>Sem plano: {sem_plano}</div>
                        </div>
                    </div>
                """)

        # Barras: planos gerados nos últimos 7 dias
        with graf2:
            with card("graf-semana"):
                render('<div class="sf-card-title">Planos nos últimos 7 dias</div>')
                render('<div class="sf-card-sub">Quantos planos você gerou por dia.</div>')

                dias = [hoje - timedelta(days=i) for i in range(6, -1, -1)]
                contagem = {d: 0 for d in dias}

                for p in planos:
                    momento = parse_datahora(p["criado_em"])
                    if momento and momento.date() in contagem:
                        contagem[momento.date()] += 1

                maximo = max(contagem.values()) or 1

                barras = "".join(
                    f"""
                    <div class="sf-bar-col">
                        <div class="sf-bar-val">{n}</div>
                        <div class="sf-bar {'sf-bar-empty' if n == 0 else ''}"
                             style="height:{max(6, int(n / maximo * 90))}px"></div>
                        <div class="sf-bar-day">{DIAS_SEMANA[d.weekday()]}</div>
                    </div>
                    """
                    for d, n in contagem.items()
                )
                render(f'<div class="sf-bars">{barras}</div>')

    # ---------- Agenda ----------

    with direita:
        with card("c4"):
            render('<div class="sf-card-title">Agenda</div>')
            render('<div class="sf-card-sub">Próximos prazos.</div>')

            proximas = [(a, d) for a, d in itens if d and d >= hoje][:6]

            if not proximas:
                render("""
                    <div class="sf-empty">
                        <b>Agenda livre</b>
                        Nenhum prazo pela frente.
                    </div>
                """)
            else:
                linhas = "".join(
                    f"""
                    <div class="sf-agenda-item">
                        <div class="sf-date"><b>{d.day:02d}</b><span>{MESES[d.month - 1]}</span></div>
                        <div class="sf-agenda-body">
                            <div class="sf-agenda-title">{h(a["nome"])}</div>
                            <div class="sf-agenda-meta">{rotulo_prazo(d)[0]}</div>
                        </div>
                        {tag(a["dificuldade"], classe_dificuldade(a["dificuldade"]))}
                    </div>
                    """
                    for a, d in proximas
                )
                render(f"<div>{linhas}</div>")


# ==================================================
# PÁGINA 2 — ATIVIDADES
# ==================================================

def pagina_atividades():

    cabecalho(
        "Atividades",
        "Cadastre suas atividades e gere um plano de execução para cada uma.",
    )

    # O plano gerado aparece no topo, acima da lista
    area_resultado = st.container()

    # ---------- Cadastro ----------

    with card("c5"):

        render('<div class="sf-card-title">Nova atividade</div>')
        render('<div class="sf-card-sub">Quanto mais detalhes, melhor o plano gerado.</div>')

        with st.form("form_atividade", clear_on_submit=True):

            nome = st.text_input(
                "Nome da atividade",
                max_chars=80,
                placeholder="Ex.: Estudar programação orientada a objetos"
            )

            descricao = st.text_area(
                "Descrição",
                height=120,
                max_chars=1000,
                placeholder="Descreva o que precisa aprender ou realizar..."
            )

            col1, col2 = st.columns(2)

            prazo = col1.date_input(
                "Prazo",
                min_value=date.today(),
                format="DD/MM/YYYY"
            )

            dificuldade = col2.selectbox(
                "Dificuldade",
                db.DIFICULDADES,
                index=1
            )

            enviado = st.form_submit_button(
                "Cadastrar atividade",
                icon=":material/add_task:",
                type="primary"
            )

        if enviado:

            nome = nome.strip()
            descricao = descricao.strip()

            if not nome and not descricao:
                alerta("hot", "Preencha os campos de nome e descrição.")

            elif not nome:
                alerta("hot", "Preencha o campo de nome.")

            elif not descricao:
                alerta("hot", "Preencha o campo de descrição.")

            elif len(nome) < 3:
                alerta("hot", "O nome deve possuir pelo menos 3 caracteres.")

            elif len(descricao) < 10:
                alerta("hot", "A descrição deve possuir pelo menos 10 caracteres.")

            else:
                try:
                    db.criar_atividade(
                        nome,
                        descricao,
                        prazo.isoformat(),
                        dificuldade
                    )

                    alerta("ok", "Atividade cadastrada com sucesso!")

                except ValueError as erro:
                    alerta("hot", str(erro))

    # ---------- Listagem ----------

    atividades = db.listar_atividades()
    nomes_com_plano = {p["atividade"] for p in db.listar_planos()}

    st.write("")
    render('<div class="sf-card-title" style="font-size:1.25rem">Minhas atividades</div>')

    if not atividades:

        with card("c6"):
            render("""
                <div class="sf-empty">
                    <b>Nenhuma atividade cadastrada</b>
                    Use o formulário acima para adicionar a primeira.
                </div>
            """)

    else:

        render(
            f'<div class="sf-card-sub">{len(atividades)} atividade(s) cadastrada(s).</div>'
        )

        for atividade in atividades:

            prazo_data = parse_data(atividade["prazo"])

            status = (
                tag("Plano gerado", "ok", "check")
                if atividade["nome"] in nomes_com_plano
                else tag("Sem plano", "neutral")
            )

            with card(f"atividade-{atividade['id']}"):

                render(f"""
                    <div class="sf-act-head">
                        <div class="sf-tags">
                            {tag(atividade["dificuldade"], classe_dificuldade(atividade["dificuldade"]))}
                            {status}
                        </div>
                        {linha_prazo(prazo_data)}
                    </div>
                    <div class="sf-act-title">{h(atividade["nome"])}</div>
                    <div class="sf-act-desc">{h(atividade["descricao"])}</div>
                """)

                confirmar_exclusao = (
                    st.session_state.get("confirmar_exclusao")
                    == atividade["id"]
                )

                # ---------- Botões ----------

                if not confirmar_exclusao:

                    col_gerar, col_excluir, _ = st.columns([1.5, 1.2, 3])

                    tem_plano = db.atividade_tem_plano(atividade["id"])

                    gerar = col_gerar.button(
                        label="Plano já gerado" if tem_plano else "Gerar plano com IA",
                        icon=":material/auto_awesome:",
                        key=f"gerar_{atividade['id']}",
                        type="primary",
                        disabled=tem_plano
                    )

                    excluir = col_excluir.button(
                        "Excluir",
                        icon=":material/delete:",
                        key=f"excluir_{atividade['id']}"
                    )

                    confirmar = False
                    cancelar = False

                else:

                    alerta("warn", 
                        "Tem certeza de que deseja excluir esta atividade? "
                        "Os planos associados também serão apagados."
                    )

                    col_confirmar, col_cancelar, _ = st.columns([1.5, 1.2, 3])

                    confirmar = col_confirmar.button(
                        "Sim, excluir",
                        icon=":material/delete:",
                        key=f"confirmar_{atividade['id']}",
                        type="primary"
                    )

                    cancelar = col_cancelar.button(
                        "Cancelar",
                        key=f"cancelar_{atividade['id']}"
                    )

                    gerar = False
                    excluir = False

                # ---------- Geração do plano ----------

                if gerar:
                    if db.atividade_tem_plano(atividade["id"]):
                        st.session_state["atividade_com_plano"] = atividade["id"]
                        st.rerun()

                    with st.spinner(
                        "A inteligência artificial está "
                        "organizando sua atividade..."
                    ):

                        try:

                            plano, modelo = gerar_plano(atividade)

                            conteudo = plano.model_dump_json(
                                ensure_ascii=False
                            )

                            db.salvar_plano(
                                atividade["id"],
                                conteudo,
                                modelo
                            )

                            st.session_state["plano_atual"] = {
                                "atividade": atividade["nome"],
                                "plano": plano.model_dump(),
                                "modelo": modelo
                            }

                            st.session_state["mensagem_plano_gerado"] = True

                            st.rerun()

                        except ErroIA as erro:

                            alerta("hot", str(erro))

                        except Exception as erro:

                            alerta("hot", 
                                "Ocorreu um erro inesperado "
                                "ao gerar o planejamento."
                            )

                            st.exception(erro)

                # ---------- Exclusão ----------

                if excluir:

                    st.session_state["confirmar_exclusao"] = atividade["id"]
                    st.rerun()

                if cancelar:

                    st.session_state.pop("confirmar_exclusao", None)
                    st.rerun()

                if confirmar:

                    removida = db.excluir_atividade(atividade["id"])

                    if removida:

                        plano_atual = st.session_state.get("plano_atual")

                        if (
                            plano_atual
                            and plano_atual["atividade"] == atividade["nome"]
                        ):
                            del st.session_state["plano_atual"]

                        st.session_state.pop("confirmar_exclusao", None)

                        st.toast("Atividade excluída com sucesso!")
                        st.rerun()

                    else:

                        st.session_state.pop("confirmar_exclusao", None)

                        alerta("warn", 
                            "Não foi possível encontrar essa atividade."
                        )

    # ---------- Resultado recente (renderizado no topo da página) ----------

    resultado = st.session_state.get("plano_atual")

    if resultado:

        with area_resultado:

            with card("c7"):

                render(f"""
                    <div class="sf-act-head">
                        <div class="sf-card-title" style="font-size:1.2rem">
                            Plano gerado: {h(resultado["atividade"])}
                        </div>
                        {tag(f"Modelo: {resultado['modelo']}")}
                    </div>
                """)

                exibir_plano(resultado["plano"])

            st.write("")


# ==================================================
# PÁGINA 3 — HISTÓRICO
# ==================================================

def pagina_historico():

    cabecalho(
        "Histórico de planos",
        "Consulte os planos de estudo que você já gerou.",
    )

    planos = db.listar_planos()

    if not planos:

        with card("c8"):
            render("""
                <div class="sf-empty">
                    <b>Nenhum plano gerado ainda</b>
                    Gere seu primeiro plano na página de atividades.
                </div>
            """)
            st.button(
                "Ir para atividades",
                icon=":material/arrow_forward:",
                type="primary",
                on_click=ir_para,
                args=("Atividades",),
                key="btn_hist_vazio",
            )
        return

    busca = st.text_input(
        "Buscar por atividade",
        placeholder="Digite parte do nome da atividade...",
        label_visibility="collapsed",
    ).strip().lower()

    filtrados = [
        p for p in planos
        if busca in str(p["atividade"]).lower()
    ]

    render(
        f'<div class="sf-card-sub">{len(filtrados)} de {len(planos)} '
        f'planejamento(s) exibido(s).</div>'
    )

    if not filtrados:
        alerta("neutral", "Nenhum plano encontrado para essa busca.")
        return

    for registro in filtrados:

        with st.expander(
            f"{registro['atividade']} — "
            f"{formatar_datahora(registro['criado_em'])}"
        ):

            render(tag(f"Modelo: {registro['modelo']}"))

            try:

                plano = json.loads(registro["conteudo"])

                exibir_plano(plano)

            except (json.JSONDecodeError, KeyError):

                alerta("hot", 
                    "Não foi possível carregar este planejamento."
                )


# ---------- Roteamento ----------

if pagina == "Painel":
    pagina_painel()
elif pagina == "Atividades":
    pagina_atividades()
else:
    pagina_historico()