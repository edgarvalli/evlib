from .comprobante_ingresos import ComprobanteIngreso
from .comprobante_pago import ComprobantePago
from typing import  Union

class ComprobanteFiscal:
    
    @staticmethod
    def convertirxml(xml: str = None,) -> Union[ComprobanteIngreso, ComprobantePago]:
        
        if xml is None:
            return None
        
        import xml.etree.ElementTree as ET
        
        if xml.endswith(".xml"):
            root = ET.parse(xml)
            root = root.getroot()
        else:
            root = ET.fromstring(xml)
        
        if root is None:
            return None
        
        tipo = root.attrib.get('TipoDeComprobante', None)
        
        if tipo is None:
            return None

        elif tipo == "I":
            return ComprobanteIngreso.convertir_xml(xml=xml)
        elif tipo == "P":
            return ComprobantePago.convertir_xml(xml=xml)