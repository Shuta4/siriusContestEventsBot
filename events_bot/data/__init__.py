
def init_db(path):
    import sqlite3
    from data import tickets
    from data.basic import DB_ID
    import data.users as users
    import data.events as events

    connection = sqlite3.connect(path)

    cursor = connection.cursor()
    cursor.executescript(
        f"CREATE TABLE {users.DB_TABLE} ("
        f"{DB_ID} TEXT NOT NULL UNIQUE,"
        f"{users.DB_TELEGRAM_ID} INTEGER NOT NULL UNIQUE,"
        f"{users.DB_PERMISSIONS_LEVEL} INTEGER NOT NULL,"
        f"{users.DB_ACTION} TEXT NOT NULL,"
        f"{users.DB_ACTION_DATA} TEXT NOT NULL,"
        f"PRIMARY KEY({DB_ID})"
        f") WITHOUT ROWID;"
        f"CREATE TABLE {events.DB_TABLE} ("
        f"{DB_ID} TEXT NOT NULL UNIQUE,"
        f"{events.DB_NAME} TEXT NOT NULL,"
        f"{events.DB_DATETIME} INTEGER NOT NULL,"
        f"{events.DB_LOCATION} TEXT NOT NULL,"
        f"{events.DB_MAX_MEMBERS} INTEGER NOT NULL,"
        f"{events.DB_DESCRIPTION} TEXT NOT NULL,"
        f"PRIMARY KEY({DB_ID})"
        f") WITHOUT ROWID;"
        f"CREATE TABLE {tickets.DB_TABLE} ("
        f"{DB_ID} TEXT NOT NULL UNIQUE,"
        f"{tickets.DB_USER} TEXT NOT NULL,"
        f"{tickets.DB_EVENT} TEXT NOT NULL,"
        f"{tickets.DB_MEMBERS} INTEGER NOT NULL,"
        f"PRIMARY KEY({DB_ID})"
        f") WITHOUT ROWID;"
    )

    connection.commit()
