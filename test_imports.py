# minimal_test.py

from PySide6.QtGui import QAction


def main():
    action = QAction("Test Action")
    print("QAction успешно импортирован и создан:", action.text())


if __name__ == "__main__":
    main()
