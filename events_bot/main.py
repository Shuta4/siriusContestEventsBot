from datetime import datetime
import logging
import os
import telebot
import qrcode
import messages
from data.users import User, Users, PermissionsLevels, ActionTypes
from data.events import Events, Event
from data.tickets import Ticket, Tickets


logging.basicConfig(level=logging.INFO, format="%(asctime)s::%(levelname)s::%(message)s", datefmt="%Y-%m-%dT%H:%M:%S")

logging.debug("Starting bot")

logging.debug("Getting environment variables...")
try:
    import envars
except EnvironmentError as e:
    logging.error(e)
    exit(1)
logging.debug("Got environment variables.")

# Connect to db

db_path = envars.db_path
logging.debug(f"Checking DataBase path '{db_path}'...")

if not os.path.exists(db_path):
    logging.info(f"Creating new DataBase in '{db_path}'...")
    import data

    data.init_db(db_path)
    logging.info(f"Created new DataBase.")

if not os.path.isfile(db_path):
    logging.error(f"Incorrect DataBase path '{db_path}'.")
    exit(1)

logging.debug("DataBase path exists.")

# Update permissions for admin users

logging.debug("Setting permissions level for admin users...")

for admin_user_id in envars.admin_users:

    admin_user = Users.get(admin_user_id)
    if admin_user is None:
        logging.debug("Creating new admin user")
        admin_user = User()

    admin_user.telegram_id = admin_user_id
    admin_user.permissions_level = PermissionsLevels.ADMIN

    admin_user.write()

logging.debug("Set permissions level for admin users.")

# Create Telegram Bot

logging.debug("Creating bot...")
bot = telebot.TeleBot(envars.bot_token, parse_mode="MARKDOWN")
logging.debug("Bot created.")

# Set handlers

logging.debug("Setting messages handlers...")


def try_wrapper(func):
    def wrap(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as err:
            logging.error(f"Unknown error: {err}")
    return wrap


def handlers_wrapper(permissions_level=PermissionsLevels.USER):
    """
    Wrapper for all message handlers.
    Provides some checks and manages user in db.
    """

    @try_wrapper
    def decorator(func):
        def wrap(message):
            logging.debug(f"Got new message on {func.__name__} handler")

            # Check chat as this bot will not work in groups

            if message.chat.type != 'private':
                bot.reply_to(message, messages.only_private_chats())
                bot.leave_chat(message.chat.id)
                logging.debug(f"Left non-private chat with id '{message.chat.id}'")
                return

            # Check user

            telegram_user_id = message.from_user.id

            logging.debug(f"Getting information about user with tgId '{telegram_user_id}' from DB.")

            user = Users.get(telegram_user_id)

            logging.debug(f"Got information about user with tgId '{telegram_user_id}', user exist: {user is not None}")

            if user is None:
                logging.debug(f"Creating new user with tgId '{telegram_user_id}'...")

                user = User()
                user.telegram_id = telegram_user_id
                user.write()

                logging.debug(f"Created user with tgId '{telegram_user_id}' and id '{user.id}'.")
                logging.info(f"New user with telegram_id = '{telegram_user_id}'")

            if user.permissions_level < permissions_level:
                logging.debug(f"No permissions for action '{func.__name__}' by user '{telegram_user_id}'.")
                bot.reply_to(message, messages.no_permissions())
                return

            func(message, user)

        return wrap

    return decorator


@bot.message_handler(commands=['start', 'help'])
@handlers_wrapper(permissions_level=PermissionsLevels.USER)
def bot_start(message, user):
    user.action = ActionTypes.IDLE
    user.write()
    bot.reply_to(message, messages.welcome_and_help(user.permissions_level >= PermissionsLevels.ADMIN))


def _get_events_keyboard(events):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    for event in events:
        keyboard.add(telebot.types.InlineKeyboardButton(
            text=f"{datetime.fromtimestamp(event['datetime']).strftime(messages.dt_format)}: {event['name']}",
            callback_data=event['id']
        ))

    return keyboard


@bot.message_handler(commands=['events'])
@handlers_wrapper(permissions_level=PermissionsLevels.USER)
def get_events(message, user):
    user.action = ActionTypes.SELECT_EVENT
    user.write()

    events = Events.get_events_print_info(True)
    bot.reply_to(message, messages.events_list(events), reply_markup=_get_events_keyboard(events))


@bot.message_handler(commands=['tickets'])
@handlers_wrapper(permissions_level=PermissionsLevels.USER)
def get_tickets(message, user):
    tickets = Tickets.get_user_tickets_for_print(user.id)
    if len(tickets) == 0:
        bot.reply_to(message, messages.no_tickets())
        return

    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)

    for ticket in tickets:
        keyboard.add(telebot.types.InlineKeyboardButton(
            text=f"{datetime.fromtimestamp(ticket['datetime']).strftime(messages.dt_format)} "
                 f"{ticket['name']}: {ticket['members']} мест",
            callback_data=ticket['id']
        ))

    user.action = ActionTypes.SELECT_TICKET
    user.write()

    bot.reply_to(message, messages.tickets_list_title(), reply_markup=keyboard)


