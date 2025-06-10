class _Column:
    label: str
    unique: bool
    default: str | bool
    index: bool
    field_type: str
    null: bool  # Nuevo atributo para indicar si el campo acepta valores nulos.

    def __repr__(self):
        return f"<{self.__class__.__name__} label={self.label} type={self.field_type}>"

    def parse_kvargs(self, kvargs: dict):
        self.default = kvargs.get("default", None)
        self.unique = bool(kvargs.get("unique", False))
        self.index = bool(kvargs.get("index", False))
        self.null = bool(
            kvargs.get("null", True)
        )  # Por defecto, los campos aceptan nulos.

        if self.default is not None and not isinstance(
            self.default, (str, int, float, bool)
        ):
            raise ValueError("The 'default' value must be of type str, int, or float.")

    def get_mysql_field(self) -> str:
        field = f"{self.field_type}"

        if self.null:
            field += " NULL"
        else:
            field += " NOT NULL"

        if self.default is not None:
            if isinstance(self.default, str):
                field += f" DEFAULT '{self.default}'"

            elif isinstance(self.default, bool):
                if self.default:
                    field += f" DEFAULT 1"
                else:
                    field += f" DEFAULT 0"
            else:
                field += f" DEFAULT {self.default}"

        if self.unique:
            field += " UNIQUE"

        field += f" COMMENT '{self.label}'"
        return field


class Char(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.size = kvargs.get("size", 100)
        self.field_type = f"VARCHAR({self.size})"


class Bool(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "TINYINT(1)"


class Integer(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "INT"


class BigInteger(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "BIGINT"


class Float(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "FLOAT"


class Text(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "TEXT"


class LongText(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "LONGTEXT"


class DateTime(_Column):
    def __init__(self, label: str, **kvargs) -> None:
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "DATETIME"


class UUID(_Column):
    def __init__(self, label: str, **kvargs):
        self.parse_kvargs(kvargs=kvargs)
        self.label = label
        self.field_type = "CHAR(36)"
