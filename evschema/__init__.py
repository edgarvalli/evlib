import inspect
from .database import Database, DBConfig, DBResult, DBConnection
from .models import Model

class EVSchema:

    def __init__(self, dbname: str, config: DBConfig = None):
        self.dbname = dbname
        if config:
            self.config = config
        else:
            self.config = DBConfig()

        self.config.dbname = dbname
        self.models_list: list[Model] = []

    def register_model(self, model):
        if getattr(model, "build") or callable(model.build):
            self.models_list.append(model)

    def database_exists(self) -> bool:
        db = Database(config=self.config)
        return db.database_exists(self.dbname)

    def verify_integrity_schema(self):
        for model in self.models_list:
            excludes = ["_name","_description"]
            members = inspect.getmembers(model, lambda a: not (inspect.isroutine(a)))
            members = [
                item[0]
                for item in members
                if not item[0].startswith("__") or not item[0].endswith("__")
            ]
            members = [item for item in members if not item in excludes]
            
            for member in members:
                print("Verifying integrity of {} in database {}".format(member, self.dbname))


    def import_models_from_path(self, models_path: str):
        import importlib
        from pathlib import Path

        models_path: Path = Path(models_path)

        if not models_path.exists():
            raise ValueError("La ruta no existe!!!")

        # Se lee todos los arhivos del paquete schema
        for model_path in models_path.iterdir():
            # Se excluye los archivos que empiezan con __
            if model_path.name.startswith("__"):
                continue

            # Se formatea el nombre del modulo a importar
            pkgname = model_path.name.replace(".py", "")
            pkgname = f"{models_path.name}.{pkgname}"

            # Se importa el modelo
            pkg = importlib.import_module(name=pkgname)

            # Se busca las clases en el paquete
            for name, obj in inspect.getmembers(pkg):
                if inspect.isclass(obj):
                    print("Importando el modelo {}".format(name))
                    self.register_model(obj)
    
    def inflate_from_csv(self, data_path: str) -> str:
        from pathlib import Path

        _data_path = Path(data_path)

        if not _data_path.exists():
            return "La ruta de datos no existe"
        
        def parse_int(param):
            try:
                return int(param)
            except:
                return str(param)
            
        def format_dict(obj: dict):
            new_obj = {}
            for key in obj.keys():
                new_obj[key] = parse_int(obj[key])
            return new_obj
            
        db = Database()
        db.config = self.config

        for data_file in _data_path.iterdir():
            if data_file.is_file():
                if str(data_file).endswith('.csv'):
                    model_name = data_file.name.replace('.csv','')
                    
                    with open(str(data_file), newline='', encoding='utf-8') as f:
                        import csv
                        data = csv.DictReader(f)
                        print(model_name)

                        
                        for row in data:
                            row = format_dict(row)
                            r = db.save(model_name, row)

                            print(r.asdict())


    def createdb(self) -> bool:
        try:
            db = Database()
            db.config = self.config
            db.new_database(dbname=self.dbname)

            model_list = []

            for model in self.models_list:
                model: Model = model()
                data = (model._name, model._description)
                model_list.append(data)
                model.build(self.config)

            line = ""

            for _ in range(100):
                line += "#"

            print(line)

            
            # for name, desc in model_list:
            #     if not desc:
            #         desc = ""

            #     db.save("models", {"name": name, "description": desc})
            
            return True
        except:
            return False
