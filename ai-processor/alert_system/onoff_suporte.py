import json
import os

CONFIG_FILE = "gt_ia_config.json"

def _read_config():
    """Lê o estado atual da configuração."""
    if not os.path.exists(CONFIG_FILE):
        # Estado inicial: desativado, como pedido
        return {"gt_ia_enabled": False}
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"gt_ia_enabled": False}

def _write_config(config):
    """Escreve o novo estado na configuração."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def ativar_gt_ia():
    """Ativa o processamento do modelo YOLO."""
    print("Ativando o suporte da GT IA (YOLO)...")
    config = _read_config()
    config["gt_ia_enabled"] = True
    _write_config(config)
    print("GT IA ATIVADA.")

def desativar_gt_ia():
    """Desativa o processamento do modelo YOLO."""
    print("Desativando o suporte da GT IA (YOLO)...")
    config = _read_config()
    config["gt_ia_enabled"] = False
    _write_config(config)
    print("GT IA DESATIVADA.")

def verificar_status_gt_ia() -> bool:
    """Verifica se a GT IA está ativada. Retorna True ou False."""
    config = _read_config()
    return config.get("gt_ia_enabled", False)