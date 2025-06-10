from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

catalogo_impuestos = {
    "retencion": {
        "1": "Retención de ISR",
        "2": "Retención de IVA",
        "3": "Retención de IEPS",
    },
    "traslado": {"2": "Traslado de IVA", "3": "Traslado de IEPS"},
}


@dataclass
class Emisor:
    rfc: str
    nombre: str
    regimen_fiscal: str
    domicilio_fiscal: Optional[str] = None
    codigo_postal: Optional[str] = None


@dataclass
class Receptor:
    rfc: str
    nombre: str
    uso_cfdi: str
    domicilio: Optional[str] = None
    codigo_postal: Optional[str] = None


@dataclass
class Concepto:
    clave_producto_servicio: str
    cantidad: float
    clave_unidad: str
    descripcion: str
    valor_unitario: float
    importe: float
    iva_trasladado: float
    isr_trasladado: float
    iva_retenido: float
    isr_retenido: float


@dataclass
class Complemento:
    tipo: str  # Ej: "TimbreFiscalDigital"
    uuid: str
    fecha_timbrado: datetime
    rfc_proveedor_certificado: str
    sello_cfd: str


class FacturaFiscal:
    def __init__(self):
        self.version: str = "4.0"  # Versión del CFDI
        self.serie: Optional[str] = None
        self.folio: Optional[str] = None
        self.fecha: datetime = datetime.now()
        self.sello: str = ""
        self.uuid: str = ""  # UUID del CFDI
        self.forma_pago: str = ""  # Clave SAT forma pago
        self.metodo_pago: str = ""  # Clave SAT método pago
        self.tipo_comprobante: str = "I"  # I=Ingreso, E=Egreso, T=Traslado
        self.lugar_expedicion: str = ""  # Código postal
        self.moneda: str = "MXN"
        self.tipo_cambio: Optional[float] = None
        self.subtotal: float = 0.0
        self.descuento: Optional[float] = None
        self.total: float = 0.0
        self.emisor: Optional[Emisor] = None
        self.receptor: Optional[Receptor] = None
        self.conceptos: List[Concepto] = []
        self.complementos: List[Complemento] = []
        self.xml_string: str = None
        self.catalogo_impuestos = catalogo_impuestos
        self.iva: float = 0.0
        self.isr: float = 0.0

    def agregar_concepto(self, concepto: Concepto):
        self.conceptos.append(concepto)
        self.subtotal += concepto.importe
        # Aquí deberías actualizar también los impuestos

    @staticmethod
    def parse_from_xml(xml_string: str) -> "FacturaFiscal":
        # Esta función debe parsear el XML CFDI y poblar una instancia de FacturaFiscal.
        # Aquí solo se muestra un esqueleto básico.
        import xml.etree.ElementTree as ET

        tree = ET.fromstring(xml_string)
        factura = FacturaFiscal()
        factura.xml_string = xml_string

        namespaces = {
            "cfdi": "http://www.sat.gob.mx/cfd/4",
            "tfd": "http://www.sat.gob.mx/TimbreFiscalDigital",
        }

        timbrefiscal = tree.find(".//tfd:TimbreFiscalDigital", namespaces)
        if timbrefiscal is not None:
            factura.uuid = timbrefiscal.attrib.get("UUID", "")
            factura.fecha = (
                datetime.fromisoformat(timbrefiscal.attrib.get("FechaTimbrado"))
                if timbrefiscal.attrib.get("FechaTimbrado")
                else datetime.now()
            )
            factura.sello = timbrefiscal.attrib.get("SelloCFD", "")

        # Ejemplo de parseo básico (debería ajustarse según el XML real)
        factura.serie = tree.attrib.get("Serie")
        factura.folio = tree.attrib.get("Folio")
        factura.fecha = (
            datetime.fromisoformat(tree.attrib.get("Fecha"))
            if tree.attrib.get("Fecha")
            else datetime.now()
        )
        factura.moneda = tree.attrib.get("Moneda", "MXN")
        factura.tipo_cambio = (
            float(tree.attrib.get("TipoCambio"))
            if tree.attrib.get("TipoCambio")
            else None
        )
        factura.subtotal = float(tree.attrib.get("SubTotal", 0))
        factura.total = float(tree.attrib.get("Total", 0))

        # Parseo de emisor
        emisor_elem = tree.find(".//cfdi:Emisor", namespaces)

        if emisor_elem is not None:
            factura.emisor = Emisor(
                rfc=emisor_elem.attrib.get("Rfc", ""),
                nombre=emisor_elem.attrib.get("Nombre", ""),
                regimen_fiscal=emisor_elem.attrib.get("RegimenFiscal", ""),
                domicilio_fiscal=emisor_elem.attrib.get("DomicilioFiscal", None),
                codigo_postal=emisor_elem.attrib.get("CodigoPostal", None),
            )

        # Parseo de receptor
        receptor_elem = tree.find(".//cfdi:Receptor", namespaces)

        if receptor_elem is not None:
            factura.receptor = Receptor(
                rfc=receptor_elem.attrib.get("Rfc", ""),
                nombre=receptor_elem.attrib.get("Nombre", ""),
                uso_cfdi=receptor_elem.attrib.get("UsoCFDI", ""),
                domicilio=receptor_elem.attrib.get("Domicilio", None),
                codigo_postal=receptor_elem.attrib.get("CodigoPostal", None),
            )

        # Parseo de conceptos
        conceptos_elem = tree.find(".//cfdi:Conceptos", namespaces)

        if conceptos_elem is not None:
            for concepto_elem in conceptos_elem.findall(".//cfdi:Concepto", namespaces):

                iva_trasladado = 0.0
                isr_retenido = 0.0

                for impuesto in concepto_elem.findall(".//cfdi:Traslado", namespaces):
                    tipo =  impuesto.attrib.get("Impuesto","000")

                    if tipo == "002":
                        iva_trasladado += float(impuesto.attrib.get("Importe", 0.0))
                        factura.iva += iva_trasladado
                
                for impuesto in concepto_elem.findall('.//cfdi:Retenido', namespaces):
                    tipo = impuesto.attrib.get("Impuesto", "000")

                    if tipo == "001":
                        isr_retenido += impuesto.attrib.get("Importe",0.0)
                        isr += isr_retenido
                        

                concepto = Concepto(
                    clave_producto_servicio=concepto_elem.attrib.get(
                        "ClaveProdServ", ""
                    ),
                    cantidad=float(concepto_elem.attrib.get("Cantidad", 0)),
                    clave_unidad=concepto_elem.attrib.get("ClaveUnidad", ""),
                    descripcion=concepto_elem.attrib.get("Descripcion", ""),
                    valor_unitario=float(concepto_elem.attrib.get("ValorUnitario", 0)),
                    importe=float(concepto_elem.attrib.get("Importe", 0)),
                    iva_retenido=0.0,
                    iva_trasladado=iva_trasladado,
                    isr_trasladado=0.0,
                    isr_retenido=isr_retenido,
                )
                factura.conceptos.append(concepto)

        # Nota: El parseo de impuestos y complementos debe implementarse según la estructura real del XML CFDI.
        return factura

    def validar(self) -> bool:
        """Valida que la factura cumpla con los requisitos mínimos del SAT"""
        # Implementar validaciones según reglas del SAT
        return True
