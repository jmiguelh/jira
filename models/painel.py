from pony.orm import Database, db_session  
import pandas as pd


db = Database()


@db_session
def carregar_cards() -> pd.DataFrame:
    sql = """SELECT c.id, c.chave, tipo, desricao, prioridade, status, criado, 
                alterado, pai, tempo_total, categoria, categoria_alterada, 
                status_agrupado, tipo_agrupado, max(s.datahora) as DataUltStatus,
                CAST ((JulianDay('now') - JulianDay(max(s.datahora)))  As Integer) as DiasUltStatus
            FROM jira_card as c
            LEFT JOIN jira_status as s
            ON c.chave = s.chave
            WHERE status_agrupado not in ('Cancelado', 'Systextil')
            GROUP BY c.id, c.chave, tipo, desricao, prioridade, status, criado, 
                alterado, pai, tempo_total, categoria, categoria_alterada, 
                status_agrupado, tipo_agrupado """
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "id",
            "chave",
            "tipo",
            "descricao",
            "prioridade",
            "status",
            "criado",
            "alterado",
            "pai",
            "tempo_total",
            "categoria",
            "categoria_alterada",
            "status_agrupado",
            "tipo_agrupado",
            "DataUltStatus",
            "DiasUltStatus",
        ],
    )
    df = df.set_index("id")
    return df


@db_session
def carregar_apropriacao() -> pd.DataFrame:
    sql = """SELECT a.card_id,
                    sum(a.tempo) as apropriacao
                FROM jira_apropriacao as a 
                WHERE a.inicio > date('now', '-15 day') 
                GROUP BY a.card_id;"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "id",
            "apropriacao",
        ],
    )
    df = df.set_index("id")
    return df


@db_session
def carregar_prioridade() -> pd.DataFrame:
    sql = """SELECT chave, ordem
            FROM jira_prioridade;"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "chave",
            "ordem",
        ],
    )
    df = df.set_index("chave")
    return df


@db_session
def total_cards() -> int:
    sql = "select count(1) from jira_card where status_agrupado not in ('Cancelado', 'Systextil')"
    result = db.select(sql)
    return result[0]


@db_session
def cards_aberto_ultimo_dia() -> int:
    sql = "select count(1) from jira_card where status_agrupado not in ('Cancelado', 'Systextil') and criado > date('now','-1 day')"
    result = db.select(sql)
    return result[0]


@db_session
def cards_aberto_no_mes() -> int:
    sql = "select count(1) from jira_card where status_agrupado not in ('Cancelado', 'Systextil') and criado > date('now','start of month')"
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
def cards_por_mes() -> pd.DataFrame:
    sql = """SELECT strftime('%Y-%m',criado) as Mês, 
                tipo_agrupado,
                sum(1) AS Cards
            FROM jira_card
            WHERE status_agrupado not in ('Cancelado', 'Systextil')
                AND criado > date(date('now','start of month'),'-5 month')
            GROUP BY strftime('%Y-%m',criado), tipo_agrupado
            ORDER BY 1 DESC"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=["Mês", "Tipo", "Cards"],
    )
    # df = df.set_index("Mês")
    return df


@db_session
def cards_concluido_por_mes() -> pd.DataFrame:
    sql = """SELECT strftime('%Y-%m',data_conclusao), 
                tipo_agrupado,
                sum(1) AS Cards
            FROM jira_vw_data_conclusao
            WHERE data_conclusao > date(date('now','start of month'),'-5 month')
            GROUP BY strftime('%Y-%m',data_conclusao), tipo_agrupado
            ORDER BY 1 DESC"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=["Mês", "Tipo", "Cards"],
    )
    # df = df.set_index("Mês")
    return df


@db_session
def cards_por_setor() -> pd.DataFrame:
    sql = """SELECT pai, count(1)
            FROM jira_card
            WHERE status_agrupado not in ('Cancelado', 'Systextil')
            GROUP BY pai"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=["Setor", "Quantidade"],
    )
    return df


@db_session
def cards_concluido_por_mes_setor() -> pd.DataFrame:
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
def cards_por_setor_status() -> pd.DataFrame:
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
            WHERE status_agrupado not in ('Cancelado', 'Systextil')
            GROUP BY pai"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=["Setor", "Evolutivo", "Corretivo"],
    )
    df = df.set_index("Setor")
    return df


@db_session
def apropriacao_por_tipo() -> pd.DataFrame:
    sql = """SELECT strftime('%Y-%m',inicio) as Mes, 
                cast((cast(sum(CASE
                    WHEN tipo_agrupado = "Evolutivo" THEN tempo
                    ELSE 0
                END) as float) / cast(sum(tempo) as float))* 100 as int) AS Evolutivo,
                cast((cast(sum(CASE
                    WHEN tipo_agrupado = "Corretivo" THEN tempo
                    ELSE 0
                END) as float) / cast(sum(tempo)as float))* 100 as int) AS Corretivo,
                cast((cast(sum(CASE
                    WHEN tipo_agrupado = "Suporte" THEN tempo
                    ELSE 0
                END) as float) / cast(sum(tempo)as float))* 100 as int) AS Suporte
            FROM jira_card as c
            INNER JOIN jira_apropriacao as a 
            ON c.id = a.card_id
            WHERE c.status_agrupado not in ('Cancelado', 'Systextil')
            GROUP BY strftime('%Y-%m',inicio)
            ORDER BY 1 DESC
            LIMIT 6"""
    result = db.select(sql)
    df = pd.DataFrame(result, columns=["Mês", "Evolutivo", "Corretivo", "Suporte"])
    # df = df.set_index("Mes")
    return df


@db_session
def apropriacao_por_pai() -> pd.DataFrame:
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
                WHERE c.status_agrupado not in ('Cancelado', 'Systextil')
                  AND c.tipo <> "Suporte"
                GROUP BY strftime('%Y-%m',inicio)
                ORDER BY 1 DESC
                LIMIT 6"""
    result = db.select(sql)
    df = pd.DataFrame(result, columns=["Mês", "CRL", "Têxtil", "Comercial"])
    # df = df.set_index("Mes")
    return df


