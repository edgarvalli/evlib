import csv
from pathlib import Path
from dataclasses import dataclass
from contextlib import contextmanager

import mysql.connector.cursor
from .evtypes import DBConfig, DBResult
import mysql.connector as mysqlconnector
import mysql.connector.abstracts
from datetime import datetime
from typing import Union

def build_condition(key: str, cond: str, param: Union[str,int], operator: str = None) -> str:
    if cond == "like":
        param = param.replace("*", "%")  # Usar % en lugar de *

    # Convertir números a cadenas de texto de forma adecuada
    if isinstance(param, str) and not param.isdigit():
        param = f"'{param}'"

    operator_str = ""
    if operator is not None:
        if operator == "|":
            operator_str = " OR "
        else:
            operator_str = " AND "
    return f"{operator_str}{key} {cond} {param}"


def handle_error_result(message: str) -> DBResult:
    result = DBResult()
    result.error = True
    result.message = message
    return result


def isfloat(val: str = None) -> bool:
    if val is None:
        return False

    try:
        float(val)
        return True
    except:
        return False


def isint(val: str = None) -> bool:
    if val is None:
        return False

    try:
        int(val)
        return True
    except:
        return False


@dataclass
class DBConnection:
    connection: mysql.connector.CMySQLConnection
    cursor: mysql.connector.abstracts.MySQLCursorAbstract

    def set_cursor_as_dictionary(self):
        self.cursor = self.connection.cursor(dictionary=True)

    def close(self):
        self.cursor.close()
        self.connection.close()


