import sys
import inspect
import importlib.util
from pathlib import Path
from typing import Union
from .evtypes import DBConfig


def generate_database(config: DBConfig, models_path: Union[str, Path]) -> dict:
    """
    Genera la base de datos y sus tablas basándose en los modelos definidos en un directorio.

    :param config: Configuración de la base de datos.
    :param models_path: Ruta al directorio donde se encuentran los modelos.
    :return: Diccionario con el resultado del proceso.
    """
    from .database import Database  # Importación interna
    response = {"error": True, "message": ""}

    # Validación del directorio de modelos
    models_path = Path(models_path) if isinstance(models_path, str) else models_path
    if not models_path.exists():
        response["message"] = f"The path '{models_path}' doesn't exist."
        return response
    if not models_path.is_dir():
        response["message"] = f"The path '{models_path}' is not a directory."
        return response

    # Creación de la base de datos
    try:
        db = Database()
        db.config = config
        print(f"Creating database with name '{db.config.dbname}'...")
        db.new_database(db.config.dbname)
    except Exception as e:
        response["message"] = f"Failed to create database: {e}"
        return response

    # Procesar modelos en el directorio
    try:
        for model in models_path.iterdir():
            if model.name == "__pycache__" or not model.name.endswith(".py"):
                continue

            if model.name == "__init__.py":
                continue

            # Importación dinámica del módulo
            model_name = model.stem
            print(f"Processing model: {model_name}")
            spec = importlib.util.spec_from_file_location(model_name, model)
            module = importlib.util.module_from_spec(spec)
            sys.modules[model_name] = module
            spec.loader.exec_module(module)

            # Inspección de clases dentro del módulo
            modules = inspect.getmembers(module, inspect.isclass)
            for _, obj in modules:
                if hasattr(obj, "build") and callable(getattr(obj, "build", None)):
                    class_instance = obj()  # Instanciar la clase
                    print(f"Building model: {obj.__name__}")
                    class_instance.build(config)  # Llamar al método 'build'

        response["error"] = False
        response["message"] = (
            f"Database '{db.config.dbname}' and models created successfully."
        )
    except Exception as e:
        response["message"] = f"Error processing models: {e}"

    return response


def is_bidimensional(tup: tuple) -> bool:
    """
    Verifica si un objeto es una estructura bidimensional (tupla de tuplas/listas).

    :param tup: Objeto a verificar.
    :return: `True` si es bidimensional, de lo contrario `False`.
    """
    return isinstance(tup, tuple) and all(isinstance(i, (tuple, list)) for i in tup)
