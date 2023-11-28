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
            card["fields"]["parent"]["fields"]["summary"] if "parent" in card else "",
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
                "Tipo de item": card["fields"]["issuetype"]["name"],
                "Chave": card["key"],
                "Resumo": card["fields"]["summary"],
                "Prioridade": card["fields"]["priority"]["name"],
                "Status": card["fields"]["status"]["name"],
                "Criado": card["fields"]["created"],
                "Atualizado": card["fields"]["updated"],
                "Epico": card["fields"]["parent"]["fields"]["summary"]
                if "parent" in card
                else "",
                "Controle de tempo": card["fields"]["timespent"],
                "Categoria do status": card["fields"]["status"]["statusCategory"][
                    "name"
                ],
                "Categoria do status alterada": card["fields"][
                    "statuscategorychangedate"
                ],
            }
        )


if __name__ == "__main__":
    inserir_db(carrega_jira())

# jira.issue_worklog()
