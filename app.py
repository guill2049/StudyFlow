
"""StudyFlow — interface principal."""

import json
from datetime import date

import streamlit as st

import db
from ai import ErroIA, gerar_plano


# ---------- Configuração ----------

st.set_page_config(
    page_title="StudyFlow",
    page_icon="📚",
    layout="wide"
)

db.inicializar()


# ---------- Funções auxiliares ----------

def exibir_plano(plano: dict):
    """Apresenta um plano de execução na interface."""

    st.markdown("### Análise da atividade")
    st.write(plano["analise"])

    col1, col2 = st.columns(2)

    col1.metric("Prioridade", plano["prioridade"])

    tempo_total = sum(
        etapa["tempo_estimado_min"]
        for etapa in plano["etapas"]
    )

    col2.metric("Tempo estimado", f"{tempo_total} min")

    st.markdown("### Etapas de execução")

    for indice, etapa in enumerate(plano["etapas"], start=1):
        with st.expander(
            f"{indice}. {etapa['titulo']}",
            expanded=True
        ):
            st.write(etapa["descricao"])
            st.caption(
                f"Tempo estimado: "
                f"{etapa['tempo_estimado_min']} minutos"
            )

    st.markdown("### Recomendações")

    for recomendacao in plano["recomendacoes"]:
        st.markdown(f"- {recomendacao}")


# ---------- Cabeçalho ----------

st.title("📚 StudyFlow")

st.caption(
    "Organize suas atividades acadêmicas "
    "e transforme-as em planos de execução."
)

aba_atividades, aba_historico = st.tabs(
    ["📋 Atividades", "🧠 Histórico de planos"]
)


# ==================================================
# ABA 1 — ATIVIDADES
# ==================================================

with aba_atividades:

    st.subheader("Nova atividade")

    with st.form("form_atividade", clear_on_submit=True):

        nome = st.text_input("Nome da atividade", max_chars=80)

        descricao = st.text_area(
            "Descrição",
            height=120,
            max_chars=1000
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
            type="primary"
        )

    if enviado:

        if not nome.strip() or not descricao.strip():

            st.error("Informe o nome e a descrição.")

        else:

            db.criar_atividade(
                nome,
                descricao,
                prazo.isoformat(),
                dificuldade
            )

            st.success("Atividade cadastrada com sucesso!")


    # ---------- Listagem ----------

    st.divider()
    st.subheader("Minhas atividades")

    atividades = db.listar_atividades()

    if not atividades:

        st.info("Nenhuma atividade cadastrada ainda.")

    else:

        for atividade in atividades:

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                col1.markdown(f"### {atividade['nome']}")

                col2.caption(
                    f"Prazo: {atividade['prazo']}"
                )

                st.write(atividade["descricao"])

                st.caption(
                    f"Dificuldade: {atividade['dificuldade']}"
                )

                gerar = st.button(
                    "✨ Gerar plano com IA",
                    key=f"gerar_{atividade['id']}",
                    type="primary"
                )

                if gerar:

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

                            st.success(
                                "Plano gerado e salvo com sucesso!"
                            )

                        except ErroIA as erro:

                            st.error(str(erro))

                        except Exception as erro:

                            st.error(
                                "Ocorreu um erro inesperado "
                                "ao gerar o planejamento."
                            )

                            st.exception(erro)


    # ---------- Resultado recente ----------

    resultado = st.session_state.get("plano_atual")

    if resultado:

        st.divider()

        st.subheader(
            f"Plano gerado: {resultado['atividade']}"
        )

        st.caption(f"Modelo utilizado: {resultado['modelo']}")

        exibir_plano(resultado["plano"])


# ==================================================
# ABA 2 — HISTÓRICO
# ==================================================

with aba_historico:

    st.subheader("Histórico de planejamentos")

    planos = db.listar_planos()

    if not planos:

        st.info("Você ainda não gerou nenhum planejamento.")

    else:

        for registro in planos:

            with st.expander(
                f"📚 {registro['atividade']} — "
                f"{registro['criado_em']}"
            ):

                st.caption(
                    f"Modelo utilizado: {registro['modelo']}"
                )

                try:

                    plano = json.loads(registro["conteudo"])

                    exibir_plano(plano)

                except (json.JSONDecodeError, KeyError):

                    st.error(
                        "Não foi possível carregar este planejamento."
                    )
