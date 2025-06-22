from dataclasses import dataclass
from typing import List, Dict
from dataclasses import field


def default_str():
    return ""


def default_float():
    return 0.0


def default_list():
    return []


class Common:

    def set_from_dict(self, kwargs: Dict = {}):
        for key in self.__dict__.keys():
            if key in kwargs:
                setattr(self, key, kwargs[key])

    def asdict(self):
        return self.__dict__


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
