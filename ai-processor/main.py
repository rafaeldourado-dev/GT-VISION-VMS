import os
import time
import threading
from typing import List, Dict

# CORREÇÃO: Importar apenas a classe APIClient
from api_client import APIClient
from detection import process_camera_stream

def main():
    """
    Função principal que busca câmeras da API e inicia o processamento para cada uma.
    """
    api_base_url = os.getenv("API_BASE_URL", "http://backend:8000/api")
    admin_api_key = os.getenv("ADMIN_API_KEY")

    if not admin_api_key:
        print("Erro: A variável de ambiente ADMIN_API_KEY não está definida.")
        return

    # CORREÇÃO: Criar uma instância do APIClient
    api_client = APIClient(base_url=api_base_url, api_key=admin_api_key)

    # Esperar que a API do backend esteja disponível
    while not api_client.is_api_available():
        print(f"A aguardar pela API em {api_base_url}/health...")
        time.sleep(5)
    print("API está disponível!")

    # CORREÇÃO: Chamar o método get_cameras() a partir da instância
    cameras = api_client.get_cameras()

    if not cameras:
        print("Nenhuma câmera encontrada para processar.")
        return

    threads: List[threading.Thread] = []
    for camera in cameras:
        if camera.get('is_active'):
            print(f"A iniciar o processamento para a câmera: {camera.get('name')} ({camera.get('rtsp_url')})")
            
            # Inicia uma thread separada para cada câmera ativa
            thread = threading.Thread(
                target=process_camera_stream,
                args=(camera, api_client),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        else:
            print(f"Câmera inativa, a ignorar: {camera.get('name')}")

    # Manter o script principal a correr enquanto as threads de processamento estiverem ativas
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()