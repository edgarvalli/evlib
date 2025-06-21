import xml.etree.ElementTree as ET
from .models import (
    List,
    Comprobante,
    Emisor,
    Receptor,
    Concepto,
    Impuesto,
    TimbreFiscal,
)


class ComprobanteIngreso:
    comprobante: Comprobante
    emisor: Emisor
    receptor: Receptor
    conceptos: List[Concepto]
    timbrefiscal: TimbreFiscal
    
    @staticmethod
    def convertir_xml(xml: str) -> "ComprobanteIngreso":
        
        if not isinstance(xml, str):
            return None
                    
        
        root = ET.fromstring(xml)
        
        if root is None:
            return None
        
        namespaces = {
            'cfdi':'http://www.sat.gob.mx/cfd/4',
            'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'
        }
        
        # Declarar comprobante
        
        comprobante_xml = root.find('.//cfdi:Comprobante', namespaces)
        
        if comprobante_xml is None:
            comprobante = None
        else:
            comprobante = Comprobante(
                Version=comprobante_xml.attrib.get('Version',''),
                Serie=comprobante_xml.attrib.get('Serie',''),
                Folio=comprobante_xml.attrib.get('Folio',''),
                Fecha=comprobante_xml.attrib.get('Fecha',''),
                Sello=comprobante_xml.attrib.get('Sello',''),
                FormaPago=comprobante_xml.attrib.get('FormaPago',''),
                NoCertificado=comprobante_xml.attrib.get('NoCertificado',''),
                Certificado=comprobante_xml.attrib.get('Certificado',''),
                SubTotal=comprobante_xml.attrib.get('SubTotal',0.0),
                Moneda=comprobante_xml.attrib.get('Moneda','MXN'),
                TipoCambio=comprobante_xml.attrib.get('TipoCambio',0.0),
                Total=comprobante_xml.attrib.get('Total',0.0),
                TipoDeComprobante=comprobante_xml.attrib.get('TipoDeComprobante','I'),
                Exportacion=comprobante_xml.attrib.get('Exportacion',''),
                MetodoPago=comprobante_xml.attrib.get('MetodoPago',''),
                LugarExpedicion=comprobante_xml.attrib.get('LugarExpedicion','')
            )
        
        
        return comprobante
