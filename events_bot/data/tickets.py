from datetime import datetime, timedelta
from data.basic import DataObject, search_by_unique_value
from data.events import Events, Event
from data.users import User, Users

DB_TABLE = "tickets"
DB_USER = "user"
DB_EVENT = "event"
DB_MEMBERS = "members"


class Ticket(DataObject):

    def __init__(self, row=None):
        """
        Manages one 'tickets' table object.
        :param row: Dict or Row object where keys is table's columns' names
        """

        # Initializing instance variables

        super().__init__(DB_TABLE, row)
        self._user = ""
        self._event = ""
        self._members = 0

        if row is None:
            # Creating new user
            return

        self._user = row[DB_USER]
        self._event = row[DB_EVENT]
        self._members = row[DB_MEMBERS]

    # Public properties

    @property
    def user(self):
        return Users.get(self._user)

    @user.setter
    @DataObject._setter
    def user(self, value):
        if isinstance(value, str):
            self._user = value

        elif isinstance(value, int):
            _user = Users.get(value)
            if _user is None:
                self._user = ""
            else:
                self._user = _user.id

        elif isinstance(value.__class__, User.__class__):
            self._user = value.id

        else:
            raise TypeError(f"Can not assign type '{type(value)}' when 'user' type is 'User.id'.")

    @property
    def event(self):
        return Events.get(self._event)

    @event.setter
    @DataObject._setter
    def event(self, value):
        if isinstance(value, str):
            self._event = value

        elif isinstance(value.__class__, Event.__class__):
            self._event = value.id

        else:
            raise TypeError(f"Can not assign type '{type(value)}' when 'event' type is 'Event.id'.")

    @property
    def members(self):
        return self._members

    @members.setter
    @DataObject._setter
    def members(self, value):
        if value < 0 or value != int(value):
            raise ValueError("Members value should be above '0' integer.")

        self._members = value

    # Instance methods

    def write(self):

        if self._user is None or self._event is None:
            raise ValueError('User and event must be filled before writing to DataBase.')

        super(Ticket, self).write({
            DB_USER: self._user,
            DB_EVENT: self._event,
            DB_MEMBERS: self.members
        })


class Tickets:

    @staticmethod
    def get(ticket_id):

        if isinstance(ticket_id, str):
            row = search_by_unique_value(DB_TABLE, ticket_id)
        else:
            raise TypeError("ticket_id must be string.")

        if row is None:
            return None

        return Ticket(row)

    @staticmethod
    def get_user_tickets_for_print(user_id):
        import sqlite3
        import envars
        from data import events
        from data.basic import DB_ID

        connection = sqlite3.connect(envars.db_path)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()

        result = []
        for row in cursor.execute(
                f"SELECT "
                f"  {DB_TABLE}.{DB_ID} AS id, "
                f"  {DB_TABLE}.{DB_MEMBERS} AS members, "
                f"  {events.DB_TABLE}.{events.DB_NAME} AS name, "
                f"  {events.DB_TABLE}.{events.DB_DATETIME} AS datetime "
                f"FROM {DB_TABLE} AS {DB_TABLE} INNER JOIN {events.DB_TABLE} AS {events.DB_TABLE} "
                f"  ON {DB_TABLE}.{DB_EVENT} = {events.DB_TABLE}.{DB_ID} "
                f"WHERE {DB_TABLE}.{DB_USER} = :user_id AND {events.DB_TABLE}.{events.DB_DATETIME} >= :datetime",
                {"user_id": user_id, "datetime": (datetime.now() - timedelta(1)).timestamp()}
        ):
            result.append(dict(row))

        connection.close()
        return result
