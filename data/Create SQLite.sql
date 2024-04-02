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

CREATE TABLE jira_diario (
    data           DATE,
    status_agrupado VARCHAR (100) NOT NULL,
    pai            VARCHAR (20)  NOT NULL,
    tipo_agrupado  VARCHAR (50)  NOT NULL,
    quantidade     INTEGER
);

CREATE TABLE "jira_controle" (
  "id" INTEGER PRIMARY KEY AUTOINCREMENT,
  "atualizacao" DATETIME
);

INSERT INTO jira_controle (atualizacao)
VALUES (datetime('now'));

CREATE VIEW jira_vw_data_conclusao AS
    SELECT c.chave,
           max(s.datahora) AS data_conclusao,
           c.tipo_agrupado,
           c.pai
      FROM jira_card AS c
           INNER JOIN
           jira_status AS s ON c.chave = s.chave
     WHERE status_agrupado = 'Concluído' AND 
           s.para IN ('Done', 'Concluído Systextil') 
     GROUP BY c.chave;

CREATE TABLE "jira_prioridade" (
  "chave" VARCHAR(10) NOT NULL PRIMARY KEY,
  "ordem" INTEGER NOT NULL
);

DROP VIEW jira_vw_lead_time;

CREATE VIEW jira_vw_lead_time AS
    SELECT c.chave,
           c.tipo_agrupado,
           IFNULL( (
                       SELECT max(s.datahora) 
                         FROM jira_status AS s
                        WHERE s.chave = c.chave AND 
                              s.para = "Aprovado"
                   ), (
                       SELECT min(s.datahora) 
                         FROM jira_status AS s
                        WHERE s.chave = c.chave
                   )
           ) AS inicio,
           (
               SELECT max(s.datahora) 
                 FROM jira_status AS s
                WHERE s.chave = c.chave AND 
                      s.para = "Done"
           )
           AS fim
      FROM jira_card AS c
     WHERE c.status = "Concluído";
