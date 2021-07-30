#!/bin/bash

export EVENTS_BOT_TOKEN=""
export EVENTS_BOT_DB=""
export EVENTS_BOT_ADMIN_USERS=""

exec python "./events_bot/main.py" &>>"./bot.log" &
