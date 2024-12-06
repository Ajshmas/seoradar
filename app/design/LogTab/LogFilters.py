# app/design/LogTab/LogFilters.py

from datetime import datetime
import logging


def filter_logs(logs, selected_filter, search_text, start_time, end_time):
    """
    Фильтрует список логов по типу, тексту и временным интервалам.

    :param logs: Список логов (словарей с ключами 'timestamp', 'log_type', 'message').
    :param selected_filter: Выбранный фильтр типа логов (например, "INFO").
    :param search_text: Текст для поиска в сообщениях логов.
    :param start_time: Начало временного интервала (datetime.datetime).
    :param end_time: Конец временного интервала (datetime.datetime).
    :return: Отфильтрованный список логов.
    """
    filtered = []
    for log in logs:
        # Фильтрация по типу лога
        if selected_filter != "Все" and log['log_type'] != selected_filter:
            continue

        # Фильтрация по тексту поиска
        if search_text and search_text not in log['message'].lower():
            continue

        # Фильтрация по времени
        try:
            # Предполагается, что временная метка в формате "YYYY-MM-DD HH:MM:SS"
            log_time = datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            logging.error(f"Невозможно разобрать временную метку лога: {
                          log['timestamp']}. Ошибка: {e}")
            continue  # Пропускаем логи с некорректными временными метками

        if not (start_time <= log_time <= end_time):
            continue

        # Если лог проходит все фильтры, добавляем его в результат
        filtered.append(log)

    return filtered
