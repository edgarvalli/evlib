import xml.etree.ElementTree as ET
from typing import List
from .models import (
    Pago,
    Pagos,
    Emisor,
    Receptor,
    Concepto,
    Comprobante,
    PagoTotales,
    TimbreFiscal,
    ComplementosPago,
    DocumentoRelacionado,
)


class ComprobantePago:
    comprobante: Comprobante
    emisor: Emisor
    receptor: Receptor
    conceptos: List[Concepto]
    complementos: ComplementosPago

    def asdict(self):
        return {
            "comprobante": self.comprobante.asdict() if self.comprobante else None,
            "emisor": self.emisor.asdict() if self.emisor else None,
            "receptor": self.receptor.asdict() if self.receptor else None,
            "conceptos": [c.asdict() for c in self.conceptos] if hasattr(self, "conceptos") and self.conceptos else [],
            "complementos": self.complementos.asdict() if self.complementos else None,
        }

    @staticmethod
    def convertir_xml(xml: str) -> "ComprobantePago":

        if not isinstance(xml, str):
            return None

        if xml.endswith(".xml"):
            root = ET.parse(xml)
            root = root.getroot()
        else:
            root = ET.fromstring(text=xml)

        if root is None:
            return None
        
        namespaces = {
            "cfdi": "http://www.sat.gob.mx/cfd/4",
            "pago20": "http://www.sat.gob.mx/Pagos20",
            "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital"
        }

        _comprobante = Comprobante()
        _comprobante.set_from_dict(root.attrib)

        emisor_tag = root.find(".//cfdi:Emisor", namespaces)

        if emisor_tag is not None:
            emisor = Emisor()
            emisor.set_from_dict(emisor_tag.attrib)

        receptor_tag = root.find(".//cfdi:Receptor", namespaces)

        if receptor_tag is not None:
            receptor = Receptor()
            receptor.set_from_dict(receptor_tag.attrib)

        timbrefiscal_tag = root.find(".//tfd:TimbreFiscalDigital", namespaces)

        if timbrefiscal_tag is not None:
            timbrefiscal = TimbreFiscal()
            timbrefiscal.set_from_dict(timbrefiscal_tag.attrib)
        

        pagos = None

        pagos_tag = root.find(".//pago20:Pagos", namespaces)

        if pagos_tag is not None:
            pagos = Pagos()
            pagos.set_from_dict(pagos_tag.attrib)


            pagostotales_tag = pagos_tag.find(".//pago20:Totales", namespaces)
            if pagostotales_tag is not None:
                pagos_totales = PagoTotales()
                pagos_totales.set_from_dict(pagostotales_tag.attrib)
                pagos.Totales = pagos_totales
            
            pago_tag = pagos_tag.find(".//pago20:pago", namespaces)
            
            if pago_tag is not None:
                pago = Pago()
                pago.set_from_dict(pago_tag.attrib)

                documentos_rel_tag = pago_tag.findall(".//pago20:DoctoRelacionado", namespaces)

                if documentos_rel_tag is not None:
                    for dr in documentos_rel_tag:
                        documento_rel = DocumentoRelacionado()
                        documento_rel.set_from_dict(dr.attrib)
                        pago.documentos_relacionados.append(documento_rel)
                
                print(pago)
            
                pagos.pago = pago




        complementos = ComplementosPago()
        complementos.timbrefiscal = timbrefiscal
        complementos.pagos = pagos

        comprobante_pago = ComprobantePago()
        comprobante_pago.comprobante = _comprobante
        comprobante_pago.emisor = emisor
        comprobante_pago.receptor = receptor
        comprobante_pago.complementos = complementos

        return comprobante_pago
