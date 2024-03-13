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
    # "Systextil",
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
    dftipo = painel.total_cards_tipo()
    dftipo7 = painel.total_cards_tipo(30)

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

    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(
        label="Total de Cards Evolutivos",
        value=dftipo.loc["Evolutivo"],
        delta=int(dftipo.loc["Evolutivo"] - dftipo7.loc["Evolutivo"]),
    )
    a2.metric(
        label="Total de Cards Corretivos",
        value=dftipo.loc["Corretivo"],
        delta=int(dftipo.loc["Corretivo"] - dftipo7.loc["Corretivo"]),
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


def quarta_linha():
    linha = st.container()
    a, b = linha.columns(2)

    df = painel.diario()
    df = df.groupby(["Status"]).sum()
    df7 = painel.diario(7)
    df7 = df7.groupby(["Status"]).sum()

    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(
        label="Total de cards no quadro",
        value=df.Quantidade.sum(),
        delta=(int(df.Quantidade.sum() - df7.Quantidade.sum())),
    )
    a.write("Total de cards por status")
    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(
        label="Especificação",
        value=df.loc["1 - Especificação"].Quantidade.item(),
        delta=(
            df.loc["1 - Especificação"].Quantidade.item()
            - df7.loc["1 - Especificação"].Quantidade.item()
        ),
    )
    a2.metric(
        label="Desenvolvimento",
        value=df.loc["2 - Desenvolvimento"].Quantidade.item(),
        delta=(
            df.loc["2 - Desenvolvimento"].Quantidade.item()
            - df7.loc["2 - Desenvolvimento"].Quantidade.item()
        ),
    )

    linha = a.container()
    a1, a2 = linha.columns(2)
    a1.metric(
        label="Homologação",
        value=df.loc["3 - Homologação"].Quantidade.item(),
        delta=(
            df.loc["3 - Homologação"].Quantidade.item()
            - df7.loc["3 - Homologação"].Quantidade.item()
        ),
    )
    a2.metric(
        label="Produção",
        value=(
            df.loc["4 - Produção"].Quantidade.item()
            if "4 - Produção" in df.index
            else 0
        ),
        delta=(
            df.loc["4 - Produção"].Quantidade.item()
            if "4 - Produção" in df.index
            else (
                0 - df7.loc["4 - Produção"].Quantidade.item()
                if "4 - Produção" in df7.index
                else 0
            )
        ),
    )

    df = painel.diario()
    b.write("Cards na esteira por tipo")
    fig = px.funnel(
        df.groupby(["Status", "Tipo"], as_index=False).sum(),
        x="Quantidade",
        y="Status",
        color="Tipo",
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


def colorir_linha(row):
    cor = [
        (
            "background-color: #f2f28d"
            if row["status_agrupado"] != "1- Baclog"
            and row["status_agrupado"] != "0 - Concluído"
            else (
                "background-color: lightgreen"
                if row["status_agrupado"] == "0 - Concluído"
                else ""
            )
        )
        for _ in row.index
    ]
    return cor


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
    df_cards = pd.merge(df_cards, painel.carregar_apropriacao(), how="left", on=["id"])
    df_cards["apropriacao"] = df_cards["apropriacao"] / 3600
    df_cards["apropriacao"].fillna(0, inplace=True)

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

    tab1, tab2, tab3 = st.tabs(["Gráficos", "Prioridade", "Dados"])
    ### Gráficos ###
    with tab1:
        primeira_linha()

        segunda_linha()

        terceira_linha()

        quarta_linha()

    ### Prioridade ###
    with tab2:
        df_prioridade = pd.merge(
            df_cards, painel.carregar_prioridade(), how="left", on=["chave"]
        )
        df_prioridade = df_prioridade.set_index("chave")

        tab4, tab5, tab6 = st.tabs(["Comercial", "Têxtil", "CRL"])

        with tab4:
            ### Comrcial ###
            df = df_prioridade.loc[
                (df_prioridade.tipo_agrupado == "Evolutivo")
                & (df_prioridade.pai == "Comercial")
            ]
            df["ordem"].fillna(0, inplace=True)
            df = df.loc[
                (df.ordem != 0)
                | (df.status_agrupado != "Concluído")
                | (df.criado > "20240313")
            ]

            df = df[
                [
                    "descricao",
                    "ordem",
                    "status_agrupado",
                    "DiasUltStatus",
                    "apropriacao",
                ]
            ]
            df.replace(
                {
                    "Backlog": "1- Baclog",
                    "Especificação": "2 - Especificação.",
                    "Desenvolvimento": "3 - Desenvolvimento.",
                    "Homologação": "4 - Homologação.",
                    "Produção": "5 - Produção",
                    "Concluído": "0 - Concluído",
                    "Systextil": "6 - Systextil",
                },
                inplace=True,
            )
            df = df.sort_values(
                by=["ordem", "status_agrupado", "DiasUltStatus"],
                ascending=[False, True, True],
            )
            df = df.style.apply(colorir_linha, axis=1).format(
                {"ordem": "{:.2f}", "DiasUltStatus": "{:.0f}", "apropriacao": "{:.2f}"}
            )
            st.subheader(f"Comercial - {len(df.index)}")
            st.dataframe(df, use_container_width=True, height=2000)

        with tab5:
            ### Têxtil ###
            df = df_prioridade.loc[
                (df_prioridade.tipo_agrupado == "Evolutivo")
                & (df_prioridade.pai == "Têxtil")
            ]
            df["ordem"].fillna(4, inplace=True)
            df = df.loc[
                (df.ordem != 4)
                | (df.status_agrupado != "Concluído")
                | (df.criado > "20231213")
            ]
            df = df[
                [
                    "descricao",
                    "ordem",
                    "status_agrupado",
                    "DiasUltStatus",
                    "apropriacao",
                ]
            ]
            df = df.replace(
                {
                    "Backlog": "1- Baclog",
                    "Especificação": "2 - Especificação.",
                    "Desenvolvimento": "3 - Desenvolvimento.",
                    "Homologação": "4 - Homologação.",
                    "Produção": "5 - Produção",
                    "Concluído": "0 - Concluído",
                    "Systextil": "6 - Systextil",
                }
            )
            df = df.sort_values(by=["ordem", "status_agrupado", "DiasUltStatus"])
            df = df.style.apply(colorir_linha, axis=1).format(
                {"ordem": "{:.0f}", "DiasUltStatus": "{:.0f}", "apropriacao": "{:.2f}"}
            )
            st.subheader(f"Têxtil - {len(df.index)}")
            st.dataframe(df, use_container_width=True, height=2000)

        with tab6:
            ### CRL ###
            df = df_prioridade.loc[
                (df_prioridade.tipo_agrupado == "Evolutivo")
                & (df_prioridade.pai == "CRL")
            ]
            df["ordem"].fillna(4, inplace=True)
            df = df.loc[
                (df.ordem != 4)
                | (df.status_agrupado != "Concluído")
                | (df.criado > "20231213")
            ]
            df = df[
                [
                    "descricao",
                    "ordem",
                    "status_agrupado",
                    "DiasUltStatus",
                    "apropriacao",
                ]
            ]
            df = df.replace(
                {
                    "Backlog": "1- Baclog",
                    "Especificação": "2 - Especificação.",
                    "Desenvolvimento": "3 - Desenvolvimento.",
                    "Homologação": "4 - Homologação.",
                    "Produção": "5 - Produção",
                    "Concluído": "0 - Concluído",
                    "Systextil": "6 - Systextil",
                }
            )
            df = df.sort_values(by=["ordem", "status_agrupado", "DiasUltStatus"])
            df = df.style.apply(colorir_linha, axis=1).format(
                {"ordem": "{:.0f}", "DiasUltStatus": "{:.0f}", "apropriacao": "{:.2f}"}
            )
            st.subheader(f"CRL - {len(df.index)}")
            st.dataframe(df, use_container_width=True, height=2000)

    ### Dados ###
    with tab3:
        st.metric(label="Total de cards", value=len(df_cards_filtrados))
        st.write("Cards")
        df_cards_filtrados["tempo_total"] = df_cards_filtrados["tempo_total"] / 3600
        st.dataframe(df_cards_filtrados, hide_index=True)


if __name__ == "__main__":
    main()
