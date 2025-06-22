from comprobante_fiscal_sat import ComprobanteFiscal

# ComprobanteFiscal.convertirxml("C:\\Users\\edgar\\Downloads\\CPR181205KV3_COVA_204_20240902.xml")

xml = "C:\\Users\\edgar\\Downloads\\CPR181205KV3_COVA_204_20240902.xml"

with open(xml, 'r', encoding='utf-8') as f:
    ComprobanteFiscal.convertirxml(xml=f.read())