@dataclass
class Database:

    config: DBConfig = None

    def __init__(self, config: DBConfig = None) -> None:
        if config:
            self.config = config
        else:
            self.config = DBConfig()


    def get_connection(self) -> mysqlconnector.MySQLConnection:
        try:
            return mysqlconnector.connect(**self.config.asdict())

        except mysqlconnector.errors.ProgrammingError as e:
            if e.errno == 1049:
                self.config.database = 'mysql'
                return mysqlconnector.connect(**self.config.asdict())

            raise e
        except KeyError as e:
            raise e

    def database_exists(self, dbname) -> bool:
        exists = True
        query = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{dbname}';"
        sql = self.get_connection()
        cursor = sql.cursor()
        cursor.execute(query)
        dbexists = cursor.fetchone()

        if dbexists is None:
            exists = False

        cursor.close()
        sql.close()

        return exists

    def new_database(self, dbname):
        self.config.database = "mysql"
        query = f"CREATE DATABASE IF NOT EXISTS {dbname}"

        sql = self.get_connection()
        cursor = sql.cursor()
        cursor.execute(query)
        sql.commit()
        self.config.database = dbname

        cursor.close()
        sql.close()

    def table_exists(self, tablename) -> bool:
        exists = False
        alias = "table_exists"
        query = f"""
            SELECT COUNT(*) AS {alias}
            FROM information_schema.tables
            WHERE table_schema = '{self.config.database}'
            AND table_name = '{tablename}';
        """
        sql = self.get_connection()
        cursor = sql.cursor(dictionary=True)
        cursor.execute(query)
        result = cursor.fetchone()
        if result[alias] > 0:
            exists = True
        
        cursor.close()
        sql.close()

        return exists

    def build_query_select(
        self,
        model: str,
        where: list[tuple] = None,
        fields: str = "*",
        limit: Union[str,int] = None,
        orderby: str = None,
        asc: bool = None,
    ) -> str:
        query = f"SELECT {fields} FROM {model}"

        if where:
            conditions = []
            for item in where:

                key, operator, val, *union = item
                union = "OR" if union and union[0] == "|" else "AND"
                val = f"{val}" if isint(val=val) or isfloat(val=val) else f"'{val}'"
                conditions.append(f"{union} {key} {operator} {val}")
                if len(conditions) > 0:
                    if union == "OR":
                        conditions[0] = conditions[0].replace("OR", "").strip()
                    else:
                        conditions[0] = conditions[0].replace("AND", "").strip()

            query += " WHERE " + " ".join(conditions)

        if orderby:
            query += f" ORDER BY {orderby}"

        if asc is not None:
            if asc == True:
                query += " ASC"
            else:
                query += " DESC"

        if limit:
            query += f" LIMIT {limit}"

        return query

    def commit(self, query: str, args: tuple = ()) -> DBResult:
        result = DBResult()
        try:

            cxn = self.get_connection()
            cursor = cxn.cursor()

            cursor.execute(query, args)
            cxn.commit()
            result.error = False
            result.message = "Query executed succesfully."

        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            result = handle_error_result(e.msg)
        finally:
            cursor.close()
            cxn.close()
            return result

    def search(
        self,
        model: str,
        where: list[tuple] = None,
        fields: str = "*",
        limit: str = "50",
        orderby: str = None,
        asc: str = None,
    ) -> DBResult:
        result = DBResult()
        query = self.build_query_select(
            model=model,
            where=where,
            fields=fields,
            limit=limit,
            orderby=orderby,
            asc=asc,
        )

        """
        Searches the database for records matching the specified criteria.

        Args:
            model (str): The name of the model/table to search.
            where (list[tuple], optional): A list of tuples specifying the conditions for the search. Defaults to None.
            fields (str, optional): A comma-separated string of fields to retrieve. Defaults to "*".
            limit (str, optional): The maximum number of records to retrieve. Defaults to "50".
            orderby (str, optional): The field to order the results by. Defaults to None.
            asc (str, optional): Specifies whether the ordering should be ascending. Defaults to None.

        Returns:
            DBResult: An object containing the search results, including columns and data.

        Raises:
            mysqlconnector.Error: If a MySQL error occurs.
            mysqlconnector.DataError: If a data-related error occurs.
            mysqlconnector.DatabaseError: If a database-related error occurs.
            mysqlconnector.ProgrammingError: If a programming error occurs.
            RuntimeError: If a runtime error occurs.
        """

        columns = self.get_description_model(model=model)

        if fields != "*":
            fields = fields.split(",")
            result.columns = [obj for obj in columns if obj["name"] in fields]
        else:
            result.columns = columns

        try:

            sql = self.get_connection()
            cursor: mysql.connector.cursor.MySQLCursor = sql.cursor(dictionary=True)
            cursor.execute(query)
            data = []
            for row in cursor:
                nrow = {}
                for k, v in row.items():
                    if isinstance(v, datetime):
                        nrow[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        nrow[k] = v

                data.append(nrow)

            result.data = data
        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            result = handle_error_result(e.msg)
        except RuntimeError as e:
            result = handle_error_result("")
        except:
            result = handle_error_result(
                "Ocurrio un error al procesar la petición ({})".format(
                    self.config.database
                )
            )

        finally:
            cursor.close()
            sql.close()
            return result


    def between(self, model: str, field: str, first, last, fields="*") -> DBResult:
        result = DBResult()

        if not isinstance(first, int | float):
            first = "'{}'".format(first)

        if not isinstance(last, int | float):
            last = "'{}'".format(last)

        query = f"SELECT {fields} FROM {model} WHERE {field} BETWEEN {first} AND {last}"

        try:

            sql = self.get_connection()
            cursor: mysql.connector.cursor.MySQLCursor = sql.cursor(dictionary=True)
            cursor.execute(query)

            cursor.execute(query)
            data = []
            for row in cursor:
                nrow = {}
                for k, v in row.items():
                    if isinstance(v, datetime):
                        nrow[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        nrow[k] = v

                data.append(nrow)

            result.data = data
                
        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            result = handle_error_result(e.msg)
        except:
            result = handle_error_result(
                "Ocurrio un error al procesar la petición ({})".format(
                    self.config.database
                )
            )

        finally:
            cursor.close()
            sql.close()
            return result

    def save(self, model: str, record: dict) -> DBResult:
        result = DBResult()

        fields = []
        values = ""

        for k, v in record.items():
            if isinstance(v, int):
                values += f"{v},"
            else:
                values += f"'{v}',"
            fields.append(k)

        values = values[:-1]

        query = (
            f"INSERT INTO {self.config.database}.{model} ({','.join(fields)}) VALUES ({values})"
        )

        try:

            sql = self.get_connection()
            cursor: mysql.connector.cursor.MySQLCursor = sql.cursor(dictionary=True)
            cursor.execute(query, record)
            sql.commit()
            lastid = cursor.lastrowid
            result.error = False
            result.message = f"Records inserted with id: {lastid}"
            result.id = lastid
        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            result = handle_error_result(e.msg)
        except:
            result = handle_error_result("Ocurrio un error al procesar la petición")
        finally:
            cursor.close()
            sql.close()
            return result

    def update(self, model: str, data: dict, id: int = None) -> DBResult:
        result = DBResult()
        params = []
        for k, v in data.items():
            if not isinstance(v, (int, float)):
                v = f"'{v}'"
            params.append(f"{k}={v}")

        params = ", ".join(params)

        if not id:
            query = f"UPDATE {model} SET {params}"
        else:
            query = f"UPDATE {model} SET {params} WHERE id={id}"

        try:
            sql = self.get_connection()
            cursor: mysql.connector.cursor.MySQLCursor = sql.cursor(dictionary=True)
            cursor.execute(query)
            sql.commit()
            result.error = False
            result.message = f"Record with id {id} was updated; {cursor.rowcount}"
        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            result = handle_error_result(e.msg)
        finally:
            cursor.close()
            sql.close()
            result.id = id
            return result

    def unlink(self, model: str, id: int) -> DBResult:
        result = DBResult()
        query = "DELETE FROM %s WHERE id=%s"

        try:
            if self.commit(query=query, args=(model, id)):
                result.error = False
                result.message = f"Record with id {id} was removed"
            else:
                result.error = True
                result.message = (
                    "Ocurrio un error al ejecutrar la sentencia ({})".format(query)
                )

            result.id = id

        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            result = handle_error_result(e.msg)
        finally:
            return result

    def findone(self, model: str, id: int, fields: str = "*") -> DBResult:
        result = DBResult()
        result.data = {}
        query = "SELECT {} FROM {} WHERE id={}".format(fields, model, id)
        try:
            sql = self.get_connection()
            cursor: mysql.connector.cursor.MySQLCursor = sql.cursor(dictionary=True)
            cursor.execute(query)
            data = cursor.fetchone()
            for k, v in data.items():
                if isinstance(v, datetime):
                    result.data[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    result.data[k] = v

            result.error = False
            result.columns = self.get_description_model(model=model)
            result.message = f"Record fount {id}"
            result.id = id
        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            result = handle_error_result(e.msg)
        finally:
            cursor.close()
            sql.close()
            return result

    def findoneby(self, model: str, where: list[tuple], fields: str = "*") -> DBResult:
        result = DBResult()
        query = self.build_query_select(model=model, where=where, fields=fields)
        try:

            sql = self.get_connection()
            cursor: mysql.connector.cursor.MySQLCursor = sql.cursor(dictionary=True)

            cursor.execute(query)
            result.data = cursor.fetchone()

            result.id = result.data["id"] if result.data else 0
            result.error = False
            result.columns = self.get_description_model(model=model)
            result.message = f"Record fount {result.id}"
        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            result = handle_error_result(e.msg)
        finally:
            cursor.close()
            sql.close()
            return result

    def bulk_from_csv(self, csv_path: str, model: str = None) -> DBResult:
        result = DBResult()
        csv_path: Path = Path(csv_path)
        if not csv_path.exists():
            result.error = True
            result.message = "Path no exists!!!!"
            return result

        if not csv_path.name.endswith(".csv"):
            result.message = "Is not a csv valid!!!!"
            return result

        if not model:
            model = csv_path.name[:-4]

        print(
            f"Guardando datos en la tabla {model} en la base de datos ({self.config.database})"
        )
        with open(csv_path, mode="r", newline="", encoding="utf-8-sig") as csv_file:
            records = [tuple(row) for row in csv.reader(csv_file)]
            result = self.bulk(model, records)

        return result

    def bulk(self, model: str, records: Union[list[dict], list[tuple]]) -> DBResult:
        result = DBResult()

        if not records:
            result.error = True
            result.message = "The list is empty"
            return result

        if isinstance(records[0], dict):
            fields = records[0].keys()
            values = [tuple(record.values()) for record in records]
        else:
            fields = records[0]  # Los campos ya están definidos
            values = records[1:]

        values_key = ["%s"] * len(fields)

        # Creamos el query
        query = f"INSERT IGNORE INTO {self.config.database}.{model} ({','.join(fields)}) VALUES ({','.join(values_key)})"

        try:
            sql = self.get_connection()
            cursor: mysql.connector.cursor.MySQLCursor = sql.cursor(dictionary=True)

            cursor.executemany(query, values)
            sql.commit()
        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            result = handle_error_result(e.msg)
        finally:
            result.error = False
            result.message = f"Records inserted on {model}; Total: {len(records)}"

            cursor.close()
            sql.close()

            return result

    def get_description_model(self, model: str) -> list[dict]:
        """
        Retrieves the description of the columns for a given model from the database.

        Args:
            model (str): The name of the model (table) to retrieve the column descriptions for.

        Returns:
            list[dict]: A list of dictionaries where each dictionary contains the column name,
                comment, and type for each column in the specified model.

        Raises:
            Exception: If there is an error executing the query or fetching the results, an
                exception is raised with the error message and code.
        """

        query = """
        SELECT COLUMN_NAME name, COLUMN_COMMENT comment, COLUMN_TYPE type
        FROM information_schema.COLUMNS
        WHERE TABLE_NAME = %s AND TABLE_SCHEMA = %s;
        """
        try:
            sql = self.get_connection()
            cursor: mysql.connector.cursor.MySQLCursor = sql.cursor(dictionary=True)
            cursor.execute(query, (model, self.config.database))
            columns = cursor.fetchall()
        except (
            mysqlconnector.Error,
            mysqlconnector.DataError,
            mysqlconnector.DatabaseError,
            mysqlconnector.ProgrammingError,
        ) as e:
            raise "Ocurrio un error: '{}' con codigo {}".format(e.msg, e.errno)

        finally:
            cursor.close()
            sql.close()
            return columns
