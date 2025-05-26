from cfdi.cfdi import FacturaFiscal

xml_path = "C:/Dev/evlib/cfdi/PET040903DH1GDAHK795006.xml"
with open(xml_path, 'r') as xmlstr:
    ff = FacturaFiscal.parse_from_xml(xmlstr.read())

    print(ff.__dict__)