import sys
from PyQt5.QtWidgets import QApplication
from db.database import Base, engine
from ui.main_Window import MainWindow


# Create tables if not exist
Base.metadata.create_all(engine)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
