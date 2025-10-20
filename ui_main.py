from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox,
    QComboBox, QHBoxLayout
)


class FuzzyTipUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Нечёткий калькулятор чаевых (Мамдани)")
        self.resize(400, 220)

        layout = QVBoxLayout()

        # Еда
        food_layout = QHBoxLayout()
        food_layout.addWidget(QLabel("Оценка еды (0-10):"))
        self.food_spin = QSpinBox()
        self.food_spin.setRange(0, 10)
        food_layout.addWidget(self.food_spin)
        layout.addLayout(food_layout)

        # Сервис
        service_layout = QHBoxLayout()
        service_layout.addWidget(QLabel("Оценка сервиса (0-10):"))
        self.service_spin = QSpinBox()
        self.service_spin.setRange(0, 10)
        service_layout.addWidget(self.service_spin)
        layout.addLayout(service_layout)

        # Метод дефаззификации
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Метод дефаззификации:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["centroid", "bisector", "mom", "som", "lom"])
        method_layout.addWidget(self.method_combo)
        layout.addLayout(method_layout)

        # Кнопки
        self.calc_button = QPushButton("Рассчитать чаевые")
        layout.addWidget(self.calc_button)

        self.graph_button = QPushButton("Показать графики")
        layout.addWidget(self.graph_button)

        self.cuts_button = QPushButton("Показать срезы чаевых")
        layout.addWidget(self.cuts_button)

        # Результат
        self.result_label = QLabel("Рекомендуемые чаевые: -")
        layout.addWidget(self.result_label)

        self.setLayout(layout)
