from datetime import datetime
from pony.orm import Database, PrimaryKey, Required, Optional, db_session, commit

db = Database()


class Card(db.Entity):
    _table_ = "jira_card"
    id = PrimaryKey(int)
    chave = Required(str, 10)
    tipo = Required(str, 50)
    desricao = Optional(str)
    prioridade = Optional(str, 20)
    status = Required(str, 50)
    criado = Optional(datetime)
    alterado = Optional(datetime)
    pai = Optional(str, 20)
    tempo_total = Optional(float)
    categoria = Optional(str, 50)
    categoria_alterada = Optional(datetime)
    status_agrupado = Optional(str, 100)
    tipo_agrupado = Optional(str, 50)


class Apropriacao(db.Entity):
    _table_ = "jira_apropriacao"
    id = PrimaryKey(int)
    card_id = Required(int)
    inicio = Required(datetime)
    tempo = Required(int)
    nome = Required(str, 150)
    alterado = Required(datetime)


class Status(db.Entity):
    _table_ = "jira_status"
    id = PrimaryKey(int)
    chave = Required(str, 10)
    de = Required(str, 50)
    para = Required(str, 50)
    datahora = Required(datetime)


class Controle(db.Entity):
    _table_ = "jira_controle"
    atualizacao = Optional(datetime)


@db_session
def ultima_atualzacao() -> datetime:
    c = Controle.get(id=1)
    return c.atualizacao.strftime("%d/%m/%Y %H:%M:%S")


@db_session
def diario():
    sql = """
        DELETE FROM jira_diario
        WHERE  data = DATE('now');
        """
    db.execute(sql)
    commit()
    sql = """
        INSERT INTO jira_diario
        SELECT DATE('now') as data, status_agrupado, pai, tipo_agrupado, count(*) as quatidade
        FROM jira_card
        GROUP BY status_agrupado, pai, tipo_agrupado
        """
    db.execute(sql)


class Prioridade(db.Entity):
    _table_ = "jira_prioridade"
    chave = PrimaryKey(str, 10, auto=True)
    ordem = Required(int, default=0)


# result = db.select("select * from jira_card where status_agrupado <> 'Cancelado'")
# colunas = ['id', 'chave', 'tipo', 'desricao', 'prioridade', 'status', 'criado', 'alterado', 'pai', 'tempo_total', 'categoria', 'categoria_alterada', 'status_agrupado', 'tipo_agrupado']
# a = pd.DataFrame(resultcolumns=colunas)


db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping(create_tables=True)
