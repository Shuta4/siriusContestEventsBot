import os

"""
envars.py provides quick access for environmental variables.
"""


def _get_env_var(name, default_value=None):
    _prefix = "EVENTS_BOT_"
    _name = f"{_prefix}{name}"
    result = os.getenv(_name, default_value)
    if result is None:
        raise EnvironmentError(f"Required environment variable {_name} is not specified")
    return result


"""
Telegram Bot Token
"""
bot_token = _get_env_var("TOKEN")

"""
Path to .db file with sqlite database
"""
db_path = _get_env_var("DB")

"""
Admin users telegram ids separated by :
"""
admin_users = [int(x) for x in _get_env_var("ADMIN_USERS", "").split(':') if x != ""]
