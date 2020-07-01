import generate_case_model.Case as single_case
import generate_case_model.CaseModel as case_model
import generate_case_model.Prop as prop
import generate_case_model.Running as running
import generate_case_model.Moja as moja
import pyAgrum as gum

class Moja_Case:
    def __init__(self, name, scn, area, width, conditional_prior_dict, evidence_dict):
        self.name = name
        self.scenario = scn
        self.area = area
        self.width = width
        self.conditional_prior_dict = conditional_prior_dict
        self.evidence_dict = evidence_dict

    def update_conditional_prior_dict(self, evidence, prior_value, add_or_change):
        if add_or_change == 'add':
            self.conditional_prior_dict[evidence] = prior_value
        else:
            self.conditional_prior_dict[evidence] = 1 - self.conditional_prior_dict[evidence]   # negation (cheating a bit. this only works for binary evidence nodes)
        #print(self.conditional_prior_dict)

    def calculate_conditioned_area(self):
        base = 1
        for item in self.conditional_prior_dict:
            if 'scn' not in item:      # don't doubly condition on prior of scenario
                base = base * self.conditional_prior_dict[item]
        return base

    def get_width(self):
        return self.width

    def get_height(self):
        return self.area/self.width

    def get_evidence_in_case(self):
        string = str(self.scenario)
        #print(self.evidence_dict)
        for item in self.evidence_dict:
            if self.evidence_dict[item] == 'false':
                string = string + " !" + item
            else:
                string = string + " " + item
        return string
