import anytree
from anytree import NodeMixin, Node, RenderTree, PreOrderIter
import plotly.graph_objects as go
import pyAgrum as gum
import generate_case_model.Case as single_case




class CaseModel:
    def __init__(self, case_list):
        self.cases = case_list
        self.old_cases = []
        self.evidence = {}
        self.caseTree = None
        self.dict_of_nodes = {}
        self.dict_of_all_ev_nodes = {}

    def set_dict_of_all_ev_nodes(self, total_ev_dict):
        self.dict_of_all_ev_nodes = total_ev_dict

    def get_dict_of_all_ev_nodes(self):
        return self.dict_of_all_ev_nodes

    def print_case_model(self):
        pass
        '''
        for case in self.cases:
            print(case.name, case.get_case_area())
            for node in case.dict_evidence_value.keys():
                print("\t", node.name, node.tag, case.dict_evidence_value[node], case.area_case)
        '''
    def add_case(self, case):
        self.cases.append(case)

    def add_scn_to_dict(self, node, scn):
        try:
            list_of_scn_a_node_belongs_to = self.dict_of_nodes[node]
        except KeyError:
            list_of_scn_a_node_belongs_to = []
        list_of_scn_a_node_belongs_to.append(scn)
        self.dict_of_nodes[node] = list_of_scn_a_node_belongs_to

    def add_evidence(self, entry, truth_value, ie):
        self.evidence[entry] = truth_value
        self.update_tree1(entry, truth_value, ie)
        self.recalculate_area_for_plot()

    def add_evidence_scenario(self, entry, truth_value, ie):
        flag = "normal"
        if entry in self.evidence.keys() and self.evidence[entry] != truth_value:   # we have changed the evidence!
            #print("truth val : ", self.evidence[entry])
            flag = "changing evidence"
            pass
        self.evidence[entry] = truth_value
        #print("truth val : ", self.evidence[entry])
        #print(self.evidence)
        posterior_entry = ie.posterior(entry).tolist()
        list_1 = []
        ie.setEvidence(self.evidence)
        for case in self.cases:
            scn_case = case.scenario
            save_key = "evidence_not_in_case"
            #print("SCENARIO CASE", scn_case)

            #print(case.dict_evidence_value.keys())

            for key in case.all_ev:
                if str(key) == entry:
                    save_key = key


            scenario_of_new_case = case.scenario

            #print("\t\t Dict of case", case.dict_evidence_value)
            #print(case.all_ev)
            new_case_dict_ev = case.all_ev
            negation_dict_ev = case.all_ev
            negation_case_area = case.area_case
            negation_scenario_width = case.scn_width
            negation_dict_all_ev = case.all_ev


            #case.dict_evidence_value[save_key] = truth_value
            #case.all_ev[save_key] = truth_value

            index = int(scn_case[-1])
            posterior_of_scn = ie.posterior('constraint')
            #case.area_case = posterior_of_scn[index]*posterior_entry[1]
            #print("AREA CALC", posterior_of_scn[index], posterior_entry[1], case.area_case)
            #case.width = posterior_of_scn[index]
            #case.set_case_area(case.area_case)

            # then, create a new case with the negation (as it were)
            if truth_value == 1:
                neg_truth_value = 0
            else:
                neg_truth_value = 1
            #if save_key != "evidence_not_in_case":

            '''print("NEGATION DICT EV BEFOR:")
            for key in negation_dict_ev:
                print(key, negation_dict_ev[key])'''


            new_case_dict_ev[save_key] = truth_value


            negation_dict_ev[save_key] = neg_truth_value
            negation_case_area = posterior_of_scn[index]*posterior_entry[0]

            '''print("NEGATION DICT EV AFTER:", negation_dict_ev)
            for key in negation_dict_ev:
                print(key, negation_dict_ev[key])'''

            case = single_case.Case("None", new_case_dict_ev, case.scn_width, case.area_case, case.all_ev, scenario_of_new_case)
            case.improve_name_list(entry, truth_value, flag)
            case.area_case = posterior_of_scn[index] * posterior_entry[1]

            case_negation = single_case.Case("None", negation_dict_ev, negation_scenario_width, negation_case_area, negation_dict_all_ev, scenario_of_new_case)
            #case_negation.improve_name_list(entry, neg_truth_value, flag)
            case_negation.area_case = posterior_of_scn[index]*posterior_entry[0]
            #print("NEG AREA CALC", posterior_of_scn[index], posterior_entry[0], case_negation.area_case)

            #case_negation.width = posterior_of_scn[index]
            list_1.append(case)
            list_1.append(case_negation)
            #case_negation.set_case_area(case_negation.area_case)

            #case.improve_name_list(entry, truth_value, flag)


        self.old_cases.append(self.cases)
        self.cases = []

        for item in list_1:
            self.add_case(item)

        #self.update_tree1(entry, truth_value, ie)
        #self.recalculate_area_for_plot()
        '''
        print("CASES: ")
        for case in self.cases:
            print("\t", case.name, case.scenario, case.area_case, case.scn_width)
            for key in case.dict_evidence_value.keys():
                print(key, case.dict_evidence_value[key])
        '''


    '''
    def remove_evidence(self, entry):
        self.evidence[entry] = 1  # not sure about this interpretation of truth value..
        self.update_tree(entry, )
        self.recalculate_area_for_plot() -> removing evidence 
    '''
    # removing evidence should mean resetting to prior! TODO: implementing resetting to prior

    def set_new_tree(self, tree):
        self.caseTree = tree

    def get_evidence_dict(self):
        return self.evidence

    def print_val_tree(self):
        for pre, fill, node in RenderTree(self.caseTree):
            print("%s%s %s %s  %s" % (pre, node.name, node.area, node.truth_value, node.tag))

    def update_tree1(self, entry, truth_value, ie):
        for node in PreOrderIter(self.caseTree):
            if node.name == "Root":
                continue
            else:
                if "!" in node.name:
                    final_array = ie.posterior(node.name[1:])
                    node.set_area(round(final_array[0], 2))
                    if truth_value == 1:
                        node.set_truth_value(0)
                    else:
                        node.set_truth_value(1)
                else:
                    final_array = ie.posterior(node.name)
                    node.set_area(round(final_array[1], 2))
                    if truth_value == 1:
                        node.set_truth_value(1)
                    else:
                        node.set_truth_value(0)



    def update_tree(self, entry, truth_value, call):
        nodes = anytree.search.findall(self.caseTree, filter_=lambda node: node.name in (entry, "!" + entry))
        for node in nodes:      # here, we actually want to update with the ie.posterior value (computationally more expensive!)
            if call == "add":
                if node.name == entry:
                    if truth_value == 1:
                        node.set_truth_value(1)
                    else:
                        node.set_truth_value(0)
                if node.name != entry:
                    if truth_value == 1:
                        node.set_truth_value(0)
                    else:
                        node.set_truth_value(1)
            if call == "remove":
                node.set_truth_value(1)

    def recalculate_area_for_plot(self):
        for case in self.cases:
            base = case.base_leaf.area
            for item in case.base_leaf.ancestors:
                if item.name != 'Root':
                    base = base * item.area
            case.recalculate_value(base)

    def print_preference_ordering(self):
        newList = sorted(self.cases, key=lambda x: x.val, reverse=True)
        for x in newList:
            print(x.list_case, x.val)

    def print_preference_ordering_relevant_cases(self):  # only show greter than 0
        newList = sorted(self.cases, key=lambda x: x.val, reverse=True)
        for x in newList:
            if x.val > 0:
                print(x.list_case, x.val)
            else:
                break

    def get_figure(self):
        figure = go.Figure()
        stack = 0
        for case in self.cases:
            if case.val > 0:
                figure.add_trace( go.Scatter(x=[0, 0, 1, 1], y=[stack, case.val + stack, case.val + stack, stack], fill="toself"))
                figure.add_trace(go.Scatter(x=[0.5], y=[stack + (case.val / 2)], text=[case.list_case], mode="text"))
                figure.add_trace(go.Scatter(x=[0.01], y=[stack + (case.val / 2)], text=[round(case.val, 2)], mode="text"))
                stack = stack + case.val
        figure.show()

    def get_figure_scenario_based(self):
        figure = go.Figure()
        stack = 0
        width = 0
        scn = None
        flag = 0
        for case in self.cases:
            print("IN FIG", case.name, case.area_case, case.dict_evidence_value)
            # if scenario changes, stack-height must reset
            if case.scenario != scn:
                stack = 0
                scn = case.scenario
                flag = 1
            if case.area_case > 0:
                width_of_case = case.get_case_width()
                height_of_case = case.get_case_height()
                figure.add_trace(
                    go.Scatter(x=[width, width, width+width_of_case, width+width_of_case], y=[stack, height_of_case, height_of_case, stack], fill="toself"))
                figure.add_trace(
                    go.Scatter(x=[(case.get_case_width()/2)+width], y=[(height_of_case / 2) + stack], text=[case.list_known_evidence], mode="text"))
                figure.add_trace(
                    go.Scatter(x=[(case.get_case_width() / 2) + width], y=[(height_of_case / 3) + stack],
                               text=[round(case.area_case, 2)], mode="text"))

            stack = stack + height_of_case
            if flag == 1:
                width = width_of_case + width
                flag = 0
        print("\n")
        figure.show()



