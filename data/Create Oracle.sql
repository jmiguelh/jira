CREATE TABLE "jira_apropriacao" (
  "ID" NUMBER(10) PRIMARY KEY,
  "CARD_ID" NUMBER(10) NOT NULL,
  "INICIO" TIMESTAMP NOT NULL,
  "TEMPO" NUMBER(10) NOT NULL,
  "NOME" VARCHAR2(150 CHAR) NOT NULL,
  "ALTERADO" TIMESTAMP NOT NULL
);

CREATE TABLE "jira_card" (
  "ID" NUMBER(10) PRIMARY KEY,
  "CHAVE" VARCHAR2(10 CHAR) NOT NULL,
  "TIPO" VARCHAR2(50 CHAR) NOT NULL,
  "DESRICAO" VARCHAR2(1000 CHAR),
  "PRIORIDADE" VARCHAR2(20 CHAR),
  "STATUS" VARCHAR2(50 CHAR) NOT NULL,
  "CRIADO" TIMESTAMP,
  "ALTERADO" TIMESTAMP,
  "PAI" VARCHAR2(20 CHAR),
  "TEMPO_TOTAL" NUMBER,
  "CATEGORIA" VARCHAR2(50 CHAR),
  "CATEGORIA_ALTERADA" TIMESTAMP,
  "STATUS_AGRUPADO" VARCHAR2(100 CHAR),
  "TIPO_AGRUPADO" VARCHAR2(50 CHAR)
);

CREATE TABLE "jira_status" (
  "ID" NUMBER(10) PRIMARY KEY,
  "CHAVE" VARCHAR2(10 CHAR) NOT NULL,
  "DE" VARCHAR2(50 CHAR) NOT NULL,
  "PARA" VARCHAR2(50 CHAR) NOT NULL,
  "DATAHORA" TIMESTAMP NOT NULL
)