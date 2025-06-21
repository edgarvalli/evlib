from .comprobante_ingresos import ComprobanteIngreso
from typing import  Union

class ComprobanteFiscal:
    
    @staticmethod
    def convertirxml(xml: str = None, xmlpath: str = None) -> Union[ComprobanteIngreso]:
        
        xml_content = xml
        
        if xmlpath is None:
            with open(str(xmlpath), 'r', encoding='utf-8') as f:
                xml_content = f.read()
        
        
        if xml_content is None:
            return None
        
        namespaces = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
        
        import xml.etree.ElementTree as ET
        
        root = ET.fromstring(xml_content)
        
        tipo = root.find('.//cfdi:Comprobante ',namespaces).get('TipoDeComprobante', None)
        
        if tipo is None:
            return None

        elif tipo is "I":
            return ComprobanteIngreso.convertir_xml(xml=xml_content)