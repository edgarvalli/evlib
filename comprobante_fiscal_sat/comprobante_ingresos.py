import xml.etree.ElementTree as ET
from .models import (
    List,
    Emisor,
    Impuesto,
    Receptor,
    Concepto,
    Comprobante,
    TimbreFiscal,
)


class ComprobanteTools:

    @staticmethod
    def obtener_impuestos(
        tag: ET.ElementTree, tipo: str, namespaces: dict = {}
    ) -> List[Impuesto]:
        _impuestos = []

        for _impuesto in tag.iterfind(".//cfdi:" + tipo, namespaces):
            _impuesto_class = Impuesto()
            _impuesto_class.tipo = tipo
            _impuesto_class.set_from_dict(_impuesto.attrib)
            _impuestos.append(_impuesto_class)

        return _impuestos


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

        if xml.endswith(".xml"):
            root = ET.parse(xml)
            root = root.getroot()
        else:
            root = ET.fromstring(text=xml)

        if root is None:
            return None

        comprobante = Comprobante()
        comprobante.set_from_dict(root.attrib)

        namespaces = {
            "cfdi": "http://www.sat.gob.mx/cfd/4",
            "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital",
        }

        tipo_impuesto = ["Traslado", "Retencion"]

        comprobante_impuestos = []
        comprobante_impuestos_tag = root.find(".//cfdi:Impuestos", namespaces)

        for tipo in tipo_impuesto:
            comprobante_impuestos.extend(
                ComprobanteTools.obtener_impuestos(
                    tag=comprobante_impuestos_tag, tipo=tipo, namespaces=namespaces
                )
            )

        emisor_tag = root.find(".//cfdi:Emisor", namespaces)
        emisor = Emisor()
        emisor.set_from_dict(emisor_tag.attrib)

        receptor_tag = root.find(".//cfdi:Receptor", namespaces)
        receptor = Receptor()
        receptor.set_from_dict(receptor_tag.attrib)

        timbrefiscal_tag = root.find(".//tfd:TimbreFiscalDigital", namespaces)
        timbrefiscal = TimbreFiscal()
        timbrefiscal.set_from_dict(timbrefiscal_tag.attrib)

        conceptos = []
        for _concepto_tag in root.findall(".//cfdi:Concepto", namespaces):
            _concepto = Concepto()
            _concepto.set_from_dict(_concepto_tag.attrib)
            for tipo in tipo_impuesto:
                _concepto.Impuestos.extend(
                    ComprobanteTools.obtener_impuestos(
                        tag=comprobante_impuestos_tag, tipo=tipo, namespaces=namespaces
                    )
                )
            
            conceptos.append(_concepto)

        # Declarar comprobante
        
        comprobante_ingreso = ComprobanteIngreso()
        comprobante.impuestos = comprobante_impuestos
        comprobante_ingreso.comprobante = comprobante
        comprobante_ingreso.emisor = emisor
        comprobante_ingreso.receptor = receptor
        comprobante_ingreso.timbrefiscal = timbrefiscal
        comprobante_ingreso.conceptos = conceptos


        return comprobante
