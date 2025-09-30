import logging

# --- Funções de Alerta (Requerem configuração externa) ---
# Você precisará de serviços como SendGrid/SMTP para email ou Twilio para WhatsApp

def enviar_alerta_email(assunto, corpo):
    """Placeholder para enviar um alerta por email."""
    logging.info(f"ALERTA EMAIL (Simulado): Assunto: {assunto} | Corpo: {corpo}")
    # Aqui entraria a lógica de envio de email (ex: usando smtplib)
    pass

def enviar_alerta_whatsapp(mensagem):
    """Placeholder para enviar um alerta por WhatsApp."""
    logging.info(f"ALERTA WHATSAPP (Simulado): Mensagem: {mensagem}")
    # Aqui entraria a lógica de envio via API (ex: Twilio)
    pass

# --- Lógica de Processamento de Falhas ---
def processar_falhas(linhas_de_log_com_falha):
    """
    Processa uma lista de falhas do log e decide se dispara um alarme.
    """
    if not linhas_de_log_com_falha:
        return

    num_falhas = len(linhas_de_log_com_falha)
    relatorio = "\n".join(linhas_de_log_com_falha)
    
    # Lógica de decisão simples
    if num_falhas > 0:
        grau_falha = "Baixo"
        if num_falhas > 5:
            grau_falha = "Médio"
        if num_falhas > 10:
            grau_falha = "Alto"

        assunto = f"Alerta de Falha no AI-Processor - Grau: {grau_falha}"
        corpo = f"""
        Foram detectadas {num_falhas} falhas no sistema.
        
        Grau de Risco: {grau_falha}
        
        Logs relevantes:
        {relatorio}
        """
        
        # Envia os alertas
        enviar_alerta_email(assunto, corpo)
        enviar_alerta_whatsapp(f"Alerta de Falha Grau {grau_falha} no AI-Processor. Verifique os logs.")