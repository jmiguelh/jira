CREATE TABLE "jira_apropriacao" (
  "id" INTEGER NOT NULL PRIMARY KEY,
  "card_id" INTEGER NOT NULL,
  "inicio" DATETIME NOT NULL,
  "tempo" INTEGER NOT NULL,
  "nome" VARCHAR(150) NOT NULL,
  "alterado" DATETIME NOT NULL
);

CREATE TABLE "jira_status" (
  "id" INTEGER NOT NULL PRIMARY KEY,
  "chave" VARCHAR(10) NOT NULL,
  "de" VARCHAR(50) NOT NULL,
  "para" VARCHAR(50) NOT NULL,
  "datahora" DATETIME NOT NULL
); 

CREATE TABLE jira_card (
    id                 INTEGER       NOT NULL
                                     PRIMARY KEY,
    chave              VARCHAR (10)  NOT NULL
                                     UNIQUE,
    tipo               VARCHAR (50)  NOT NULL,
    desricao           TEXT          NOT NULL,
    prioridade         VARCHAR (20)  NOT NULL,
    status             VARCHAR (50)  NOT NULL,
    criado             DATETIME,
    alterado           DATETIME,
    pai                VARCHAR (20)  NOT NULL,
    tempo_total        REAL,
    categoria          VARCHAR (50)  NOT NULL,
    categoria_alterada DATETIME,
    status_agrupado    VARCHAR (100) NOT NULL,
    tipo_agrupado      VARCHAR (50) 
);
