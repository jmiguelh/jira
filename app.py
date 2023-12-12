import streamlit as st
import pandas as pd
import time
import jira

TIPO = ["Todos", "Evolutivo", "Corretivo"]
SETOR = ["Todos", "CRL", "Comercial", "Têxtil"]
STATUS = [
    "Backlog",
    "Especificação",
    "Desenvolvimento",
    "Homologação",
    "Produção",
    "Concluído",
    "Systextil",
]

with st.sidebar:
    st.image("img/lunelli.png", width=250)
    with st.expander(":pushpin: Filtos"):
        setor = st.selectbox("Setor:", SETOR)
        tipo = st.selectbox("Tipo:", TIPO)
        status = st.multiselect("Status:", STATUS, default=STATUS)
    with st.expander(
        f":arrows_counterclockwise:Última atualização: {jira.ultima_atualzacao()}"
    ):
        if st.button("Recarregar dados"):
            with st.spinner("Carregando..."):
                jira.carregar()
            st.success("Sucesso!")
            time.sleep(3)
            st.rerun()

    st.write("")
    st.image("img/salesforce_logo.png", width=150)


topo = st.container()
topo.title("Salesforce Squad")

print(status)

# pd.DataFrame()
# conn = st.connection()