@db_session
def diario_por_status() -> pd.DataFrame:
    sql = """SELECT data, status_agrupado, sum(quantidade)
            FROM jira_diario
            GROUP BY data, status_agrupado
            HAVING status_agrupado not in('Concluído','Cancelado','Systextil')
            AND data > date('now','-30 days');"""
    result = db.select(sql)
    df = pd.DataFrame(result, columns=["Data", "Status", "Cards"])
    df = df.replace(
        {
            "Backlog": "1- Baclog",
            "Especificação": "2 - Especif.",
            "Desenvolvimento": "3 - Desenv.",
            "Homologação": "4 - Homolog.",
            "Produção": "5 - Prod.",
        }
    )
    df = df.sort_values(by=["Status"])
    return df


@db_session
def diario(dias: int = 0) -> pd.DataFrame:
    where = f" WHERE data <= date('now','-{dias} day')" if dias > 0 else ""
    sql = f"""SELECT status_agrupado, pai,  tipo_agrupado, quantidade 
            FROM jira_diario
            WHERE data = (SELECT max(data) FROM jira_diario{where})
            AND status_agrupado NOT in ('Cancelado', 'Concluído', 'Backlog','Systextil')"""
    result = db.select(sql)
    df = pd.DataFrame(result, columns=["Status", "Setor", "Tipo", "Quantidade"])
    df = df.replace(
        {
            "Especificação": "1 - Especificação",
            "Desenvolvimento": "2 - Desenvolvimento",
            "Homologação": "3 - Homologação",
            "Produção": "4 - Produção",
        }
    )
    return df


@db_session
def total_cards_tipo(dias: int = 0) -> pd.DataFrame:
    sql = f"""SELECT tipo_agrupado, SUM(quantidade)
                FROM jira_diario
                WHERE data = (SELECT max(data) FROM jira_diario WHERE data <= date('now','-{dias} day'))
                AND status_agrupado NOT in ('Cancelado', 'Concluído','Systextil')
                GROUP BY tipo_agrupado;
            """
    result = db.select(sql)
    df = pd.DataFrame(result, columns=["Tipo", "Quantidade"])
    df = df.set_index("Tipo")
    return df


@db_session
def carregar_tempo() -> pd.DataFrame:
    sql = """SELECT a.chave,
                a.de AS status,
                CAST ( (
                    SELECT JULIANDAY(a.datahora) - JULIANDAY(b.datahora) 
                        FROM jira_status AS b
                        WHERE a.chave = b.chave AND 
                            b.id < a.id
                        ORDER BY b.id
                        LIMIT 1
                )
                AS INT) AS tempo
            FROM jira_status AS a;"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "chave",
            "status",
            "tempo",
        ],
    )
    return df


@db_session
def carregar_lead_time() -> pd.DataFrame:
    sql = """SELECT chave,
                tipo_agrupado,
                CAST(JULIANDAY(fim) - JULIANDAY(inicio) AS INT) as leadtime
            FROM jira_vw_lead_time
            WHERE inicio NOT NULL
            ORDER BY leadtime"""
    result = db.select(sql)
    df = pd.DataFrame(
        result,
        columns=[
            "chave",
            "tipo",
            "leadtime",
        ],
    )
    return df


def trata_lead_time(df: pd.DataFrame) -> pd.DataFrame:
    df = df["leadtime"].value_counts().to_frame().sort_index().reset_index()
    df["acumulado"] = df["count"].cumsum()
    return df


def pecent_lead_time(df: pd.DataFrame, pecentual: float) -> int:
    return (
        df.loc[df.acumulado < (df["count"].sum() * pecentual)]
        .tail(1)["leadtime"]
        .values[0]
    )


db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping(create_tables=True)
