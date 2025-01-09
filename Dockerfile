# Usar a imagem mais leve de Python na versão 3.12
FROM python:3.12-slim

# Configurar variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \ 
    PYTHONUNBUFFERED=1
# Configurar o timezone para São Paulo
ENV TZ=America/Sao_Paulo
# Atualizar pacotes do sistema e instalar dependências necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Configurar diretório de trabalho
WORKDIR /app

# Clonar o repositório do GitHub
# Utilizando autenticação com token armazenado como ARG
ARG GITHUB_TOKEN
RUN git clone https://$GITHUB_TOKEN@github.com/jmiguelh/jira.git /app

# Instalar dependências do projeto
RUN pip3 install -r requirements.txt

EXPOSE 9000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:9000/_stcore/health || exit 1

# Comando padrão para executar o aplicativo
ENTRYPOINT ["streamlit", "run", "/app/app.py", "--server.port=9000", "--server.address=0.0.0.0"]
