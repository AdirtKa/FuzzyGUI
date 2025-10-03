import sys
from PySide6.QtWidgets import QApplication
from controller import FuzzyTipController


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FuzzyTipController()
    window.show()
    sys.exit(app.exec())
