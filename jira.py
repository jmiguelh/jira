import os
from dotenv import load_dotenv
from atlassian import Jira
from datetime import datetime
import time
from models.db import *
import log.log as log

FORMATO_DATA = "%Y-%m-%dT%H:%M:%S"

load_dotenv()


def carrega_cards() -> dict:
    jira = Jira(
        url=os.getenv("BASE_URL"),
        username=os.getenv("JIRA_EMAIL"),
        password=os.getenv("API_KEY"),
        cloud=True,
    )

    jql_request = "PROJECT IN (SFS) and type not in (subTaskIssueTypes(),Epic) AND status != Cancelled AND key != SFS-272 and status != Reprovado"

    cards = []
    campos = [
        "issueId",
        "issuetype",
        "summary",
        "priority",
        "status",
        "created",
        "updated",
        "parent",
        "timespent",
        "statuscategorychangedate",
    ]
    inicio = 0
    passo = 100
    total = 1000
    while inicio < total:
        issues = jira.jql(
            jql_request,
            limit=passo,
            start=inicio,
            fields=campos,
        )
        inicio = issues["startAt"] + passo
        total = issues["total"]
        cards.extend(issues["issues"])
    log.logar("CARD", f"Total de cards: {total}")
    return cards


def carrega_apropriacoes() -> dict:
    jira = Jira(
        url=os.getenv("BASE_URL"),
        username=os.getenv("JIRA_EMAIL"),
        password=os.getenv("API_KEY"),
        cloud=True,
    )

    with db_session:
        ultima = time.mktime(max(a.alterado for a in Apropriacao).timetuple())

    apropriacoes = jira.get_updated_worklogs(since=ultima + 1)

    ids = []
    for apropriacao in apropriacoes["values"]:
        ids.append(apropriacao["worklogId"])

    apropriacoes = jira.get_worklogs(ids)

    return apropriacoes


def carrega_status(chave: "str"):
    jira = Jira(
        url=os.getenv("BASE_URL"),
        username=os.getenv("JIRA_EMAIL"),
        password=os.getenv("API_KEY"),
        cloud=True,
    )
    status = jira.get_issue_changelog(chave, limit=5000)

    for s in status["histories"]:
        if s["items"][0]["field"] == "status":
            inserir_db_status(
                s["id"],
                chave,
                s["items"][0]["fromString"],
                s["items"][0]["toString"],
                s["created"],
            )


def listar_cards(cards: "dict"):
    i = 0
    for card in cards:
        i += 1
        print(
            i,
            card["fields"]["issuetype"]["name"],
            card["key"],
            card["fields"]["summary"],
            card["fields"]["priority"]["name"],
            card["fields"]["status"]["name"],
            card["fields"]["created"],
            card["fields"]["updated"],
            card["fields"]["parent"]["fields"]["summary"]
            if "parent" in card["fields"]
            else "",
            card["fields"]["timespent"],
            card["fields"]["status"]["statusCategory"]["name"],
            card["fields"]["statuscategorychangedate"],
        )


def inserir_db_cards(cards: "dict"):
    with db_session:
        for card in cards:
            c = Card.get(id=card["id"])
            if not c == None:
                if not c.alterado == datetime.strptime(
                    card["fields"]["updated"][:19], FORMATO_DATA
                ):
                    # Atualiza campos
                    log.logar("CARD", f"Card alterado: {c.card}")
                    c.tipo = card["fields"]["issuetype"]["name"]
                    c.desricao = card["fields"]["summary"]
                    c.prioridade = card["fields"]["priority"]["name"]
                    c.status = card["fields"]["status"]["name"]
                    c.status_agrupado = card["fields"]["status"]["description"]
                    c.alterado = datetime.strptime(
                        card["fields"]["updated"][:19], FORMATO_DATA
                    )
                    c.pai = (
                        card["fields"]["parent"]["fields"]["summary"]
                        if "parent" in card["fields"]
                        else ""
                    )
                    c.tempo_total = card["fields"]["timespent"]
                    c.categoria = (
                        card["fields"]["status"]["statusCategory"]["name"]
                        if not card["fields"]["status"]["name"] == "Concluído"
                        else "Concluído"
                    )
                    c.categoria_alterada = datetime.strptime(
                        card["fields"]["statuscategorychangedate"][:19], FORMATO_DATA
                    )
                    # Busca status
                    carrega_status(c.chave)
            else:
                # Inser novo card
                log.logar("CARD", f"Card inserido: {card['key']}")
                Card(
                    id=card["id"],
                    tipo=card["fields"]["issuetype"]["name"],
                    chave=card["key"],
                    desricao=card["fields"]["summary"],
                    prioridade=card["fields"]["priority"]["name"],
                    status=card["fields"]["status"]["name"],
                    status_agrupado=card["fields"]["status"]["description"],
                    criado=datetime.strptime(
                        card["fields"]["created"][:19], FORMATO_DATA
                    ),
                    alterado=datetime.strptime(
                        card["fields"]["updated"][:19], FORMATO_DATA
                    ),
                    pai=card["fields"]["parent"]["fields"]["summary"]
                    if "parent" in card["fields"]
                    else "",
                    tempo_total=card["fields"]["timespent"],
                    categoria=card["fields"]["status"]["statusCategory"]["name"]
                    if not card["fields"]["status"]["name"] == "Concluído"
                    else "Concluído",
                    categoria_alterada=datetime.strptime(
                        card["fields"]["statuscategorychangedate"][:19], FORMATO_DATA
                    ),
                )
                # Busca status
                carrega_status(card["key"])


def inserir_db_apropriacoes(apropriacoes: "dict"):
    with db_session:
        for apropriacao in apropriacoes:
            log.logar("APROPRIAÇÃO", f"Apropriação inserida: {apropriacao['issueId']}")
            Apropriacao(
                id=apropriacao["id"],
                card_id=apropriacao["issueId"],
                inicio=datetime.strptime(apropriacao["started"][:19], FORMATO_DATA),
                tempo=apropriacao["timeSpentSeconds"],
                nome=apropriacao["author"]["displayName"],
                alterado=datetime.strptime(apropriacao["updated"][:19], FORMATO_DATA),
            )


def inserir_db_status(id: "int", chave: "str", de: "str", para: "str", datahora: "str"):
    with db_session:
        s = Status.get(id=id)
        if s == None:
            log.logar("STATUS", f"Status alterado: {chave}")
            Status(
                id=id,
                chave=chave,
                de=de,
                para=para,
                datahora=datetime.strptime(datahora[:19], FORMATO_DATA),
            )


if __name__ == "__main__":
    log.logar("MAIN", "Início do processo")
    log.logar("MAIN", "Início Cards")
    inserir_db_cards(carrega_cards())
    log.logar("MAIN", "Início Apropriação")
    inserir_db_apropriacoes(carrega_apropriacoes())
    log.logar("MAIN", "Fim do Processo")
