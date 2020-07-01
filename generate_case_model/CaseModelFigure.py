import plotly.graph_objects as go
import pyAgrum as gum
import generate_case_model.CaseModel as case_model
import generate_case_model.Moja_Case as moja_case


class CaseModelFigure:
    def __init__(self, initial_case_model):
        self.figure = go.Figure()
        self.casemodel = initial_case_model
        # to do: create such that each line is a subfigure in self.figure.
        # for now, plot line-by-line

    def show(self):
        self.figure.show()

    def update(self):
       pass

    def get_figure(self):
        prelude_width = 0
        prelude_height = 0   # stack
        figure = self.figure
        for case in self.casemodel.cases:
            width_of_case = case.get_width()
            height_of_case = case.get_height()
            area_of_case = width_of_case * height_of_case
            evidence_in_case = case.get_evidence_in_case()
            figure.add_trace(
                go.Scatter(x=[prelude_width, prelude_width, prelude_width + width_of_case, prelude_width + width_of_case],
                           y=[prelude_height, prelude_height + height_of_case, prelude_height + height_of_case, prelude_height], fill="toself"))
            figure.add_trace(
                go.Scatter(x=[(width_of_case / 2) + prelude_width], y=[(height_of_case / 2) + prelude_height],
                           text=[evidence_in_case], mode="text"))
            figure.add_trace(
                go.Scatter(x=[(width_of_case / 2) + prelude_width], y=[(height_of_case / 3) + prelude_height],
                           text=[round(area_of_case, 6)], mode="text"))
            figure.update_xaxes(range=[-0.1, 1.1])
            figure.update_layout(yaxis_type='log')

            prelude_width = prelude_width + width_of_case

