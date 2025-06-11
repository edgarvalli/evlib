import sys
from pathlib import Path

cwd = Path(__file__).parent.parent

sys.path.append(str(cwd))

from cfdi import SATSDK

sdk = SATSDK()

sdk.autenticar()