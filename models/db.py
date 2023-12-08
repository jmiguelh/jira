from datetime import datetime
from pony.orm import *


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


db.bind(provider="sqlite", filename="../data/db.sqlite", create_db=True)

db.generate_mapping(create_tables=True)
