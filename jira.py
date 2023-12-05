import os
from dotenv import load_dotenv
from atlassian import Jira
from models.db import *
from datetime import datetime

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
    return cards


def carrega_apropriacoes():
    jira = Jira(
        url=os.getenv("BASE_URL"),
        username=os.getenv("JIRA_EMAIL"),
        password=os.getenv("API_KEY"),
        cloud=True,
    )

    apropriacoes = jira.get_updated_worklogs(since=1701399600)

    fim = apropriacoes["lastPage"]
    proxima = apropriacoes["until"] + 1
    ids = []
    for apropriacao in apropriacoes["values"]:
        ids.append(apropriacao["worklogId"])

    apropriacoes = jira.get_worklogs(ids)

    for apropriacao in apropriacoes:
        ...
        # apropriacao["Id"]
        # apropriacao["issueId"]
        # apropriacao["started"]
        # apropriacao["timeSpentSeconds"]
        # apropriacao["author"]["displayName"]


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


def inserir_db(cards: "dict"):
    with db_session:
        for card in cards:
            c = Card.get(id=card["id"])
            if not c == None:
                if not c.alterado == datetime.strptime(
                    card["fields"]["updated"][:19], FORMATO_DATA
                ):
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

            else:
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


if __name__ == "__main__":
    cards = carrega_cards()
    inserir_db(cards)
