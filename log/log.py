import logging
import logging.config

logging.config.fileConfig("log/logging.conf", disable_existing_loggers=False)


def logar(Nome: "str", Mensagem: "str"):
    logger = logging.getLogger(Nome)
    logger.info(Mensagem)
