import inspect
from typing import Optional, List, Tuple,Union
from .database import Database, DBConfig, DBResult


class Model:
    _name: str  # Nombre del modelo/tabla
    _description: Optional[str] = None  # Descripción opcional
    id: int
    uuid: str
    config: Optional[DBConfig] = None  # Configuración de la base de datos
    # Lista de índices: (nombre del campo, es único)
    index: List[Tuple[str, bool]]

    def __init__(self, app=None, config: DBConfig = None) -> None:
        """
        Inicializa el modelo y obtiene el nombre de la tabla asociada.
        """
        self.app = app
        self._name = self.get_model_name()
        self.index = []
        if config:
            self.config = config
        else:
            self.config = DBConfig()

    def build(self, config: DBConfig) -> None:
        """
        Construye el modelo en la base de datos.
        """
        self.config = config
        if self.app is None:
            self.__run_build()
        else:
            with self.app.app_context():
                self.__run_build()

    def __run_build(self) -> None:
        """
        Ejecuta la construcción del modelo, verificando si la tabla existe.
        """
        if not self.check_is_model_exists():
            self.generate_model()

    def get_index_definitions(self) -> List[str]:
        """
        Genera las definiciones de índices para el modelo.
        """
        definitions = []
        for name, unique in self.index:
            index_type = "UNIQUE " if unique else ""
            definitions.append(
                f"{index_type}INDEX idx_{
                               self._name}_{name} ({name})"
            )
        return definitions

    def __default_query(self, fields: List[str]) -> str:
        """
        Genera la consulta SQL para crear la tabla.
        """
        base_fields = [
            "id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID'",
        ]
        base_fields.extend(fields)
        base_fields.extend(
            [
                "create_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Fecha de Creacion'",
                "update_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Fecha de Actualizacion'",
            ]
        )
        base_fields.extend(self.get_index_definitions())

        query = f"CREATE TABLE IF NOT EXISTS {self.config.dbname}.{
            self._name} ({', '.join(base_fields)})"
        return query

    def check_is_model_exists(self) -> bool:
        """
        Verifica si la tabla del modelo ya existe en la base de datos.
        """
        try:
            db = Database()
            db.config = self.config
            return db.table_exists(tablename=self._name)
        except Exception as e:
            print(
                f"[ERROR] Error checking if table '{
                  self._name}' exists: {e}"
            )
            return False

    def get_model_name(self) -> str:
        """
        Obtiene el nombre del modelo/tablas.
        Si no está definido, utiliza el nombre de la clase.
        """
        if hasattr(self, "_name"):
            tablename: str = getattr(self, "_name").replace(".", "_")
        else:
            tablename = self.__class__.__name__.lower()
        return tablename

    def generate_model(self) -> None:
        """
        Genera la tabla en la base de datos con los campos definidos en el modelo.
        """
        try:
            fields = inspect.getmembers(self, lambda a: not (inspect.isroutine(a)))
            fields.reverse()
            fields_mysql = []

            for field in fields:
                name, attribute = field
                if hasattr(attribute, "get_mysql_field") and name.lower() != "uuid":
                    mysql_field = f"{name} {attribute.get_mysql_field()}"
                    is_unique = getattr(attribute, "unique", False)

                    # Gestionar índices
                    if getattr(attribute, "index", False):
                        self.index.append((name, is_unique))
                        if is_unique:
                            mysql_field = mysql_field.replace("UNIQUE", "")

                    fields_mysql.append(mysql_field)

            query = self.__default_query(fields=fields_mysql)
            # print(query)  # Depuración: Muestra la consulta generada

            print(
                f"Creating table '{self._name}' in database '{
                  self.config.dbname}'..."
            )
            db = Database()
            db.config = self.config
            db.commit(query=query)
            print(f"Table '{self._name}' created successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to generate table '{self._name}': {e}")

    def getinstance(self) -> Database:
        db = Database()
        db.config = self.config
        return db

    def get_columns(self):
        db = self.getinstance()
        return db.get_description_model(self._name)

    def search(
        self,
        where: list[tuple] = None,
        fields: str = "*",
        limit: str = "50",
        orderby: str = None,
    ) -> DBResult:
        db = self.getinstance()
        return db.search(
            model=f"{self._name}",
            where=where,
            fields=fields,
            limit=limit,
            orderby=orderby,
        )

    def between(self, field: str, first, last, fields="*") -> DBResult:
        db = self.getinstance()
        return db.between(
            model=f"{self._name}", field=field, first=first, last=last, fields=fields
        )

    def search_stream(
        self,
        where: list[tuple] = None,
        fields: str = "*",
        limit: str = "50",
        orderby: str = None,
        action=None,
    ) -> DBResult:
        db = self.getinstance()
        return db.search(
            model=f"{self._name}",
            where=where,
            fields=fields,
            limit=limit,
            orderby=orderby,
            action=action,
        )

    def populate_from_dict(self, obj: dict):
        if hasattr(obj, "items"):
            for k, v in obj.items():
                if hasattr(self, k):
                    setattr(self, k, v)

    def save(self, record: dict = None) -> DBResult:
        db = self.getinstance()
        if not record:
            record = {}
            exeptions = ["app", "_name", "_description", "index", "config"]
            for k, v in self.__dict__.items():
                if not k in exeptions:
                    record[k] = v

        if "id" in record:
            record.pop("id")

        return db.save(self._name, record=record)

    def update(self, id: int, data: dict = None) -> DBResult:
        db = self.getinstance()

        if not data:
            data = {}
            exeptions = ["app", "_name", "_description", "index", "config"]
            for k, v in self.__dict__.items():
                if not k in exeptions:
                    data[k] = v

        if "id" in data:
            data.pop("id")

        return db.update(self._name, id=id, data=data)

    def updateall(self, data: dict = None) -> DBResult:
        db = self.getinstance()

        if not data:
            data = {}
            exeptions = ["app", "_name", "_description", "index", "config"]
            for k, v in self.__dict__.items():
                if not k in exeptions:
                    data[k] = v

        if "id" in data:
            data.pop("id")

        return db.update(self._name, data=data)

    def unlink(self, id: int) -> DBResult:
        db = self.getinstance()
        return db.unlink(self._name, id=id)

    def findone(self, id: int, fields: str = "*") -> DBResult:
        db = self.getinstance()
        return db.findone(self._name, id=id, fields=fields)

    def findoneby(self, where: list[tuple], fields: str = "*") -> DBResult:
        db = self.getinstance()
        return db.findoneby(model=self._name, where=where, fields=fields)

    def bulk_from_csv(self, csv_path: str) -> DBResult:
        db = self.getinstance()
        return db.bulk_from_csv(csv_path=csv_path, model=self._name)

    def bulk(self, records: Union[list[dict], list[tuple]] = []) -> DBResult:
        db = self.getinstance()
        return db.bulk(model=self._name, records=records)
