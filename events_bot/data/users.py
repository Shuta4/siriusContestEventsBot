from data.basic import DataObject, search_by_unique_value

DB_TABLE = "users"
DB_TELEGRAM_ID = "telegramId"
DB_PERMISSIONS_LEVEL = "permissionsLevel"
DB_ACTION = "action"
DB_ACTION_DATA = "actionData"


class PermissionsLevels:
    """
    Enumeration for permissions levels.
    BANNED - can't interact with bot.
    USER - standard level, can read events information and sign up for them.
    ADMIN - can read/write events information.
    """

    BANNED = 0
    USER = 1
    ADMIN = 2


class ActionTypes:
    """
    Enumeration defines user-action types.
    """

    # Nothing happens
    IDLE = ""

    # User should click on inline keyboard
    SELECT_EVENT = "SELECT_EVENT"
    SELECT_TICKET = "SELECT_TICKET"
    SELECT_ACTION_ON_EVENT = "SELECT_ACTION_ON_EVENT"

    # User should send message with text
    ENTER_NEW_EVENT_PARAMS = "ENTER_NEW_EVENT_PARAMS"
    ENTER_EVENT_PARAMS = "ENTER_EVENT_PARAMS"
    ENTER_EVENT_DESCRIPTION = "ENTER_EVENT_DESCRIPTION"
    ENTER_TICKET_MEMBERS = "ENTER_TICKET_MEMBERS"



class User(DataObject):

    def __init__(self, row=None):
        """
        Manages one 'users' table object.
        :param row: Dict or Row object where keys is table's columns' names
        """

        # Initializing instance variables

        super().__init__(DB_TABLE, row)
        self._telegram_id = ""
        self._permissions_level = PermissionsLevels.USER
        self._action = ActionTypes.IDLE
        self._action_data = ""

        if row is None:
            # Creating new user
            return

        self._telegram_id = row[DB_TELEGRAM_ID]
        self._permissions_level = row[DB_PERMISSIONS_LEVEL]
        self._action = row[DB_ACTION]
        self._action_data = row[DB_ACTION_DATA]

    # Public properties

    @property
    def telegram_id(self):
        """
        Telegram User Id
        """
        return self._telegram_id

    @telegram_id.setter
    @DataObject._setter
    def telegram_id(self, value):
        self._telegram_id = value

    @property
    def permissions_level(self):
        """
        User's permissions level defines what commands can user execute.
        """
        return self._permissions_level

    @permissions_level.setter
    @DataObject._setter
    def permissions_level(self, value):
        if value != PermissionsLevels.BANNED and value != PermissionsLevels.USER and value != PermissionsLevels.ADMIN:
            raise ValueError(
                f"Permissions Level only accept values: "
                f"{[PermissionsLevels.BANNED, PermissionsLevels.USER, PermissionsLevels.ADMIN]} "
                f"but not {value}."
            )

        self._permissions_level = value

    @property
    def action(self):
        return self._action

    @action.setter
    @DataObject._setter
    def action(self, value):
        if value == ActionTypes.IDLE:
            self.action_data = ""
        self._action = value

    @property
    def action_data(self):
        return self._action_data

    @action_data.setter
    @DataObject._setter
    def action_data(self, value):
        self._action_data = value

    # Instance methods

    def write(self):
        """
        Creates or updates user in database
        """

        super(User, self).write({
            DB_TELEGRAM_ID: self._telegram_id,
            DB_PERMISSIONS_LEVEL: self._permissions_level,
            DB_ACTION: self._action,
            DB_ACTION_DATA: self._action_data
        })


class Users:

    @staticmethod
    def get(user_id):
        """
        Gets User instance by its internal or telegram id.
        :param user_id: User's internal db id or telegram user id.
        :return: If User exist returns its instance else returns None.
        """

        if isinstance(user_id, str):
            row = search_by_unique_value(DB_TABLE, user_id)
        elif isinstance(user_id, int):
            row = search_by_unique_value(DB_TABLE, user_id, DB_TELEGRAM_ID)
        else:
            raise TypeError("user_id must be string or integer.")

        if row is None:
            return None

        return User(row)
