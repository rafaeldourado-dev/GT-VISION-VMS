import logging
import sys

LOG_FILE = "ai_processor.log"

def configurar_logging():
    """Configura o logging para salvar em ficheiro e mostrar na consola."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("Sistema de logs iniciado.")

def verificar_logs_por_violacoes(keyword="ERRO"):
    """
    Exemplo de função que varre o log em busca de palavras-chave.
    Retorna uma lista de linhas que contêm a palavra.
    """
    violacoes = []
    try:
        with open(LOG_FILE, 'r') as f:
            for line in f:
                if keyword.upper() in line.upper():
                    violacoes.append(line.strip())
    except FileNotFoundError:
        logging.warning("Ficheiro de log ainda não existe.")
    return violacoes