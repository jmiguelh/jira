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

### Barra lateral ###
with st.sidebar:
    st.image("img/lunelli_colorida.png", width=250)
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

### Título ###
topo = st.container()
topo.title("Salesforce Squad")

### Primeria Linha ###
corpo = st.container()
a, b, c = corpo.columns(3)

total_cards = painel.total_cards()
cards_aberto_ultimo_dia = painel.cards_aberto_ultimo_dia()
cards_aberto_no_mes = painel.cards_aberto_no_mes()
total_cards_concluidos = painel.total_cards_concluidos()
cards_conluidos_ultimo_dia = painel.cards_conluidos_ultimo_dia()
cards_concludos_no_mes = painel.cards_concludos_no_mes()

linha = a.container()
a1, a2 = linha.columns(2)
a1.metric(label="Total de cards abertos", value=total_cards)
a2.metric(
    label="Total de cards concluídos",
    value=total_cards_concluidos,
    delta=total_cards - total_cards_concluidos,
)

linha = a.container()
a1, a2 = linha.columns(2)
a1.metric(
    label="Cards aberto ontem",
    value=cards_aberto_ultimo_dia,
)
a2.metric(
    label="Cards concluídos ontem",
    value=cards_conluidos_ultimo_dia,
    delta=cards_aberto_ultimo_dia - cards_conluidos_ultimo_dia,
)

linha = a.container()
a1, a2 = linha.columns(2)
a1.metric(label="Cards abertos no mês", value=cards_aberto_no_mes)
a2.metric(
    label="Cards concluídos no mês",
    value=cards_concludos_no_mes,
    delta=cards_aberto_no_mes - cards_concludos_no_mes,
)


b.write("Cards aberto por mês")
fig = px.bar(
    painel.cards_por_mes(),
    x="Mês",
    y=["Corretivo", "Evolutivo"],
    text_auto=True,
)
fig.update_layout(
    legend=dict(
        orientation="h", entrywidth=70, yanchor="bottom", y=1.02, xanchor="right", x=1
    )
)
b.plotly_chart(fig, use_container_width=True)


fig = px.pie(
    painel.cards_por_setor(), values="Quantidade", names="Setor", width=450, height=450
)
fig.update_layout(
    legend=dict(
        orientation="h", entrywidth=70, yanchor="bottom", y=1.02, xanchor="right", x=1
    )
)
c.write("Cards aberto por setor")
c.plotly_chart(fig, use_container_width=True)


### Segunda linha ###
rodape = st.container()
a, b, c = rodape.columns(3)

a.write("% Apropriação por tipo")
fig = px.bar(
    painel.apropriacao_por_tipo(),
    x=["Corretivo", "Evolutivo"],
    y="Mês",
    text_auto=True,
    orientation="h",
)
fig.update_layout(
    legend=dict(
        orientation="h", entrywidth=70, yanchor="bottom", y=1.02, xanchor="right", x=1
    )
)
a.plotly_chart(fig, use_container_width=True)


b.write("Cards concluído por mês")

fig = px.bar(
    painel.cards_concluido_por_mes(),
    x="Mês",
    y=["Corretivo", "Evolutivo"],
    text_auto=True,
)
fig.update_layout(
    legend=dict(
        orientation="h", entrywidth=70, yanchor="bottom", y=1.02, xanchor="right", x=1
    )
)
b.plotly_chart(fig, use_container_width=True)

c.write("Cards concluído no mês por setor")
fig = px.pie(
    painel.cards_concluido_por_mes_setor(),
    values="Quantidade",
    names="Setor",
    width=450,
    height=450,
)
fig.update_layout(
    legend=dict(
        orientation="h", entrywidth=70, yanchor="bottom", y=1.02, xanchor="right", x=1
    )
)
c.plotly_chart(fig, use_container_width=True)
