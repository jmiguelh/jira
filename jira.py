import os
from dotenv import load_dotenv
from atlassian import Jira
from datetime import datetime
import time
from models.db import (
    Card,
    Status,
    Apropriacao,
    Controle,
    diario,
    db_session,
    ultima_apropriacao,
)
import log.log as log

FORMATO_DATA = "%Y-%m-%dT%H:%M:%S.%f%z"

load_dotenv()


def carrega_cards() -> dict:
    jira = Jira(
        url=os.getenv("BASE_URL"),
        username=os.getenv("JIRA_EMAIL"),
        password=os.getenv("API_KEY"),
        cloud=True,
    )

    jql_request = (
        "PROJECT IN (SFS) and type not in (subTaskIssueTypes(),Epic) AND key != SFS-272"
    )

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
        ultima = time.mktime(
            datetime.strptime(
                ultima_apropriacao(), "%Y-%m-%d %H:%M:%S.%f%z"
            ).timetuple()
        )

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
    status = jira.get_issue_changelog(
        chave,
        limit=5000,
    )
    if "histories" in status:
        for s in status["histories"]:
            if (
                s["items"][0]["field"] == "status"
                or s["items"][0]["field"] == "resolution"
            ):
                inserir_db_status(
                    s["id"],
                    chave,
                    (
                        s["items"][0]["fromString"]
                        if s["items"][0]["fromString"] is not None
                        else s["items"][1]["fromString"]
                    ),
                    (
                        s["items"][0]["toString"]
                        if s["items"][0]["toString"] is not None
                        else s["items"][1]["toString"]
                    ),
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
            (
                card["fields"]["parent"]["fields"]["summary"]
                if "parent" in card["fields"]
                else ""
            ),
            card["fields"]["timespent"],
            card["fields"]["status"]["statusCategory"]["name"],
            card["fields"]["statuscategorychangedate"],
        )


def inserir_db_cards(cards: "dict"):
    with db_session(optimistic=False):
        for card in cards:
            c = Card.get(id=card["id"])
            if c is not None:
                if not c.alterado == datetime.strptime(
                    card["fields"]["updated"][:23], "%Y-%m-%dT%H:%M:%S.%f"
                ):
                    # Atualiza campos
                    log.logar("CARD", f"Card alterado: {c.chave}")
                    c.tipo = card["fields"]["issuetype"]["name"]
                    c.tipo_agrupado = agrupar_tipo(card["fields"]["issuetype"]["name"])
                    c.desricao = card["fields"]["summary"]
                    c.prioridade = card["fields"]["priority"]["name"]
                    c.status = card["fields"]["status"]["name"]
                    c.status_agrupado = agrupar_status(card["fields"]["status"]["name"])
                    c.alterado = datetime.strptime(
                        card["fields"]["updated"], FORMATO_DATA
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
                        card["fields"]["statuscategorychangedate"], FORMATO_DATA
                    )
                    # Busca status
                    carrega_status(c.chave)
                # else:
                #     c.categoria_alterada = datetime.strptime(
                #         card["fields"]["statuscategorychangedate"], FORMATO_DATA
                #     )
                #     if card["fields"]["status"]["name"] == "Concluído":
                #         carrega_status(c.chave)
            else:
                # Inser novo card
                log.logar("CARD", f"Card inserido: {card['key']}")
                Card(
                    id=card["id"],
                    tipo=card["fields"]["issuetype"]["name"],
                    tipo_agrupado=agrupar_tipo(card["fields"]["issuetype"]["name"]),
                    chave=card["key"],
                    desricao=card["fields"]["summary"],
                    prioridade=card["fields"]["priority"]["name"],
                    status=card["fields"]["status"]["name"],
                    status_agrupado=agrupar_status(card["fields"]["status"]["name"]),
                    criado=datetime.strptime(card["fields"]["created"], FORMATO_DATA),
                    alterado=datetime.strptime(card["fields"]["updated"], FORMATO_DATA),
                    pai=(
                        card["fields"]["parent"]["fields"]["summary"]
                        if "parent" in card["fields"]
                        else ""
                    ),
                    tempo_total=card["fields"]["timespent"],
                    categoria=(
                        card["fields"]["status"]["statusCategory"]["name"]
                        if not card["fields"]["status"]["name"] == "Concluído"
                        else "Concluído"
                    ),
                    categoria_alterada=datetime.strptime(
                        card["fields"]["statuscategorychangedate"], FORMATO_DATA
                    ),
                )
                # Busca status
                carrega_status(card["key"])


