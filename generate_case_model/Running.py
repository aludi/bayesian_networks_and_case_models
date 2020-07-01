import generate_case_model.CaseModel as case_model
import generate_case_model.Prop as prop
import plotly.graph_objects as go
import pyAgrum as gum

class Running:

    def __init__(self, bn, imported, ie):
        full_case_model, figure, base_y_pos, caseModel, total_ev_dict = self.initiate(bn, imported, ie)
        self.bn = bn
        self.caseModel = caseModel
        self.print_full_case_model = full_case_model
        self.y_base = base_y_pos
        self.figure = figure
        self.total_ev_dict = total_ev_dict

    def get_caseModel(self):
        return self.caseModel
    def set_caseModel(self, caseModel):
        self.caseModel = caseModel
    def get_total_ev_dict(self):
        return self.total_ev_dict
    def get_params_figure(self):
        return self.figure, self.print_full_case_model, self.y_base
    def set_figure(self, figure):
        self.figure = figure
    def decrease_y_base(self):
        self.y_base = self.y_base - 2
    def get_y_base(self):
        return self.y_base
    def get_figure(self):
        return self.figure

    def find_posterior_events(self, bn, caseModel, evidence, ie, imported):
        x = bn.variable(evidence).name()
        parent_node = bn.parents(x).pop()  # evidence/entry has one parent because evidence supports one node (TODO: more nodes) -> parent is a set
        parent_node = bn.variable(parent_node).name()
        caseModel.find_posterior_events(evidence, parent_node, ie, imported)


    def recursing_children_for_dict(self, bn, parent, ie, scn_dict_ev, scn_dict_area):
        name_parent = parent.name
        children = bn.children(name_parent)
        if str(children) != "set()":
            if parent.tag is not "SCENARIO":
                parent.set_tag("ASPECT")
            for child in children:
                good_name = bn.variable(child).name()
                if good_name != 'constraint':
                    node = prop.Prop(good_name, parent=parent)
                    node.add_scenario(parent.get_scenario())
                    scn_dict_ev[node.name] = None
                    scn_dict_area[node] = None
                    self.recursing_children_for_dict(bn, node, ie, scn_dict_ev, scn_dict_area)
                else:
                    ie.posterior('constraint')
        else:
            parent.set_tag("EVIDENCE")
        return scn_dict_ev, scn_dict_area

    def initiate(self, bn, imported, ie):
        caseModelDomainSpace = 1
        cases = [({}, 1)]  # ([], 1)
        list_of_scenarios = []
        for x in bn.names():
            node_name = bn.variable(x).name()
            if str(bn.parents(x)) != "set()":
                for item in bn.parents(x):
                    pass
            if "scn" in node_name:
                prior_on_scenarios = ie.posterior('constraint').tolist()
                index_in_constraint_table = node_name[-1]
                if imported == 1:
                    prior_scenario_value = 1 - prior_on_scenarios[int(index_in_constraint_table)]
                else:
                    prior_scenario_value = prior_on_scenarios[int(index_in_constraint_table)]
                node_atom = prop.Prop(node_name, prior_scenario_value, truth_value=1, tag="SCENARIO")
                node_atom.add_scenario(node_name)
                list_of_scenarios.append(node_atom)
            division = len(bn.variable(x).domain()) - 3  # - <, , , >, # check len q, if q > 5, then not binary (<0,1>).
            caseModelDomainSpace = caseModelDomainSpace / division
            for case in cases:
                cases.remove(case)
                (dict_of_names, area) = case
                area_new = area / division
                dict_of_names[node_name] = -1  # -1 means "not evidence set"
                new_case = (dict_of_names, area_new)
                cases.append(new_case)
        root_arg = prop.Prop("Root", 1, tag="SPACE")
        scenario_dict_ev = {}
        scenario_dict_area = {}
        total_ev_dict = {}

        case_list = []
        for scenario in list_of_scenarios:
            new_dict_ev = {scenario.name: scenario.truth_value}
            # print(new_dict_ev)
            new_dict_area = {scenario.name: scenario.area}
            # print(new_dict_area)
            new_dict_ev, new_dict_area = self.recursing_children_for_dict(bn, scenario, ie, new_dict_ev, new_dict_area)
            scenario_dict_key = scenario.name
            scenario_dict_ev[scenario_dict_key] = new_dict_ev
            total_ev_dict = {**total_ev_dict, **scenario_dict_ev[scenario_dict_key]}
            case_area = 1
            case = single_case.Case(scenario.name, new_dict_ev, scenario.area, scenario.area, total_ev_dict,
                                    scenario.name)
            case_list.append(case)

        new_list = []
        for case in case_list:
            case.all_ev = dict(total_ev_dict)
            for key in case.all_ev:
                case.all_ev[key] = None
        caseModel = case_model.CaseModel(case_list)

        full_case_model = True
        figure = go.Figure()

        return full_case_model, figure, 0, caseModel, total_ev_dict



    '''def __init__(self, bayesian_network):
        self.caseModel = self.run_cm_conversion_on_bn(bayesian_network)
        self.evidence = None'''

    '''def set_evidence(self):
        pass

    def get_caseModel(self):
        return self.caseModel

    def return_dict_for_cpt(self, value_dict, parentNode):
        if parentNode.name[0] == "!":
            actual_name = parentNode.name[1:]
            value = 0
            value_dict[actual_name] = value
        elif parentNode.name != "Root" and parentNode.name[0] != "!":
            actual_name = parentNode.name
            value = 1
            value_dict[actual_name] = value
        return value_dict

    def set_evidence_in_BN_and_CM(self, evidence, value, ie):  # value is either 0 or 1 (for now) #in running: set evidence
        old_evidence_dict = self.caseModel.get_evidence_dict()
        old_evidence_dict[evidence] = value
        ie.setEvidence(old_evidence_dict)
        ie.makeInference()
        self.caseModel.add_evidence(evidence, value, ie)  # overwriting for testing

    def run_cm_conversion_on_bn(self, bn):
        caseModelDomainSpace = 1
        cases = [({}, 1)]  # ([], 1)
        bn.names()
        for x in bn.names():
            node_name = bn.variable(x).name()
            division = len(bn.variable(x).domain()) - 3  # - <, , , >, # check len q, if q > 5, then not binary (<0,1>).
            caseModelDomainSpace = caseModelDomainSpace / division
            for case in cases:
                cases.remove(case)
                (dict_of_names, area) = case
                area_new = area / division
                dict_of_names[node_name] = -1  # -1 means "not evidence set"
                new_case = (dict_of_names, area_new)
                cases.append(new_case)
        root_arg = prop.Prop("Root", 1, tag="SPACE")
        for name in dict_of_names.keys():
            array = bn.cpt(name).tolist()
            for parentNode in root_arg.leaves:
                value_dict = {}
                value_dict = self.return_dict_for_cpt(value_dict, parentNode)
                for node in parentNode.ancestors:
                    value_dict = self.return_dict_for_cpt(value_dict, node)
                final_array = bn.cpt(name)[value_dict]
                node_pos = prop.Prop(name, parent=parentNode)
                node_neg = prop.Prop("!" + name, parent=parentNode)
                node_pos.set_area(final_array[1])
                node_neg.set_area(final_array[0])


        caseModel = case_model.CaseModel(root_arg)
        for leaf in root_arg.leaves:
            base = leaf.area
            name_list = [leaf.name]
            prior_dict = {}
            prior_dict[leaf.name] = base
            leaf.set_tag("EVIDENCE")    # set final node as node with no children
            for item in leaf.ancestors:
                if item.name != "Root":
                    base = base * item.area * item.truth_value
                    name_list.append(item.name)
                    prior_dict[item.name] = item.area
                    if 'scn' in item.name and item.tag == None:  #scenario node tag!!!
                        item.set_tag("SCENARIO")
                    elif 'constraint' in item.name and item.tag == None:
                        item.set_tag("CONSTRAINT")
                    elif item.tag == None:
                        item.set_tag("ASPECT")      # aspect node
                    # TODO: constraint node when three-valued


            case = single_case.Case(name_list, base, prior_dict, leaf)
            caseModel.add_case(case)
        return caseModel'''
