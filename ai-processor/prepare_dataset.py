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
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
except NameError:
    BASE_DIR = os.getcwd()

INPUT_EXCEL_PATH = os.path.join(BASE_DIR, "report.xlsx")
YOLO_MODEL_PATH = os.path.join(BASE_DIR, "yolov8n.pt")
OUTPUT_PATH = os.path.join(BASE_DIR, "fast-plate-ocr-master", "data")

def download_image(url):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        image_array = np.frombuffer(response.content, np.uint8)
        return cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    except requests.exceptions.RequestException:
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
    for _, row in tqdm(df_filtered.iterrows(), total=len(df_filtered), desc="Processando imagens"):
        full_image = download_image(row['Imagem'])
        if full_image is None: continue
            
        results = model(full_image, verbose=False)
        
        if len(results[0].boxes) > 0:
            coords = results[0].boxes[0].xyxy[0].cpu().numpy().astype(int)
            plate_crop = full_image[coords[1]:coords[3], coords[0]:coords[2]]
            
            plate_label = str(row['Placa']).strip()
            new_filename = f"{plate_label}_{processed_count}.jpg"
            
            all_records.append({ "image_data": plate_crop, "label": plate_label, "filename": new_filename })
            processed_count += 1

    train_records, val_records = train_test_split(all_records, test_size=0.2, random_state=42)

    # <<< MUDANÇA CRÍTICA AQUI >>>
    # Usando 'image_path' e 'plate_text'
    train_csv_data = [{"image_path": os.path.join("train_images", r['filename']), "plate_text": r['label']} for r in train_records]
    pd.DataFrame(train_csv_data).to_csv(os.path.join(OUTPUT_PATH, "train.csv"), index=False)
    for r in train_records:
        cv2.imwrite(os.path.join(train_dir, r['filename']), r['image_data'])

    # <<< MUDANÇA CRÍTICA AQUI >>>
    # Usando 'image_path' e 'plate_text'
    val_csv_data = [{"image_path": os.path.join("val_images", r['filename']), "plate_text": r['label']} for r in val_records]
    pd.DataFrame(val_csv_data).to_csv(os.path.join(OUTPUT_PATH, "validation.csv"), index=False)
    for r in val_records:
        cv2.imwrite(os.path.join(val_dir, r['filename']), r['image_data'])
    
    print("\n🎉 Processamento concluído com os nomes de coluna corretos!")

if __name__ == "__main__":
    main()