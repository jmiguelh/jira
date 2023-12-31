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
COLOR_DISCRETE_MAP = {"Têxtil": "olive", "Comercial": "orange", "CRL": "royalblue"}


def barra_lateral():
    with st.sidebar:
        st.image("img/lunelli_colorida.png", width=250)
        with st.expander(":pushpin: Filtos"):
            setor = st.selectbox("Setor:", SETOR)
            tipo = st.selectbox("Tipo:", TIPO)
            status = st.multiselect("Status:", STATUS, default=STATUS)
        with st.expander(
            f":arrows_counterclockwise: Última atualização: {jira.ultima_atualzacao()}"
        ):
            if st.button("Recarregar dados"):
                with st.spinner("Carregando..."):
                    jira.carregar()
                st.success("Sucesso! Repocessando...")
                time.sleep(3)
                st.rerun()

        st.write("")
        st.image("img/salesforce_logo.png", width=150)
        return (setor, tipo, status)


def primeira_linha():
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
        y="Cards",
        color="Tipo",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        )
    )
    b.plotly_chart(fig, use_container_width=True)

    fig = px.pie(
        painel.cards_por_setor(),
        values="Quantidade",
        names="Setor",
        color="Setor",
        color_discrete_map=COLOR_DISCRETE_MAP,
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        )
    )
    c.write("Cards aberto por setor")
    c.plotly_chart(fig, use_container_width=True)


def segunda_linha():
    rodape = st.container()
    a, b, c = rodape.columns(3)

    a.write("% Apropriação por tipo")
    fig = px.bar(
        painel.apropriacao_por_tipo(),
        x=["Corretivo", "Evolutivo"],
        y="Mês",
        text_auto=True,
        orientation="h",
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        )
    )
    a.plotly_chart(fig, use_container_width=True)

    b.write("Cards concluído por mês")

    fig = px.bar(
        painel.cards_concluido_por_mes(),
        x="Mês",
        y="Cards",
        color="Tipo",
        text_auto=True,
        color_discrete_sequence=px.colors.qualitative.Set1,
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        )
    )
    b.plotly_chart(fig, use_container_width=True)

    c.write("Cards concluído no mês por setor")
    fig = px.pie(
        painel.cards_concluido_por_mes_setor(),
        values="Quantidade",
        names="Setor",
        color="Setor",
        color_discrete_map=COLOR_DISCRETE_MAP,
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        )
    )
    c.plotly_chart(fig, use_container_width=True)


def terceira_linha():
    terceira = st.container()
    a, b = terceira.columns(2)

    a.write("Evolução dos cards")
    fig = px.area(
        painel.diario_por_status(),
        x="Data",
        y="Cards",
        color="Status",
        line_group="Status",
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        )
    )
    a.plotly_chart(fig, use_container_width=True)

    b.write("% Apropriação por Setor")
    fig = px.bar(
        painel.apropriacao_por_pai(),
        x=["Comercial", "Têxtil", "CRL"],
        y="Mês",
        text_auto=True,
        orientation="h",
        color_discrete_map=COLOR_DISCRETE_MAP,
    )
    fig.update_layout(
        legend=dict(
            orientation="h",
            entrywidth=70,
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        )
    )
    b.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(
        page_title="Lunelli - Salesforce Squad",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="auto",
    )
    ### Remover o botão Deploy
    st.markdown(
        """
            <style>
                .reportview-container {
                    margin-top: -2em;
                }
                #MainMenu {visibility: hidden;}
                .stDeployButton {display:none;}
                footer {visibility: hidden;}
                #stDecoration {display:none;}
            </style>
        """,
        unsafe_allow_html=True,
    )

    setor, tipo, status = barra_lateral()
    ### Filtros ###
    df_cards = painel.carregar_cards()
    if setor != "Todos":
        df_cards_filtrados = df_cards[df_cards.pai == setor]
    else:
        df_cards_filtrados = df_cards

    if tipo != "Todos":
        df_cards_filtrados = df_cards_filtrados[
            df_cards_filtrados.tipo_agrupado == tipo
        ]

    df_cards_filtrados = df_cards_filtrados.loc[df_cards.status_agrupado.isin(status)]
    df_cards_filtrados = df_cards_filtrados.sort_index(ascending=False)

    st.title("Salesforce Squad")

    tab1, tab2 = st.tabs(["Gráficos", "Dados"])
    with tab1:
        primeira_linha()

        segunda_linha()

        terceira_linha()

    with tab2:
        st.metric(label="Total de cards", value=len(df_cards_filtrados))
        st.write("Cards")
        st.dataframe(df_cards_filtrados, hide_index=True)


if __name__ == "__main__":
    main()
