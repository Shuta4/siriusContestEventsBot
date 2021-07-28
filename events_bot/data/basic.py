import sqlite3
import uuid

import envars

DB_ID = "id"


class DataObject:

    def __init__(self, table, obj):
        self._connection = sqlite3.connect(envars.db_path)
        self._table = table
        self._has_changes = False
        self._id = ""

        if obj is None:
            self._has_changes = True
            return

        self._id = obj[DB_ID]

    def _setter(func):
        def wrap(self, value):
            func(self, value)
            self._has_changes = True
        return wrap

    @property
    def id(self):
        """
        Object's unique identifier in DataBase
        """
        return self._id

    @id.setter
    @_setter
    def id(self, value):
        """
        Allows to set predefined id for new object.
        Does not control id unique!
        """
        if self._id != "":
            raise ValueError("Can't change id value when it is already filled.")
        self._id = value

    def write(self, *args):

        if not self._has_changes:
            # If nothing changed no need to touch database
            return

        cursor = self._connection.cursor()

        create_new = False
        if self._id == "":
            # Generates random uuid for new object in db
            self._id = str(uuid.uuid4())
            create_new = True

        obj_dict = {
            DB_ID: self._id
        }
        if len(args) > 0:
            obj_dict.update(args[0])

        if create_new:

            sql_columns = ""
            sql_values = ""
            for key in obj_dict:
                sql_columns += f", {key}"
                sql_values += f", :{key}"

            cursor.execute(
                f"INSERT INTO {self._table} ({DB_ID}{sql_columns}) VALUES (:{DB_ID}{sql_values})",
                obj_dict
            )

        else:
            if len(obj_dict) == 1:
                return

            sql = ""
            for key in obj_dict:
                if key == DB_ID:
                    continue
                sql += f"{key} = :{key},"
            sql = sql.removesuffix(',')

            cursor.execute(
                f"UPDATE {self._table} SET {sql} "
                f"WHERE {DB_ID} = :{DB_ID}",
                obj_dict
            )

        cursor.close()
        self._connection.commit()
        self._has_changes = False

    def __del__(self):
        self._connection.close()


def search_by_unique_value(table, value, search=DB_ID):
    connection = sqlite3.connect(envars.db_path)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    result = None
    for row in cursor.execute(
            f"SELECT * FROM {table} WHERE {search} = :search_value",
            {"search_value": value}
    ):
        result = row
        break

    connection.close()
    return result
