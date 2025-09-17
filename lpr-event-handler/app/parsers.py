from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import xml.etree.ElementTree as ET
import json
import base64
from datetime import datetime

class LPREventParser(ABC):
    @abstractmethod
    def parse(self, request_data: bytes) -> Optional[Dict[str, Any]]:
        pass

class HikvisionXMLParser(LPREventParser):
    def parse(self, request_data: bytes) -> Optional[Dict[str, Any]]:
        try:
            root = ET.fromstring(request_data)
            plate = root.findtext('.//{http://www.hikvision.com/ver20/XMLSchema}plateNumber')
            if not plate:
                return None
            # Você pode adicionar a extração da imagem aqui se desejar
            return {"license_plate": plate.strip()}
        except ET.ParseError:
            return None

class IntelbrasJSONParser(LPREventParser):
    def parse(self, request_data: bytes) -> Optional[Dict[str, Any]]:
        try:
            data = json.loads(request_data)
            plate = data.get("LPR", {}).get("Plate", "")
            if not plate:
                return None
            return {"license_plate": plate.strip()}
        except json.JSONDecodeError:
            return None

PARSER_MAP = {
    "hikvision": HikvisionXMLParser(),
    "intelbras": IntelbrasJSONParser(),
}

def get_parser(brand: str) -> Optional[LPREventParser]:
    return PARSER_MAP.get(brand)