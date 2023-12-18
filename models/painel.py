from datetime import datetime
from pony.orm import *
import pandas as pd


db = Database()


@db_session
def total_cards() -> int:
    sql = "select count(1) from jira_card where status_agrupado <> 'Cancelado'"
    result = db.select(sql)
    return result[0]


@db_session
def cards_aberto_ultimo_dia() -> int:
    sql = "select count(1) from jira_card where status_agrupado <> 'Cancelado' and criado > date('now','-1 day')"
    result = db.select(sql)
    return result[0]


@db_session
def cards_aberto_no_mes() -> int:
    sql = "select count(1) from jira_card where status_agrupado <> 'Cancelado' and criado > date('now','start of month')"
    result = db.select(sql)
    return result[0]


@db_session
def total_cards_concluidos() -> int:
    sql = """SELECT sum(quantidade)
            FROM jira_diario
            WHERE status_agrupado = 'Concluído'
            AND data = (SELECT max(data)
                        FROM jira_diario
                        WHERE data <= date('now','-1 day'))"""
    result = db.select(sql)
    return result[0]


@db_session
def cards_conluidos_ultimo_dia() -> int:
    sql = """SELECT sum(quantidade)
            FROM jira_diario
            WHERE status_agrupado = 'Concluído'
            AND data = (SELECT max(data)
                        FROM jira_diario);"""

    result = db.select(sql)
    return total_cards_concluidos() - result[0]


@db_session
def cards_concludos_no_mes() -> int:
    sql = """SELECT sum(quantidade)
            FROM jira_diario
            WHERE status_agrupado = 'Concluído'
            AND data = (SELECT min(data)
                        FROM jira_diario
                        WHERE data > date('now','start of month'));"""
    result = db.select(sql)
    return total_cards_concluidos() - result[0]


@db_session
def cards_por_mes():
    sql = """SELECT strftime('%Y-%m',criado), 
            sum(CASE
                WHEN tipo_agrupado = "Evolutivo" THEN 1
                ELSE 0
            END) AS Evolutivo,
            sum(CASE
                WHEN tipo_agrupado = "Corretivo" THEN 1
                ELSE 0
            END) AS Corretivo
            FROM jira_card
            WHERE status_agrupado <> 'Cancelado'
            GROUP BY strftime('%Y-%m',criado)
            ORDER BY 1 DESC
            LIMIT 6"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=["Mês", "Evolutivo", "Corretivo"],
    )
    df = df.set_index("Mês")
    return df


@db_session
def cards_por_setor():
    sql = """SELECT pai, count(1)
            FROM jira_card
            WHERE status_agrupado <> 'Cancelado'
            GROUP BY pai"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=["Setor", "Quantidade"],
    )
    return df


@db_session
def cards_por_setor_status():
    sql = """SELECT pai, 
            sum(CASE
                WHEN tipo_agrupado = "Evolutivo" THEN 1
                ELSE 0
            END) AS Evolutivo,
            sum(CASE
                WHEN tipo_agrupado = "Corretivo" THEN 1
                ELSE 0
            END) AS Corretivo
            FROM jira_card
            WHERE status_agrupado <> 'Cancelado'
            GROUP BY pai"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=["Setor", "Evolutivo", "Corretivo"],
    )
    df = df.set_index("Setor")
    return df


db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping(create_tables=True)
