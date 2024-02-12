import schedule
import time
import jira
from datetime import datetime


def agendamento():
    # Verificar se hoje é um dia útil (segunda a sexta-feira)
    hoje = datetime.now()
    if hoje.weekday() < 5:  # 0 é segunda-feira, 4 é sexta-feira
        jira.carregar()


schedule.every().day.at("08:00").do(agendamento)
schedule.every().day.at("20:00").do(agendamento)

while True:
    schedule.run_pending()
    time.sleep(1)
