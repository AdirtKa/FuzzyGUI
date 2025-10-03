import numpy as np
import matplotlib.pyplot as plt
from ui_main import FuzzyTipUI
from fuzzy_system import build_system
import skfuzzy as fuzz


class FuzzyTipController(FuzzyTipUI):
    def __init__(self):
        super().__init__()

        self.calc_button.clicked.connect(self.calculate_tip)
        self.graph_button.clicked.connect(self.show_graphs)
        self.cuts_button.clicked.connect(self.show_tip_cuts)  # 🔥 новая кнопка

        self.last_system = None

    def calculate_tip(self):
        food_score = self.food_spin.value()
        service_score = self.service_spin.value()
        method = self.method_combo.currentText()

        tipping = build_system(method)
        tipping.input['food'] = food_score
        tipping.input['service'] = service_score
        tipping.compute()

        result = tipping.output['tip']
        self.result_label.setText(f"Рекомендуемые чаевые: {result:.2f}%")

        self.last_system = tipping

    def show_graphs(self):
        if self.last_system is None:
            self.result_label.setText("Сначала рассчитайте чаевые!")
            return

        antecedents = {ant.label: ant for ant in self.last_system.ctrl.antecedents}
        consequents = {con.label: con for con in self.last_system.ctrl.consequents}

        food = antecedents['food']
        service = antecedents['service']
        tip_var = consequents['tip']

        import matplotlib.pyplot as plt
        fig, axes = plt.subplots(3, 1, figsize=(8, 10))

        # --- Еда ---
        for name, term in food.terms.items():
            axes[0].plot(food.universe, term.mf, label=name)
        food_val = self.food_spin.value()
        axes[0].axvline(food_val, color='red', linestyle='--', label=f'Оценка еды = {food_val}')
        axes[0].set_title("Еда")
        axes[0].set_xlabel("Оценка (1-10)")
        axes[0].set_ylabel("Принадлежность")
        axes[0].legend()
        axes[0].grid(True)

        # --- Сервис ---
        for name, term in service.terms.items():
            axes[1].plot(service.universe, term.mf, label=name)
        service_val = self.service_spin.value()
        axes[1].axvline(service_val, color='red', linestyle='--', label=f'Оценка сервиса = {service_val}')
        axes[1].set_title("Сервис")
        axes[1].set_xlabel("Оценка (1-10)")
        axes[1].set_ylabel("Принадлежность")
        axes[1].legend()
        axes[1].grid(True)

        # --- Чаевые ---
        for name, term in tip_var.terms.items():
            axes[2].plot(tip_var.universe, term.mf, label=name)
        result = self.last_system.output['tip']
        axes[2].axvline(result, color='red', linestyle='--', label=f'Чаевые = {result:.2f}%')
        axes[2].set_title("Чаевые")
        axes[2].set_xlabel("Процент (%)")
        axes[2].set_ylabel("Принадлежность")
        axes[2].legend()
        axes[2].grid(True)

        plt.tight_layout()
        plt.show()

    def show_tip_cuts(self):
        if self.last_system is None:
            self.result_label.setText("Сначала рассчитайте чаевые!")
            return

        # --- 1. Получаем все переменные из системы
        antecedents = {ant.label: ant for ant in self.last_system.ctrl.antecedents}
        consequents = {con.label: con for con in self.last_system.ctrl.consequents}

        food = antecedents['food']
        service = antecedents['service']
        tip_var = consequents['tip']

        x = tip_var.universe
        mf = tip_var.terms  # {'low': Term, 'medium': Term, 'high': Term}

        # --- 2. Берём входные значения пользователя
        food_val = self.food_spin.value()
        service_val = self.service_spin.value()

        # --- 3. Фаззификация (степени принадлежности входов)
        μ_food_bad = fuzz.interp_membership(food.universe, food.terms['bad'].mf, food_val)
        μ_food_good = fuzz.interp_membership(food.universe, food.terms['good'].mf, food_val)

        μ_serv_poor = fuzz.interp_membership(service.universe, service.terms['poor'].mf, service_val)
        μ_serv_avg = fuzz.interp_membership(service.universe, service.terms['average'].mf, service_val)
        μ_serv_exc = fuzz.interp_membership(service.universe, service.terms['excellent'].mf, service_val)

        # --- 4. Применяем правила Мамдани
        # Rule1: poor OR bad → low
        act_low = max(μ_serv_poor, μ_food_bad)

        # Rule2: average → medium
        act_medium = μ_serv_avg

        # Rule3: excellent AND good → high
        act_high = min(μ_serv_exc, μ_food_good)

        # --- 5. Усечение функций принадлежности выходных термов
        cut_low = np.fmin(mf['low'].mf, act_low)
        cut_medium = np.fmin(mf['medium'].mf, act_medium)
        cut_high = np.fmin(mf['high'].mf, act_high)

        # --- 6. Агрегация
        aggregated = np.fmax(cut_low, np.fmax(cut_medium, cut_high))

        # --- 7. Дефаззификация (центр тяжести)
        centroid = np.sum(x * aggregated) / np.sum(aggregated)

        # --- 8. Рисуем график
        import matplotlib.pyplot as plt
        plt.figure(figsize=(8, 5))

        # Исходные кривые
        for name, term in mf.items():
            plt.plot(x, term.mf, '--', label=f"{name} (исходн.)")

        # Срезы
        plt.fill_between(x, 0, cut_low, alpha=0.4, color="blue", label=f"low (срез, {act_low:.2f})")
        plt.fill_between(x, 0, cut_medium, alpha=0.4, color="green", label=f"medium (срез, {act_medium:.2f})")
        plt.fill_between(x, 0, cut_high, alpha=0.4, color="red", label=f"high (срез, {act_high:.2f})")

        # Итоговые значения
        result = self.last_system.output['tip']
        plt.axvline(result, color='red', linestyle='--', label=f'Выход (defuzz) = {result:.2f}%')

        plt.title("Чаевые – усечённые функции принадлежности (Мамдани)")
        plt.xlabel("Чаевые (%)")
        plt.ylabel("Принадлежность")
        plt.legend()
        plt.grid(True)
        plt.show()