@bot.message_handler(commands=['newevent'])
@handlers_wrapper(permissions_level=PermissionsLevels.ADMIN)
def new_event(message, user):
    user.action = ActionTypes.ENTER_NEW_EVENT_PARAMS
    user.write()
    bot.reply_to(message, messages.new_event_start())


@bot.message_handler(commands=['allevents'])
@handlers_wrapper(permissions_level=PermissionsLevels.ADMIN)
def get_all_events(message, user):
    user.action = ActionTypes.SELECT_EVENT
    user.write()

    events = Events.get_events_print_info(False)
    bot.reply_to(message, messages.events_list(events), reply_markup=_get_events_keyboard(events))


def send_qrcode(chat_id, user, ticket):
    from urllib.parse import quote
    import io

    def image_to_byte_array(image):
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr

    event = ticket.event

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(
        f"ticket://{ticket.id}"
        f"?datetime={event.datetime.isoformat()}"
        f"&name={quote(event.name.encode('cp1251'))}"
        f"&members={ticket.members}"
    )
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    bot.send_photo(chat_id, image_to_byte_array(img), caption=messages.ticket_caption(ticket))

    user.action = ActionTypes.IDLE
    user.write()


@bot.callback_query_handler(func=lambda cb: True)
@try_wrapper
def query_handler(callback_query):
    logging.debug("Starting query_handler")

    user = Users.get(callback_query.from_user.id)
    if user is None:
        bot.answer_callback_query(callback_query.id, messages.unknown_user())
        return

    if user.action == ActionTypes.SELECT_EVENT or \
            user.action == ActionTypes.SELECT_ACTION_ON_EVENT:

        if user.action == ActionTypes.SELECT_ACTION_ON_EVENT:
            event_id = user.action_data
        else:
            event_id = callback_query.data

        event = Events.get(event_id)
        if event is None:
            bot.answer_callback_query(callback_query.id, messages.unknown_event())
            return

        bot.answer_callback_query(callback_query.id)

        if user.action == ActionTypes.SELECT_EVENT:
            markup = telebot.types.InlineKeyboardMarkup(row_width=1)
            markup.add(telebot.types.InlineKeyboardButton(text="Записаться", callback_data="signup"))
            if user.permissions_level >= PermissionsLevels.ADMIN:
                markup.add(telebot.types.InlineKeyboardButton(text="Редактировать", callback_data="edit"))

            user.action = ActionTypes.SELECT_ACTION_ON_EVENT
            user.action_data = event.id
            user.write()

            bot.send_message(
                callback_query.message.chat.id,
                messages.full_event_information(event),
                reply_markup=markup
            )
        else:
            if callback_query.data == "signup":
                user.action = ActionTypes.ENTER_TICKET_MEMBERS
                user.action_data = event.id
                user.write()
                bot.send_message(
                    callback_query.message.chat.id,
                    messages.enter_ticket_members()
                )
            elif callback_query.data == "edit":
                if user.permissions_level < PermissionsLevels.ADMIN:
                    bot.send_message(callback_query.message.chat.id, messages.no_permissions())
                    return

                user.action = ActionTypes.ENTER_EVENT_PARAMS
                user.action_data = event.id
                user.write()

                bot.send_message(callback_query.message.chat.id, messages.edit_event_start())

    elif user.action == ActionTypes.SELECT_TICKET:
        ticket = Tickets.get(callback_query.data)
        if ticket is None:
            bot.answer_callback_query(callback_query.id, messages.unknown_ticket())
            return

        send_qrcode(callback_query.message.chat.id, user, ticket)

    else:
        bot.answer_callback_query(callback_query.id, messages.not_recognized())


