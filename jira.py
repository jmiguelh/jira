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

# jira.issue_worklog()
