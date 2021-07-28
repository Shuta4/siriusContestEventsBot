from data.basic import DataObject, search_by_unique_value
from datetime import datetime

DB_TABLE = 'events'
DB_NAME = 'name'
DB_DATETIME = 'datetime'
DB_LOCATION = 'location'
DB_MAX_MEMBERS = 'maxMembers'
DB_DESCRIPTION = 'description'


class Event(DataObject):

    def __init__(self, row=None):
        super().__init__(DB_TABLE, row)

        self._name = ""
        self._datetime = datetime.fromtimestamp(0)
        self._location = ""
        self._max_members = 0
        self._description = ""

        if row is None:
            return

        self._name = row[DB_NAME]
        self._datetime = datetime.fromtimestamp(row[DB_DATETIME])
        self._location = row[DB_LOCATION]
        self._max_members = row[DB_MAX_MEMBERS]
        self._description = row[DB_DESCRIPTION]

    @property
    def name(self):
        return self._name

    @name.setter
    @DataObject._setter
    def name(self, value):
        self._name = value

    @property
    def datetime(self):
        return self._datetime

    @datetime.setter
    @DataObject._setter
    def datetime(self, value):
        self._datetime = value

    @property
    def location(self):
        return self._location

    @location.setter
    @DataObject._setter
    def location(self, value):
        self._location = value

    @property
    def max_members(self):
        return self._max_members

    @max_members.setter
    @DataObject._setter
    def max_members(self, value):
        self._max_members = value

    @property
    def description(self):
        return self._description

    @description.setter
    @DataObject._setter
    def description(self, value):
        self._description = value

    def write(self):
        super(Event, self).write({
            DB_NAME: self._name,
            DB_DATETIME: self._datetime.timestamp(),
            DB_LOCATION: self._location,
            DB_MAX_MEMBERS: self._max_members,
            DB_DESCRIPTION: self._description,
        })


class Events:

    @staticmethod
    def get(event_id):
        row = search_by_unique_value(DB_TABLE, event_id)
        if row is None:
            return None
        return Event(row)

    @staticmethod
    def get_events_print_info(available_only):
        import sqlite3
        import envars
        from data.basic import DB_ID
        from data.tickets import DB_EVENT, DB_MEMBERS
        from data import tickets

        connection = sqlite3.connect(envars.db_path)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        sql_search = ""
        if available_only:
            sql_search = \
                f"WHERE " \
                f"  (temp_events.available_places > 0 OR {DB_TABLE}.{DB_MAX_MEMBERS} = 0) AND " \
                f"  {DB_TABLE}.{DB_DATETIME} > :current_time "

        cursor.execute(
            f"CREATE TEMP TABLE IF NOT EXISTS temp_events AS SELECT "
            f"  {DB_TABLE}.{DB_ID} as {DB_ID}, "
            f"  CASE "
            f"      WHEN {DB_TABLE}.{DB_MAX_MEMBERS} - sum(IFNULL({tickets.DB_TABLE}.{DB_MEMBERS}, 0)) <= 0 "
            f"          THEN 0 "
            f"      ELSE {DB_TABLE}.{DB_MAX_MEMBERS} - sum(IFNULL({tickets.DB_TABLE}.{DB_MEMBERS}, 0)) "
            f"  END as available_places "
            f"FROM {DB_TABLE} LEFT JOIN {tickets.DB_TABLE} "
            f"  ON {DB_TABLE}.{DB_ID} = {tickets.DB_TABLE}.{DB_EVENT} "
            f"GROUP BY {DB_TABLE}.{DB_ID} "
        )

        result = []
        for row in cursor.execute(
                f"SELECT "
                f"  {DB_TABLE}.{DB_ID} AS id, "
                f"  {DB_TABLE}.{DB_NAME} AS name, "
                f"  {DB_TABLE}.{DB_DATETIME} AS datetime, "
                f"  {DB_TABLE}.{DB_MAX_MEMBERS} AS max_members, "
                f"  {DB_TABLE}.{DB_LOCATION} AS location, "
                f"  temp_events.available_places AS available_places "
                f"FROM {DB_TABLE} INNER JOIN temp.temp_events AS temp_events "
                f"  ON {DB_TABLE}.{DB_ID} = temp_events.{DB_ID} "
                f"{sql_search}"
                f";",
                {"current_time": int(datetime.now().timestamp())}
        ):
            result.append(dict(row))

        connection.close()
        return result
