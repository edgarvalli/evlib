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

            """
            for name, desc in model_list:
                if not desc:
                    desc = ""

                db.save("models", {"name": name, "description": desc})
            """
            return True
        except:
            return False
