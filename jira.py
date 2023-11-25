import os
from dotenv import load_dotenv
from atlassian import Jira

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


i = 0
for card in cards:
    i += 1
    print(i, card["key"], card["fields"]["issuetype"]["name"])

# jira.issue_worklog()
