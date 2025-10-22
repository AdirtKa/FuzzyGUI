import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def build_system(defuzzify_method="centroid"):
    # Входные переменные
    food = ctrl.Antecedent(np.arange(0, 11, 1), 'food')
    service = ctrl.Antecedent(np.arange(0, 11, 1), 'service')

    # Выходная переменная
    tip = ctrl.Consequent(np.arange(0, 26, 1), 'tip', defuzzify_method=defuzzify_method)

    # --- Функции принадлежности ---
    food['bad'] = fuzz.trapmf(food.universe, [0, 0, 4, 10])
    food['good'] = fuzz.trapmf(food.universe, [4, 10, 10, 10])

    service['poor'] = fuzz.trapmf(service.universe, [0, 0, 2, 5])
    service['average'] = fuzz.trimf(service.universe, [2, 5, 10])
    service['excellent'] = fuzz.trimf(service.universe, [5, 10, 10])

    tip['low'] = fuzz.trimf(tip.universe, [0, 0, 10])
    tip['medium'] = fuzz.trimf(tip.universe, [0, 10, 15])
    tip['high'] = fuzz.trapmf(tip.universe, [10, 15, 25, 25])

    # --- Правила ---
    rule1 = ctrl.Rule(service['poor'] | food['bad'], tip['low'])
    rule2 = ctrl.Rule(service['average'], tip['medium'])
    rule3 = ctrl.Rule(service['excellent'] & food['good'], tip['high'])

    tipping_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
    return ctrl.ControlSystemSimulation(tipping_ctrl)

