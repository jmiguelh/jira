import os
from dotenv import load_dotenv
from atlassian import Jira
import pprint

load_dotenv()

jira = Jira(
    url=os.getenv("BASE_URL"),
    username=os.getenv("JIRA_EMAIL"),
    password=os.getenv("API_KEY"),
    cloud=True,
)


jql_request = "PROJECT IN (SFS) and type not in (subTaskIssueTypes(),Epic) AND status != Cancelled AND key != SFS-272 and status != Reprovado"
issues = jira.jql(
    jql_request,
)
pprint.pprint(issues)
