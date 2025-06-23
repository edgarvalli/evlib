from dataclasses import dataclass
from typing import Dict, Any, List, Union


class DBBase:
    def parse_from_dict(self, config: Dict[str, Any]):
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def asdict(self) -> dict:
        return self.__dict__


@dataclass
class DBConfig(DBBase):
    def __init__(
        self,
        host: str = "",
        port: int = 0,
        user: str = "",
        password: str = "",
        database: str = "",
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database


@dataclass
class DBResult(DBBase):
    error: bool
    message: str
    columns: list
    data: Union[List[dict], dict]
    id: int

    def __init__(self) -> None:
        self.error = False
        self.message = ""
        self.data = []
        self.columns = []
        self.id = None


@dataclass
class HttpAPIResponse:

    error: bool
    message: str
    data: Union[list, dict]

    def __init__(self) -> None:
        self.error = True
        self.message = "Http Response Init"
        self.data = {}

    def todict(self) -> dict:
        return self.__dict__
