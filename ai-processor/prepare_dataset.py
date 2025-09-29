import os
import cv2
import pandas as pd
import requests
import shutil
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from ultralytics import YOLO
import numpy as np

# --- CONFIGURAÇÃO ---
try:
    # Se estiver rodando como um script
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
except NameError:
    # Se estiver rodando em um ambiente interativo (como Jupyter)
    BASE_DIR = os.getcwd()

INPUT_EXCEL_PATH = os.path.join(BASE_DIR, "report.xlsx")
YOLO_MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")
OUTPUT_PATH = os.path.join(BASE_DIR, "fast-plate-ocr-master", "data")

def download_image(url):
    """Tenta baixar uma imagem de uma URL com um timeout."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()  # Lança um erro para status HTTP ruins (4xx ou 5xx)
        image_array = np.frombuffer(response.content, np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Aviso: Falha ao baixar a imagem da URL: {url} | Erro: {e}")
        return None

def main():
    print("--- INICIANDO PREPARAÇÃO FINAL DO DATASET (COM COLUNAS CORRIGIDAS) ---")
    
    if os.path.exists(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)
    
    train_dir = os.path.join(OUTPUT_PATH, "train_images")
    val_dir = os.path.join(OUTPUT_PATH, "val_images")
    os.makedirs(train_dir)
    os.makedirs(val_dir)
    print("Diretórios limpos e recriados.")

    model = YOLO(YOLO_MODEL_PATH)
    
    df = pd.read_excel(INPUT_EXCEL_PATH, skiprows=5)
    df.rename(columns=lambda x: x.strip(), inplace=True)
    df_filtered = df.dropna(subset=['Placa', 'Imagem'])
    df_filtered = df_filtered[df_filtered['Placa'].str.strip() != '']

    all_records = []
    processed_count = 0
    error_count = 0
    
    # <<< INÍCIO DA SEÇÃO CORRIGIDA >>>
    for _, row in tqdm(df_filtered.iterrows(), total=len(df_filtered), desc="Processando imagens"):
        full_image = download_image(row['Imagem'])
        if full_image is None:
            error_count += 1
            continue
            
        results = model(full_image, verbose=False)
        
        if len(results[0].boxes) > 0:
            coords_float = results[0].boxes[0].xyxy[0].cpu().numpy()
            
            # 1. VERIFICAÇÃO: Checa se as coordenadas são números finitos (evita 'inf' e 'NaN')
            if np.isfinite(coords_float).all():
                # 2. CONVERSÃO SEGURA: Usa int64 para uma gama maior de valores
                coords = coords_float.astype(np.int64)
                
                # 3. VALIDAÇÃO DE LIMITES: Garante que as coordenadas não sejam negativas
                coords = np.maximum(coords, 0)

                h, w, _ = full_image.shape
                x1, y1, x2, y2 = coords
                
                # Garante que as coordenadas não ultrapassem as dimensões da imagem
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w, x2), min(h, y2)

                # Processa apenas se a área de recorte for válida (evita recortes de tamanho zero)
                if x2 > x1 and y2 > y1:
                    plate_crop = full_image[y1:y2, x1:x2]
                    
                    plate_label = str(row['Placa']).strip()
                    new_filename = f"{plate_label}_{processed_count}.jpg"
                    
                    all_records.append({"image_data": plate_crop, "label": plate_label, "filename": new_filename})
                    processed_count += 1
                else:
                    error_count += 1
                    print(f"🐛 Aviso: Coordenadas com área zero para a imagem: {row['Imagem']}")
            else:
                error_count += 1
                print(f"🐛 Aviso: Coordenadas inválidas (inf/NaN) detectadas na imagem: {row['Imagem']}. Pulando.")
    # <<< FIM DA SEÇÃO CORRIGIDA >>>

    print("\n--- Resumo do Processamento ---")
    print(f"✅ Imagens processadas com sucesso: {processed_count}")
    print(f"❌ Imagens com erro ou puladas: {error_count}")
    print("--------------------------------")

    if not all_records:
        print("Nenhuma imagem foi processada com sucesso. Encerrando o script.")
        return

    train_records, val_records = train_test_split(all_records, test_size=0.2, random_state=42)

    # Usando 'image_path' e 'plate_text' para os arquivos CSV
    train_csv_data = [{"image_path": os.path.join("train_images", r['filename']), "plate_text": r['label']} for r in train_records]
    pd.DataFrame(train_csv_data).to_csv(os.path.join(OUTPUT_PATH, "train.csv"), index=False)
    for r in tqdm(train_records, desc="Salvando imagens de treino"):
        cv2.imwrite(os.path.join(train_dir, r['filename']), r['image_data'])

    val_csv_data = [{"image_path": os.path.join("val_images", r['filename']), "plate_text": r['label']} for r in val_records]
    pd.DataFrame(val_csv_data).to_csv(os.path.join(OUTPUT_PATH, "validation.csv"), index=False)
    for r in tqdm(val_records, desc="Salvando imagens de validação"):
        cv2.imwrite(os.path.join(val_dir, r['filename']), r['image_data'])
    
    print("\n🎉 Processamento concluído com sucesso!")

if __name__ == "__main__":
    main()