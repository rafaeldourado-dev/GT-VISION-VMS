import logging

def send_blacklist_alert_email(vehicle_sighting: dict):
    """
    Função temporária (placeholder) para lidar com alertas de email.
    TODO: Implementar a lógica real de envio de email aqui.
    """
    plate = vehicle_sighting.get('license_plate', 'N/A')
    logging.warning(f"Alerta de email (AINDA NÃO IMPLEMENTADO) para a placa: {plate}")
    print(f"Placeholder: Enviando alerta de blacklist para {plate}")
    pass