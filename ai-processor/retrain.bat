@echo OFF
echo ======================================================
echo INICIANDO ROTINA DE TREINAMENTO AUTOMATICO
echo Data: %DATE% - Hora: %TIME%
echo ======================================================

:: Certifique-se de que o caminho para a sua pasta de projeto está correto
set PROJECT_DIR=D:\GT-VISION-VMS\ai-processor

:: Ativa o ambiente virtual
call %PROJECT_DIR%\venv\Scripts\activate

:: Passo 1: Executa o coletor para adicionar novos dados ao dataset
echo.
echo --- PASSO 1: COLETANDO NOVOS DADOS ---
python %PROJECT_DIR%\collector.py

:: Passo 2: Navega para a pasta de treinamento
cd %PROJECT_DIR%\fast-plate-ocr-master

:: Passo 3: Define o backend do Keras
set KERAS_BACKEND=tensorflow 

:: Passo 4: Inicia o treinamento
echo.
echo --- PASSO 2: INICIANDO TREINAMENTO ---
fast-plate-ocr train ^
  --model-config-file models/cct_s_v1.yaml ^
  --plate-config-file config/default_latin_plate_config.yaml ^
  --annotations data/train.csv ^
  --val-annotations data/validation.csv ^
  --epochs 150 ^
  --batch-size 32 ^
  --output-dir trained_models/ ^
  --mixed-precision-policy mixed_float16

echo.
echo ======================================================
echo ROTINA DE TREINAMENTO CONCLUIDA
echo ======================================================
pause