@bot.message_handler(content_types=['text'])
@handlers_wrapper(permissions_level=PermissionsLevels.ADMIN)
def text_handler(message, user):
    def event_from_message(_event):
        lines = message.text.split('\n')

        if len(lines) < 2:
            raise ValueError("Necessary params name and datetime is not defined.")

        _name = lines[0]
        _datetime = datetime.strptime(lines[1], messages.dt_format)
        _location = ""
        _max_members = 0

        if len(lines) > 2:
            _location = lines[2]

        if len(lines) > 3:
            _max_members = int(lines[3])

        _event.name = _name
        _event.datetime = _datetime
        _event.location = _location
        _event.max_members = _max_members
        _event.description = ""

        _event.write()
        return _event

    if user.action == ActionTypes.ENTER_NEW_EVENT_PARAMS or \
            user.action == ActionTypes.ENTER_EVENT_PARAMS:

        if user.action == ActionTypes.ENTER_EVENT_PARAMS:
            event = Events.get(user.action_data)
        else:
            event = Event()

        _old_description = event.description

        try:
            event = event_from_message(event)
        except ValueError:
            bot.reply_to(message, messages.not_recognized())
            return

        if user.action == ActionTypes.ENTER_EVENT_PARAMS:
            bot.reply_to(message, messages.enter_edited_event_description(_old_description))
        else:
            bot.reply_to(message, messages.enter_new_event_description())

        user.action = ActionTypes.ENTER_EVENT_DESCRIPTION
        user.action_data = event.id
        user.write()

    elif user.action == ActionTypes.ENTER_EVENT_DESCRIPTION:

        event = Events.get(user.action_data)
        event.description = message.text
        event.write()

        user.action = ActionTypes.IDLE
        user.write()

        bot.reply_to(message, messages.description_saved())

    elif user.action == ActionTypes.ENTER_TICKET_MEMBERS:

        try:
            _members = int(message.text)
        except Exception as err:
            logging.debug(f"Incorrect members input: {err}")
            bot.reply_to(message, messages.members_must_be_int())
            return

        ticket = Ticket()
        ticket.user = user
        ticket.event = user.action_data

        _event = ticket.event
        _available_places = _event.available_places
        if _event.max_members != 0 and \
                _available_places < _event.max_members:
            bot.reply_to(message, messages.too_many_members(_available_places))
            return

        ticket.members = _members
        ticket.write()

        send_qrcode(message.chat.id, user, ticket)

    else:
        bot.reply_to(message, messages.not_recognized())


@bot.message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document',
                                                               'location', 'contact', 'sticker'])
@try_wrapper
def default_command(message):
    bot.reply_to(message, messages.unsupported_type())


logging.debug("Set messages handlers.")

# Start Polling

logging.debug("Bot starts polling...")

bot.polling()

logging.debug("Bot stopped polling.")
