from anytree import NodeMixin


class Prop(NodeMixin):
    def __init__(self, name, area=None, truth_value=None, tag=None, parent=None, children=None):
        self.name = name
        self.area = area
        self.parent = parent
        self.truth_value = self.set_truth_value()  # sort of like a multiplyer (get bn update maybe?)
        self.tag = tag
        self.scenario = None
        if children:
            self.children = children


# belongs to scenario attribute?

    def set_area(self, area):
        self.area = area

    def set_truth_value(self):
        if "!" in self.name:
            truth_value = 0
        else:
            truth_value = 1
        return truth_value

    def set_tag(self, tag):
        self.tag = tag

    def add_scenario(self, scn_name):
        self.scenario = scn_name

    def get_scenario(self):
        return self.scenario
