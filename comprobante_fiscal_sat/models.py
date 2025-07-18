from dataclasses import dataclass
from typing import List, Dict
from dataclasses import field


def default_str():
    return ""


def default_float():
    return 0.0


def default_list():
    return []

def default_int():
    return 0

def default_dict():
    return {}


class Common:

    def set_from_dict(self, kwargs: Dict = {}):
        for key in self.__dict__.keys():
            if key in kwargs:
                value = kwargs[key]
                attr = getattr(self, key)
                if isinstance(attr, str):
                    setattr(self, key, str(value))
                elif isinstance(attr, int):
                    try:
                        setattr(self, key, int(value))
                    except (ValueError, TypeError):
                        setattr(self, key, 0)
                elif isinstance(attr, float):
                    try:
                        setattr(self, key, float(value))
                    except (ValueError, TypeError):
                        setattr(self, key, 0.0)
                elif isinstance(attr, dict):
                    if isinstance(value, dict):
                        setattr(self, key, value)
                elif isinstance(attr, list):
                    if isinstance(value, list):
                        setattr(self, key, value)
                else:
                    setattr(self, key, value)

    def asdict(self):
        def convert(value):
            if isinstance(value, Common):
                return value.asdict()
            elif isinstance(value, list):
                return [convert(item) for item in value]
            elif isinstance(value, dict):
                return {k: convert(v) for k, v in value.items()}
            else:
                return value

        return {key: convert(getattr(self, key)) for key in self.__dict__}


@dataclass
class Emisor(Common):
    Rfc: str = field(default_factory=default_str)
    Nombre: str = field(default_factory=default_str)
    RegimenFiscal: str = field(default_factory=default_str)


@dataclass
class Receptor(Common):
    Rfc: str = field(default_factory=default_str)
    Nombre: str = field(default_factory=default_str)
    DomicilioFiscalReceptor: str = field(default_factory=default_str)
    RegimenFiscalReceptor: str = field(default_factory=default_str)
    UsoCFDI: str = field(default_factory=default_str)


@dataclass
class Impuesto(Common):
    tipo: str = field(default_factory=default_str)
    Base: float = field(default_factory=default_float)
    Impuesto: str = field(default_factory=default_str)
    TipoFactor: str = field(default_factory=default_str)
    TasaOCuota: float = field(default_factory=default_float)
    Importe: float = field(default_factory=default_float)


@dataclass
class Concepto(Common):
    ClaveProdServ: str = field(default_factory=default_str)
    NoIdentificacion: str = field(default_factory=default_str)
    Cantidad: float = field(default_factory=default_float)
    Descripcion: str = field(default_factory=default_str)
    ValorUnitario: str = field(default_factory=default_str)
    Importe: float = field(default_factory=default_float)
    ObjetoImp: str = field(default_factory=default_str)
    Impuestos: List[Impuesto] = field(default_factory=default_list)


@dataclass
class TimbreFiscal(Common):
    UUID: str = field(default_factory=default_str)
    FechaTimbrado: str = field(default_factory=default_str)
    RfcProvCertif: str = field(default_factory=default_str)
    SelloCFD: str = field(default_factory=default_str)
    NoCertificadoSAT: str = field(default_factory=default_str)
    SelloSAT: str = field(default_factory=default_str)


@dataclass
class Comprobante(Common):
    Version: str = field(default_factory=default_str)
    Serie: str = field(default_factory=default_str)
    Folio: str = field(default_factory=default_str)
    Fecha: str = field(default_factory=default_str)
    Sello: str = field(default_factory=default_str)
    FormaPago: str = field(default_factory=default_str)
    NoCertificado: str = field(default_factory=default_str)
    Certificado: str = field(default_factory=default_str)
    Moneda: str = field(default_factory=default_str)
    TipoCambio: float = field(default_factory=default_float)
    SubTotal: float = field(default_factory=default_float)
    Total: float = field(default_factory=default_float)
    TipoDeComprobante: str = field(default_factory=default_str)
    Exportacion: str = field(default_factory=default_str)
    MetodoPago: str = field(default_factory=default_str)
    LugarExpedicion: str = field(default_factory=default_str)
    impuestos: List[Impuesto] = field(default_factory=default_list)


@dataclass
class TrasladoDR(Common):
    BaseDR: float = field(default_factory=default_float)
    ImpuestoDR: str = field(default_factory=default_str)
    TipoFactorDR: str = field(default_factory=default_str)
    TasaOCuotaDR: float = field(default_factory=default_float)
    ImporteDR: float = field(default_factory=default_float)

@dataclass
class ImpuestosDR(Common):
    TrasladosDR: TrasladoDR

@dataclass
class DocumentoRelacionado(Common):
    IdDocumento: str = field(default_factory=default_str)
    Serie: str = field(default_factory=default_str)
    Folio: str = field(default_factory=default_str)
    MonedaDR: str = field(default_factory=default_str)
    EquivalenciaDR: float = field(default_factory=default_float)
    NumParcialidad: int = field(default_factory=default_int)
    ImpSaldoAnt: float = field(default_factory=default_float)
    ImpPagado: float = field(default_factory=default_float)
    ImpSaldoInsoluto: float = field(default_factory=default_float)
    ObjetoImpDR: float = field(default_factory=default_float)
    impuestos: ImpuestosDR = field(default_factory=default_dict)

@dataclass
class Pago(Common):
    FechaPago: str = field(default_factory=default_str)
    FormaDePagoP: str = field(default_factory=default_str)
    MonedaP: str = field(default_factory=default_str)
    TipoCambioP: float = field(default_factory=default_float)
    Monto: float = field(default_factory=default_float)
    documentos_relacionados: List[DocumentoRelacionado] = field(default_factory=default_list)

class PagoTotales(Common):
    TotalTrasladosBaseIVA16: float = field(default_factory=default_float)
    TotalTrasladosImpuestoIVA16: float = field(default_factory=default_float)
    MontoTotalPagos: float = field(default_factory=default_float)

class Pagos(Common):
    Version: str = field(default_factory=default_str)
    Totales: PagoTotales = field(default_factory=default_dict)
    pago: Pago = field(default_factory=default_dict)

@dataclass
class ComplementosPago(Common):
    pagos: Pagos = field(default_factory=default_dict)
    timbrefiscal: TimbreFiscal = field(default_factory=default_dict)