def inserir_db_apropriacoes(apropriacoes: "dict"):
    with db_session(optimistic=False):
        for apropriacao in apropriacoes:
            a = Apropriacao.get(id=apropriacao["id"])
            if a is not None:
                log.logar(
                    "APROPRIAÇÃO", f"Apropriação alterada: {apropriacao['issueId']}"
                )
                a.inicio = datetime.strptime(apropriacao["started"], FORMATO_DATA)
                a.tempo = apropriacao["timeSpentSeconds"]
                a.nome = apropriacao["author"]["displayName"]
                a.alterado = datetime.strptime(apropriacao["updated"], FORMATO_DATA)
            else:
                log.logar(
                    "APROPRIAÇÃO", f"Apropriação inserida: {apropriacao['issueId']}"
                )
                Apropriacao(
                    id=apropriacao["id"],
                    card_id=apropriacao["issueId"],
                    inicio=datetime.strptime(apropriacao["started"], FORMATO_DATA),
                    tempo=apropriacao["timeSpentSeconds"],
                    nome=apropriacao["author"]["displayName"],
                    alterado=datetime.strptime(apropriacao["updated"], FORMATO_DATA),
                )


def inserir_db_status(id: "int", chave: "str", de: "str", para: "str", datahora: "str"):
    with db_session:
        s = Status.get(id=id)
        if s is None:
            log.logar("STATUS", f"Status alterado: {chave}")
            Status(
                id=id,
                chave=chave,
                de=de,
                para=para,
                datahora=datetime.strptime(datahora, FORMATO_DATA),
            )


def agrupar_status(status: "str") -> str:
    match status:
        case "Aguardando Aprovação":
            retorno = "Backlog"
        case "Aguardando Chamado":
            retorno = "Systextil"
        case "Aguardando Desenvolvimento":
            retorno = "Systextil"
        case "Aprovado":
            retorno = "Especificação"
        case "Aguardando Orçamento":
            retorno = "Systextil"
        case "Em andamento":
            retorno = "Desenvolvimento"
        case "Especificação":
            retorno = "Especificação"
        case "Tarefas pendentes":
            retorno = "Desenvolvimento"
        case "Validação BA":
            retorno = "Desenvolvimento"
        case "Aguardando QA":
            retorno = "Desenvolvimento"
        case "Aguardando homologação":
            retorno = "Homologação"
        case "Homologando Systextil":
            retorno = "Systextil"
        case "Validação em QA":
            retorno = "Homologação"
        case "Aguardando PRD":
            retorno = "Produção"
        case "Concluído":
            retorno = "Concluído"
        case "Concluído Systextil":
            retorno = "Concluído"
        case "Validação em PRD":
            retorno = "Produção"
        case "Aprovação da Especificação":
            retorno = "Especificação"
        case "Homologando":
            retorno = "Homologação"
        case "Reprovar Homologação":
            retorno = "Homologação"
        case "Cancelado":
            retorno = "Cancelado"
        case "Reprovado":
            retorno = "Cancelado"
    return retorno


def agrupar_tipo(tipo: "str") -> str:
    match tipo:
        case "Ajuste":
            retorno = "Corretivo"
        case "Configuração":
            retorno = "Evolutivo"
        case "Estudo":
            retorno = "Evolutivo"
        case "Inconsistência":
            retorno = "Corretivo"
        case "Melhoria":
            retorno = "Evolutivo"
        case "Nova função":
            retorno = "Evolutivo"
        case "Suporte":
            retorno = "Suporte"
    return retorno


def atualizar():
    with db_session(optimistic=False):
        c = Controle.get(id=1)
        c.atualizacao = datetime.now()


def carregar():
    log.logar("MAIN", "Início do processo")
    log.logar("MAIN", "Início Cards")
    inserir_db_cards(carrega_cards())
    log.logar("MAIN", "Início Apropriação")
    inserir_db_apropriacoes(carrega_apropriacoes())
    log.logar("MAIN", "Início Diário")
    diario()
    atualizar()
    log.logar("MAIN", "Fim do Processo")


if __name__ == "__main__":
    carregar()
