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
    sql = """SELECT count(1)
            FROM jira_card
            WHERE status_agrupado = 'Concluído'"""
    result = db.select(sql)
    return result[0]


@db_session
def cards_conluidos_ultimo_dia() -> int:
    sql = """SELECT count(1)
            FROM jira_vw_data_conclusao
            WHERE data_conclusao > date('now','-1 day')"""
    result = db.select(sql)
    return result[0]


@db_session
def cards_concludos_no_mes() -> int:
    sql = """SELECT count(1)
            FROM jira_vw_data_conclusao
            WHERE data_conclusao > date('now','start of month');"""
    result = db.select(sql)
    return result[0]


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
    # df = df.set_index("Mês")
    return df


@db_session
def cards_concluido_por_mes():
    sql = """SELECT strftime('%Y-%m',data_conclusao), 
            sum(CASE
                WHEN tipo_agrupado = "Evolutivo" THEN 1
                ELSE 0
            END) AS Evolutivo,
            sum(CASE
                WHEN tipo_agrupado = "Corretivo" THEN 1
                ELSE 0
            END) AS Corretivo
            FROM jira_vw_data_conclusao
            GROUP BY strftime('%Y-%m',data_conclusao)
            ORDER BY 1 DESC
            LIMIT 6"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=["Mês", "Evolutivo", "Corretivo"],
    )
    # df = df.set_index("Mês")
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
def cards_concluido_por_mes_setor():
    sql = """SELECT pai, count(1)
            FROM jira_vw_data_conclusao
            WHERE data_conclusao > date('now','start of month')
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


@db_session
def apropriacao_por_tipo():
    sql = """SELECT strftime('%Y-%m',inicio) as Mes, 
                cast((cast(sum(CASE
                    WHEN tipo_agrupado = "Evolutivo" THEN tempo
                    ELSE 0
                END) as float) / cast(sum(tempo) as float))* 100 as int) AS Evolutivo,
                cast((cast(sum(CASE
                    WHEN tipo_agrupado = "Corretivo" THEN tempo
                    ELSE 0
                END) as float) / cast(sum(tempo)as float))* 100 as int) AS Corretivo
            FROM jira_card as c
            INNER JOIN jira_apropriacao as a 
            ON c.id = a.card_id
            WHERE c.status_agrupado <> 'Cancelado'
            GROUP BY strftime('%Y-%m',inicio)
            ORDER BY 1 DESC
            LIMIT 6"""
    result = db.select(sql)
    df = pd.DataFrame(result, columns=["Mês", "Evolutivo", "Corretivo"])
    # df = df.set_index("Mes")
    return df


@db_session
def apropriacao_por_pai():
    sql = """SELECT strftime('%Y-%m',inicio) as Mes, 
                    cast((cast(sum(CASE
                        WHEN pai = "CRL" THEN tempo
                        ELSE 0
                    END) as float) / cast(sum(tempo) as float))* 100 as int) AS CRL,
                    cast((cast(sum(CASE
                        WHEN pai = "Têxtil" THEN tempo
                        ELSE 0
                    END) as float) / cast(sum(tempo)as float))* 100 as int) AS Têxtil,
                    cast((cast(sum(CASE
                        WHEN pai = "Comercial" THEN tempo
                        ELSE 0
                    END) as float) / cast(sum(tempo)as float))* 100 as int) AS Têxtil
                FROM jira_card as c
                INNER JOIN jira_apropriacao as a 
                ON c.id = a.card_id
                WHERE c.status_agrupado <> 'Cancelado'
                GROUP BY strftime('%Y-%m',inicio)
                ORDER BY 1 DESC
                LIMIT 6"""
    result = db.select(sql)
    df = pd.DataFrame(result, columns=["Mês", "CRL", "Têxtil", "Comercial"])
    # df = df.set_index("Mes")
    return df


@db_session
def diario_por_status():
    sql = """SELECT data, status_agrupado, sum(quantidade)
            FROM jira_diario
            GROUP BY data, status_agrupado
            HAVING status_agrupado not in('Concluído','Cancelado','Systextil')
            AND data > date('now','-30 days');"""
    result = db.select(sql)
    df = pd.DataFrame(result, columns=["Data", "Status", "Cards"])
    return df


db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping(create_tables=True)
