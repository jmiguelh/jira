import os
from dotenv import load_dotenv
from atlassian import Jira
from tinydb import TinyDB, Query


def carrega_jira() -> dict:
    load_dotenv()

    jira = Jira(
        url=os.getenv("BASE_URL"),
        username=os.getenv("JIRA_EMAIL"),
        password=os.getenv("API_KEY"),
        cloud=True,
    )

    jql_request = "PROJECT IN (SFS) and type not in (subTaskIssueTypes(),Epic) AND status != Cancelled AND key != SFS-272 and status != Reprovado"

    cards = []
    inicio = 0
    passo = 100
    total = 1000
    while inicio < total:
        issues = jira.jql(jql_request, limit=passo, start=inicio)
        inicio = issues["startAt"] + passo
        total = issues["total"]
        cards.extend(issues["issues"])
    return cards


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
    db = TinyDB("data/db.json")
    db.truncate()
    for card in cards:
        db.insert(
            {
                "tipo de item": card["fields"]["issuetype"]["name"],
                "chave": card["key"],
                "resumo": card["fields"]["summary"],
                "prioridade": card["fields"]["priority"]["name"],
                "status": card["fields"]["status"]["name"],
                "status_agrupado": card["fields"]["status"]["description"],
                "criado": card["fields"]["created"],
                "atualizado": card["fields"]["updated"],
                "epico": card["fields"]["parent"]["fields"]["summary"]
                if "parent" in card["fields"]
                else None,
                "tempo": card["fields"]["timespent"],
                "categoria": card["fields"]["status"]["statusCategory"]["name"],
                "categoria_alterada": card["fields"]["statuscategorychangedate"],
            }
        )


if __name__ == "__main__":
    cards = carrega_jira()
    inserir_db(cards)

# jira.issue_worklog()
