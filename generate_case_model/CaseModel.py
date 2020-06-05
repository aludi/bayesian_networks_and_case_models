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
        if entry in self.evidence.keys():
            if self.evidence[entry] != truth_value:
                flag = 1
            if self.evidence[entry] == truth_value:
                #print("IN FLAG 2")
                flag = 2
        else:
            flag = 0
        ie.setEvidence({})
        ie.makeInference()
        self.evidence[entry] = truth_value
        posterior_entry = ie.posterior(entry).tolist()
        ie.setEvidence(self.evidence)
        posterior_of_scn = ie.posterior('constraint')
        #print(ie.posterior(entry))
        #print(posterior_of_scn)
        if flag == 1:
            self.change_evidence_scenario(posterior_entry, posterior_of_scn, entry, truth_value)
        elif flag == 0:
            self.add_new_evidence_scenario(entry, truth_value, posterior_entry, posterior_of_scn, ie)



    def change_evidence_scenario(self, posterior_entry, posterior_of_scn, entry, new_truth_value):
        for case in self.cases:
            old_case_ev_dict = dict(case.all_ev)
            index = int(case.scenario[-1])

            if old_case_ev_dict[entry] == new_truth_value:      # the case where the thing is negaated. We only need to update and swap around the posteriors...
                case.area_case = posterior_entry[0]*posterior_of_scn[index]
            else:
                case.area_case = posterior_entry[1]*posterior_of_scn[index]
            case.scn_width = posterior_of_scn[index]


    def add_new_evidence_scenario(self, entry, truth_value, posterior_entry, posterior_of_scn, ie):
        print("NEW EVIDENCE")
        list_1 = []
        for case in self.cases:

            if truth_value == 1:
                neg_truth_value = 0
            else:
                neg_truth_value = 1

            new_pos_evidence_dict = {}
            new_pos_evidence_dict['constraint'] = [0, 1, 1]
            new_neg_evidence_dict = {}
            new_neg_evidence_dict['constraint'] = [0, 1, 1]


            for x in case.all_ev:
                if case.all_ev[x] != None:
                    new_pos_evidence_dict[x] = case.all_ev[x]
                    new_neg_evidence_dict[x] = case.all_ev[x]
                if x == entry:
                    new_pos_evidence_dict[x] = truth_value
                    new_neg_evidence_dict[x] = neg_truth_value

            ie.setEvidence({})
            ie.posterior(entry)
            print(ie.posterior(entry))
            ie.makeInference()
            ie.setEvidence(new_pos_evidence_dict)
            posterior_of_scn = ie.posterior('constraint')
            print("PRINT POSTERIOR OF SCN GIVEN EVIENCE IN CASE", posterior_of_scn, new_pos_evidence_dict)
            print(case.scenario, posterior_entry)
            ie.setEvidence(new_neg_evidence_dict)
            posterior_of_scn = ie.posterior('constraint')
            print("PRINT POSTERIOR OF SCN GIVEN EVIENCE IN CASE", posterior_of_scn, new_neg_evidence_dict)
            print(case.scenario, posterior_entry)

            '''

            new_case_dict_ev = dict(case.all_ev)
            negation_dict_ev = dict(case.all_ev)
            index = int(case.scenario[-1])
            new_width = posterior_of_scn[index]
            # then, create a new case with the negation (as it were)


            new_case_dict_ev[entry] = truth_value
            negation_dict_ev[entry] = neg_truth_value



            new_case = single_case.Case("None", dict(new_case_dict_ev), new_width, posterior_of_scn[index] * posterior_entry[1], dict(new_case_dict_ev), case.scenario)
            case_negation = single_case.Case("None", dict(negation_dict_ev), new_width, posterior_of_scn[index]*posterior_entry[0], dict(negation_dict_ev), case.scenario)

            #print("NEW CASE", new_case.area_case, new_case.all_ev)
            #print("NEW NEGATED CASE", case_negation.area_case, case_negation.all_ev)

            list_already_contains_case = False
            list_already_contains_negated_case = False
            for item in list_1:
                if item.all_ev == new_case.all_ev:
                    list_already_contains_case = True
                elif item.all_ev == case_negation.all_ev:
                    list_already_contains_negated_case = True
            if list_already_contains_case == False:
                list_1.append(new_case)
            if list_already_contains_negated_case == False:
                list_1.append(case_negation)
        self.old_cases.append(self.cases)
        self.cases = []
        

        for item in list_1:
            self.add_case(item)
        '''


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
        scn = 'scn_1'
        flag = 0
        total_sum_area = 0
        for case in self.cases:
            #print("IN FIG", case.name, case.area_case)
            val_val = case.check_with_evidence(self.evidence)
            total_sum_area = case.area_case + total_sum_area
            height_of_case = case.get_case_height()
            # if scenario changes, stack-height must reset and we must move to the right
            if case.scenario != scn:
                width = width_of_case + width
                stack = 0
                scn = case.scenario

            if val_val == True or val_val == False:
                width_of_case = case.get_case_width()
                case.collect_known_evidence()
                figure.add_trace(
                    go.Scatter(x=[width, width, width+width_of_case, width+width_of_case], y=[stack, stack+height_of_case, stack+height_of_case, stack], fill="toself"))
                figure.add_trace(
                    go.Scatter(x=[(case.get_case_width()/2)+width], y=[(height_of_case / 2) + stack], text=[case.list_known_evidence], mode="text"))
                figure.add_trace(
                    go.Scatter(x=[(case.get_case_width() / 2) + width], y=[(height_of_case / 3) + stack],
                               text=[round(case.area_case, 2)], mode="text"))
                figure.update_xaxes(range=[-0.1, 1.1])
                figure.update_yaxes(range=[-0.1, 1.1])

            stack = stack + height_of_case

        print("\n")
        print(total_sum_area)
        figure.show()



