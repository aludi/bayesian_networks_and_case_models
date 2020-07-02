import plotly.graph_objects as go
import plotly.offline as po
from svgutils.compose import *

import cufflinks as cf


class CaseModelFigure:
    def __init__(self, initial_case_model):
        self.figure = go.Figure()
        self.casemodel = initial_case_model
        self.figure_list = []

    def show(self):
        self.figure = cf.Figure(
            cf.subplots(self.figure_list, base_layout=self.figure_list[1].to_dict()['layout'], shared_xaxes=True, shape=(len(self.figure_list), 1)))
        self.figure.show()

    def get_formatted_string(self, truth_val, string):
        if truth_val == 'false':
            return "! " + string
        else:
            return "" + string

    def get_figure(self, evidence, truth_value):
        prelude_width = 0
        prelude_height = 0   # stack
        figure = go.Figure()

        rough_height_indication_for_plot = self.casemodel.cases[0].get_height()
        figure.add_trace(
            go.Scatter(x=[1.2], y=[0.1],
                       text=[self.get_formatted_string(truth_value, evidence)], mode="text"))
        for case in self.casemodel.cases:
            width_of_case = case.get_width()
            height_of_case = case.get_height()
            area_of_case = width_of_case * height_of_case
            events_in_case = case.get_events_in_case()
            if case.scenario != events_in_case[-1]:
                relevant_events = [case.scenario, events_in_case[-1]]
            else:
                relevant_events = [case.scenario]
            figure.add_trace(
                go.Scatter(x=[prelude_width, prelude_width, prelude_width + width_of_case, prelude_width + width_of_case],
                           y=[prelude_height, prelude_height + height_of_case, prelude_height + height_of_case, prelude_height], fill="toself"))
            figure.add_trace(
                go.Scatter(x=[(width_of_case / 2) + prelude_width], y=[0.05],
                           text=[relevant_events], mode="text"))
            figure.add_trace(
                go.Scatter(x=[(width_of_case / 2) + prelude_width], y=[0.001],
                           text=[round(area_of_case, 6)], mode="text"))
            figure.update_xaxes(range=[-0.1, 1.4])

            figure.update_layout(yaxis_type='log')

            prelude_width = prelude_width + width_of_case
        self.append_figure_to_figure_list(figure)

    def append_figure_to_figure_list(self, new_figure):
        self.figure_list.append(new_figure)

