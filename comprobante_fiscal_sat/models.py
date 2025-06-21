from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Emisor:
    Rfc: str
    Nombre: str
    RegimenFiscal: str

@dataclass
class Receptor:
    Rfc: str
    Nombre: str
    DomicilioFiscalReceptor: str
    RegimenFiscalReceptor: str
    UsoCFDI: str
    
@dataclass
class Impuesto:
    tipo: str = "traslado"
    Base: float
    Impuesto: str
    TipoFactor: str
    TasaOCuota: float
    Importe: float

@dataclass
class Concepto:
    ClaveProdServ: str
    NoIdentificacion: str
    Cantidad: float
    Descripcion: str
    ValorUnitario: str
    Importe: float
    ObjetoImp: str

@dataclass
class TimbreFiscal:
    UUID: str
    FechaTimbrado: str
    RfcProvCertif: str
    SelloCFD: str
    NoCertificadoSAT: str
    SelloSAT: str

@dataclass
class Comprobante:
    Version: str
    Serie: str
    Folio: str
    Fecha: str
    Sello: str
    FormaPago: str
    NoCertificado: str
    Certificado: str
    Moneda: str
    TipoCambio: float
    SubTotal: float
    Total: float
    TipoDeComprobante: str
    Exportacion: str
    MetodoPago: str
    LugarExpedicion: str