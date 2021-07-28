
dt_format = "%d.%m.%Y %H:%M"


def enter_help():
    return f"Введите /help для получения информации."


def unsupported_type():
    return f"Такие сообщения не поддерживаются.\n" \
           f"{enter_help()}"


def only_private_chats():
    return f"Я работаю только в приватных чатах."


def no_permissions():
    return f"Недостаточно прав для этого действия."


def not_recognized():
    return f"Я вас не понимаю.\n" \
           f"{enter_help()}"


def welcome_and_help(is_admin):
    admin_commands = ''
    if is_admin:
        admin_commands = f"\n" \
                         f"*Команды администратора:*\n" \
                         f"/newevent - создать новое мероприятие\n" \
                         f"/allevents - список всех мероприятий"

    return f"Я могу записать тебя на мероприятия, " \
           f"проходящие на [Федеральной территории Сириус](https://sirius-ft.ru/)\n" \
           f"\n" \
           f"*Команды:*\n" \
           f"/events - список доступных мероприятий\n" \
           f"/tickets - список ваших билетов на мероприятия{admin_commands}"


def events_list(events):
    if len(events) == 0:
        return f"Нет доступных мероприятий."

    from datetime import datetime

    result = f"*Мероприятия:*\n"
    for event in events:

        if event['max_members'] == 0:
            available_places = "без ограничения на кол-во участников"
        else:
            available_places = f"мест: {event['available_places']}/{event['max_members']}"

        result += f"`{datetime.fromtimestamp(event['datetime']).strftime(dt_format)}`: " \
                  f"*{event['name']}*: " \
                  f"{event['location']}: " \
                  f"{available_places}\n"

    result += f"Для получения подробной информации нажмите на кнопку ниже."

    return result


def event_fields():
    return f"Название мероприятия\n" \
           f"Дату и время в формате `dd.MM.yyyy HH:mm`\n" \
           f"Место проведения мероприятия\n" \
           f"Максимальное количество участников, 0 - не ограничено\n" \
           f"\n" \
           f"Пример:\n" \
           f"```\n" \
           f"IT-конференция\n" \
           f"29.07.2021 13:00\n" \
           f"Образовательный центр \"Сириус\"\n" \
           f"0```"


def event_action_start(action):
    return f"Для {action} мероприятия введите в одном сообщении *на отдельных строках*:\n{event_fields()}"


def new_event_start():
    return event_action_start("создания нового")


def edit_event_start():
    return event_action_start("редактирования")


def enter_event_description(action, old_description=""):
    return f"Мероприятие {action}.\n" \
           f"Теперь введите описание мероприятия." \
           f"{old_description}"


def enter_new_event_description():
    return enter_event_description("создано")


def enter_edited_event_description(description):
    return enter_event_description(
        "изменено (старое описание было удалено)",
        f"\nСтарое описание: ```\n{description}```"
    )


def description_saved():
    return f"Описание сохранено."


def unknown_user():
    return f"Не удалось получить пользователя, попробуйте ввести /help"


def unknown_event():
    return f"Не удалось получить информацию о выбранном событии."


def unknown_ticket():
    return f"Не удалось получить информацию о выбранном билете."


def full_event_information(event):

    if event.max_members == 0:
        max_members = "не ограничено"
    else:
        max_members = str(event.max_members)

    return f"*{event.name}* {event.datetime.strftime(dt_format)}\n" \
           f"Место проведения: {event.location}\n" \
           f"Максимальное кол-во участников: {max_members}\n" \
           f"{event.description}"


def enter_ticket_members():
    return f"Введите кол-во мест."


def signup_success():
    return f"Вы успешно записались на мероприятие."


def tickets_list_title():
    return f"*Ваши билеты.*\n" \
           f"Нажмите на кнопку, чтобы запросить qr-код."


def no_tickets():
    return f"У вас нет билетов."


def ticket_caption(ticket):
    event = ticket.event
    return f"{event.datetime.strftime(dt_format)} {event.name}: {ticket.members} мест"


def members_must_be_int():
    return f"Количество мест должно задаваться целым числом."


def too_many_members(max_members):
    return f"Указано слишком большое кол-во участников, максимальное: {max_members}"
