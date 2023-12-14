import streamlit as st
import pandas as pd
import plotly.express as px
import time
import jira
import models.painel as painel

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

st.set_page_config(
    page_title="Lunelli - Salesforce Squad",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
            st.success("Sucesso! Repocessando...")
            time.sleep(3)
            st.rerun()

    st.write("")
    st.image("img/salesforce_logo.png", width=150)

topo = st.container()
topo.title("Salesforce Squad")

corpo = st.container()
a, b, c = corpo.columns(3)

a.metric(
    label="Total de cards abertos",
    value=painel.total_cards(),
    delta=painel.cards_aberto_ultimo_dia(),
)
a.metric(
    label="Cards abertos no Mês",
    value=painel.cards_aberto_no_mes(),
)

b.write("Cards aberto por mês")
b.bar_chart(painel.cards_por_mes())

fig = px.pie(
    painel.cards_por_setor(), values="Quantidade", names="Setor", width=450, height=450
)

c.write("Cards aberto por setor")
c.plotly_chart(fig)

# c.bar_chart(painel.cards_por_setor())

rodape = st.container()
a, b = rodape.columns(2)

a.bar_chart(painel.cards_por_setor_status())
