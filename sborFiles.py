import os

# Путь к главной папке (где находится этот скрипт)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_FILE = os.path.join(ROOT_DIR, 'main.py')
APP_DIR = os.path.join(ROOT_DIR, 'app')
OUTPUT_FILE = os.path.join(ROOT_DIR, 'output.txt')


def write_directory(output, rel_dir_path):
    """
    Записывает заголовок для директории.
    """
    output.write(f"\n===== {rel_dir_path}/ =====\n\n")


def write_file(output, file_path, rel_file_path):
    """
    Записывает заголовок и содержимое файла.
    Если файл пустой, записывает только заголовок.
    """
    output.write(f"===== {rel_file_path} =====\n")
    try:
        if os.path.getsize(file_path) > 0:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            output.write(content)
        else:
            output.write("[Файл пустой]")
    except Exception as e:
        output.write(f"[Ошибка при чтении файла: {e}]")
    output.write("\n\n")  # Разделитель между файлами


def traverse_app_directory(app_dir, output):
    """
    Рекурсивно проходит по директории app/ и записывает файлы и папки в output.txt,
    игнорируя папки __pycache__.
    """
    for root, dirs, files in os.walk(app_dir):
        # Исключаем папки __pycache__ из обхода
        dirs[:] = [d for d in dirs if d != '__pycache__']

        # Получаем относительный путь к текущей директории от app/
        rel_dir = os.path.relpath(root, app_dir)
        if rel_dir == '.':
            rel_dir = ''
        else:
            write_directory(output, rel_dir)

        # Обрабатываем файлы в текущей директории
        for file in files:
            file_path = os.path.join(root, file)
            rel_file_path = os.path.join(rel_dir, file) if rel_dir else file
            write_file(output, file_path, rel_file_path)

        # Проверяем, есть ли поддиректории или файлы
        if not dirs and not files and rel_dir:
            # Пустая директория
            write_directory(output, rel_dir)


def write_main_file(output, main_file_path, rel_main_path='main.py'):
    """
    Записывает файл main.py в output.txt.
    """
    output.write(f"===== {rel_main_path} =====\n")
    try:
        if os.path.getsize(main_file_path) > 0:
            with open(main_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            output.write(content)
        else:
            output.write("[Файл пустой]")
    except Exception as e:
        output.write(f"[Ошибка при чтении файла: {e}]")
    output.write("\n\n")  # Разделитель между файлами


def main():
    # Проверка наличия main.py и app/
    missing = False
    if not os.path.isfile(MAIN_FILE):
        print(f"Главный файл {MAIN_FILE} не найден.")
        missing = True
    if not os.path.isdir(APP_DIR):
        print(f"Папка app/ не найдена в {ROOT_DIR}.")
        missing = True
    if missing:
        return

    print("Сбор файлов из main.py и папки app/ (игнорируя __pycache__)...")

    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as out_file:
            # Сначала записываем main.py
            write_main_file(out_file, MAIN_FILE)

            # Затем обходим папку app/
            traverse_app_directory(APP_DIR, out_file)

        print(f"Готово! Содержимое записано в {OUTPUT_FILE}.")
    except Exception as e:
        print(f"Произошла ошибка при записи в {OUTPUT_FILE}: {e}")


if __name__ == "__main__":
    main()
