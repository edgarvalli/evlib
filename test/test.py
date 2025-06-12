import sys
from pathlib import Path

cwd = Path(__file__).parent.parent

sys.path.append(str(cwd))

from cfdi.cfdi import FacturaFiscal
from cfdi import tools

if len(sys.argv) == 1:
    raise ValueError('Debe de definir un parametro.')

path = Path(sys.argv[1])

if not path.exists():
    raise ValueError('No es una ruta valida {}'.format(str(path)))

facturas = tools.convertir_facturas_zip(path)

tools.exportar_facturas_excel(facturas)