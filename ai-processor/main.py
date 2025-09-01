import cv2
import threading
import time
import logging
from detection import LPRProcessor
from api_client import APIClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("AI-Processor")

class CameraStreamer(threading.Thread):
    def __init__(self, camera_info: dict, lpr_processor: LPRProcessor, api_client: APIClient):
        super().__init__(daemon=True)
        self.camera_info = camera_info
        self.lpr_processor = lpr_processor
        self.api_client = api_client
        self.is_running = True

    def run(self):
        camera_id = self.camera_info['id']
        rtsp_url = self.camera_info['rtsp_url']
        logger.info(f"A iniciar stream para a câmara {camera_id} ({self.camera_info['name']})")
        
        while self.is_running:
            cap = cv2.VideoCapture(rtsp_url)
            if not cap.isOpened():
                logger.warning(f"Não foi possível abrir o stream para a câmara {camera_id}. A tentar novamente em 10s.")
                time.sleep(10)
                continue

            logger.info(f"Stream conectado com sucesso para a câmara {camera_id}.")
            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    logger.warning(f"Frame perdido da câmara {camera_id}. A reconectar...")
                    break 

                sighting_data = self.lpr_processor.process_frame(frame, camera_id)
                if sighting_data:
                    self.api_client.send_sighting(sighting_data)
                
                time.sleep(0.05)
            
            cap.release()
        logger.info(f"Stream para a câmara {camera_id} encerrado.")

    def stop(self):
        self.is_running = False

def main():
    logger.info("Serviço AI-Processor a iniciar...")
    
    api_client = APIClient()
    lpr_processor = LPRProcessor()
    
    active_threads: dict[int, CameraStreamer] = {}

    while True:
        try:
            active_cameras = api_client.get_active_cameras()
            current_camera_ids = {cam['id'] for cam in active_cameras}
            running_thread_ids = set(active_threads.keys())

            for cam in active_cameras:
                if cam['id'] not in running_thread_ids:
                    logger.info(f"Nova câmara ativa detetada: ID {cam['id']}. A iniciar processamento.")
                    thread = CameraStreamer(cam, lpr_processor, api_client)
                    thread.start()
                    active_threads[cam['id']] = thread

            for cam_id in running_thread_ids - current_camera_ids:
                logger.info(f"Câmara ID {cam_id} não está mais ativa. A parar processamento.")
                active_threads[cam_id].stop()
                del active_threads[cam_id]

        except Exception as e:
            logger.error(f"Erro no ciclo principal de gestão de câmaras: {e}")

        time.sleep(30)

if __name__ == "__main__":
    main()