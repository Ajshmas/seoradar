# app/design/LogTab/LogFilters.py

def filter_logs(logs, selected_filter, search_text, start_time, end_time):
    """
    Фильтрует логи на основе выбранных фильтров.

    :param logs: Список всех логов.
    :param selected_filter: Выбранный тип логов для фильтрации ("Все", "INFO", "ERROR", и т.д.).
    :param search_text: Текст для поиска в сообщениях логов.
    :param start_time: Начало временного интервала (datetime.datetime).
    :param end_time: Конец временного интервала (datetime.datetime).
    :return: Список отфильтрованных логов.
    """
    filtered_logs = []

    for log in logs:
        # Фильтрация по типу лога
        if selected_filter != "Все" and log['log_type'] != selected_filter:
            continue

        # Фильтрация по тексту поиска (регистр не учитывается)
        if search_text and search_text not in log['message'].lower():
            continue

        # Получаем временную метку лога
        log_time = log['timestamp']  # Объект datetime.datetime

        # Фильтрация по времени
        if not (start_time <= log_time <= end_time):
            continue

        # Если лог прошёл все фильтры, добавляем его в список
        filtered_logs.append(log)

    return filtered_logs
