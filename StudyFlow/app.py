"""StudyFlow — interface Streamlit (Etapa 1: cadastro e listagem)."""
from datetime import date

import pandas as pd
import streamlit as st

import db

st.set_page_config(page_title="StudyFlow", page_icon="📚", layout="centered")
db.inicializar()

st.title("📚 StudyFlow")
st.caption("Organize suas atividades acadêmicas e transforme-as em planos de execução.")

aba_atividades, = st.tabs(["Atividades"])

with aba_atividades:
    st.subheader("Nova atividade")

    with st.form("form_atividade", clear_on_submit=True):
        nome = st.text_input("Nome da atividade")
        descricao = st.text_area("Descrição", height=120)
        col1, col2 = st.columns(2)
        prazo = col1.date_input("Prazo", min_value=date.today(), format="DD/MM/YYYY")
        dificuldade = col2.selectbox("Dificuldade", db.DIFICULDADES, index=1)
        enviado = st.form_submit_button("Cadastrar", type="primary")

    if enviado:
        if not nome.strip() or not descricao.strip():
            st.error("Informe o nome e a descrição da atividade.")
        else:
            db.criar_atividade(nome, descricao, prazo.isoformat(), dificuldade)
            st.success(f"Atividade “{nome.strip()}” cadastrada.")

    st.divider()
    st.subheader("Atividades cadastradas")

    atividades = db.listar_atividades()
    if not atividades:
        st.info("Nenhuma atividade cadastrada ainda.")
    else:
        df = pd.DataFrame(atividades)
        df["prazo"] = pd.to_datetime(df["prazo"]).dt.strftime("%d/%m/%Y")
        df = df[["id", "nome", "prazo", "dificuldade", "descricao"]]
        df.columns = ["ID", "Atividade", "Prazo", "Dificuldade", "Descrição"]
        st.dataframe(df, use_container_width=True, hide_index=True)