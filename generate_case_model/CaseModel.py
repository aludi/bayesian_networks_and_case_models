import anytree
from anytree import NodeMixin, Node, RenderTree, PreOrderIter
import plotly.graph_objects as go
import pyAgrum as gum
import generate_case_model.Case as single_case
from termcolor import colored



class CaseModel:
    def __init__(self, case_list):
        self.cases = case_list
        self.old_cases = []
        self.evidence = {}
        self.caseTree = None
        self.dict_of_nodes = {}
        self.dict_of_all_ev_nodes = {}
        self.string_new_evidence_added_this_step = ""

    def set_dict_of_all_ev_nodes(self, total_ev_dict):
        self.dict_of_all_ev_nodes = total_ev_dict

    def get_dict_of_all_ev_nodes(self):
        return self.dict_of_all_ev_nodes

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

    def add_evidence_scenario(self, entry, truth_value, ie, imported):
        #print(entry,  truth_value)
        self.set_temp_evidence_for_visualization(entry, truth_value)
        if imported == 1:
            if entry != 'vE':
                truth_value = self.swap_vals(truth_value)   # for imported BN TODO: fix thiiiis
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
        posterior_entry = ie.posterior(entry)
        ie.setEvidence(self.evidence)
        posterior_of_scn = ie.posterior('constraint')
        width = posterior_of_scn

        if flag == 1:
            self.change_evidence_scenario(posterior_entry, posterior_of_scn, entry, truth_value)
        elif flag == 0:
            self.add_new_evidence_scenario(entry, truth_value, posterior_entry, ie, width, imported)

    def get_conditioned_area(self, base_case, entry, prior_dict):
        conditioned_area = 1
        for item in prior_dict:
            if item != entry:
                #print("item etc.", item, prior_dict[item], conditioned_area)
                conditioned_area = prior_dict[item] * conditioned_area
        return conditioned_area

    def set_temp_evidence_for_visualization(self, entry, truth_value):
        if truth_value == 0:
            new_ev = "!"+entry
        else:
            new_ev = entry
        self.string_new_evidence_added_this_step = new_ev

    def get_string_evidence_added_this_step(self):
        return self.string_new_evidence_added_this_step



    def change_evidence_scenario(self, posterior_entry, posterior_of_scn, entry, new_truth_value):
        print(posterior_entry, posterior_of_scn, entry, new_truth_value)
        for case in self.cases:
            old_case_ev_dict = dict(case.all_ev)
            index = int(case.scenario[-1])
            old_prior_dict = case.prior_dict
            conditioned_area = self.get_conditioned_area(case, entry, old_prior_dict)
            if entry == 'vE':
                #todo
                continue
            elif old_case_ev_dict[entry] == new_truth_value:      # the case where the thing is negaated. We only need to update and swap around the posteriors...
                case.area_case = conditioned_area*posterior_entry[0]*posterior_of_scn[index]
                case.prior_dict[entry] = posterior_entry[0]
            else:
                case.area_case = conditioned_area*posterior_entry[1]*posterior_of_scn[index]
                case.prior_dict[entry] = posterior_entry[1]
            case.scn_width = posterior_of_scn[index]
            print(posterior_of_scn)

    def swap_vals(self, x):
        if x == 1:
            return 0
        if x == 0:
            return 1

    def update_the_dict_with_priors(self, ie, imported):
        posterior_contraint = ie.posterior("constraint").tolist()
        print(posterior_contraint)
        for case in self.cases:
            name_scenario = case.scenario
            index = int(name_scenario[-1])
            prior_of_scenario = posterior_contraint[index]
            prior_dict = dict(case.prior_dict)
            if imported == 0:
                prior_dict[name_scenario] = prior_of_scenario
            else:
                prior_dict[name_scenario] = 1 - prior_of_scenario
            case.prior_dict = prior_dict


    def generate_new_case(self, base_case, entry, new_truth_value, ie, width, posterior_entry, index_posterior, imported):

        '''if imported == 1:
            print("generating new case with entry: ", entry, "and (swapped) truth value ", self.swap_vals(new_truth_value))
        else:
            print("generating new case with entry: ", entry, "and truth value ", new_truth_value)
        print("evidence: ", base_case.all_ev)'''

        full_dict = dict(base_case.all_ev)
        new_evidence_dict = {}
        new_evidence_dict['vE'] = 1
        for x in base_case.all_ev:
            if base_case.all_ev[x] != None:
                new_evidence_dict[x] = base_case.all_ev[x]
            if x == entry:
                #new_evidence_dict[x] = new_truth_value
                full_dict[x] = new_truth_value

        conditioned_area = self.get_conditioned_area(base_case, entry, base_case.prior_dict)
        old_prior_dict = dict(base_case.prior_dict)
        #print(old_prior_dict)
        ie.eraseAllEvidence()
        ie.makeInference()
        '''print(ie.nbrHardEvidence())
        print(ie.posterior('constraint'))
        print("MURDER WITH GUN before vE", ie.posterior('murder_with_gun'))
        print("FLEES before vE", ie.posterior('flees_in_car'))
        print(ie.posterior('scn1'))

        print("new evidence dict", new_evidence_dict)'''
        ie.setEvidence(new_evidence_dict)
        ie.addAllTargets()

        ie.makeInference()

        '''print(ie.posterior('constraint'))

        print(ie.nbrHardEvidence())

        print("has evidence", ie.hasEvidence('vE'))

        print("constraint after update with this evidence", ie.posterior('constraint'))
        print(ie.posterior('scn1'))
        print("MURDER WITH GUN after vE = 1", ie.posterior('murder_with_gun'))
        print("FLEES after vE", ie.posterior('flees_in_car'))
'''

        prior_to_condition_area_on = ie.posterior(entry)
        new_evidence_dict[entry] = 'yes'
        #print("add new evidence to dict ", new_evidence_dict)
        ie.setEvidence(new_evidence_dict)
        ie.makeInference()
        '''print(ie.posterior('constraint'))

        print(ie.nbrHardEvidence())

        print("constraint after this evidence: ", ie.posterior('constraint'), ie.posterior(entry))
        print(ie.posterior('scn1'))
        print("is target", ie.isTarget('murder_with_gun'))

        print("AFTER FLEES  vE", ie.posterior('flees_in_car'))

        print("AFTER MURDER", ie.posterior('murder_with_gun'))'''
        # on the first call, set evidence dict for positive atom, on the second call for the negated atom
        try:
            posterior_of_scn = ie.posterior('constraint')
            #print(prior_to_condition_area_on)
            index = int(base_case.scenario[-1])
            new_width = base_case.scn_width
            print(new_width)
            #print("\t posterior scenario: ", (posterior_of_scn[index]))
            #print("evidence:", new_evidence_dict)
            #print("posterior entry", entry, colored(prior_to_condition_area_on[{entry:index_posterior}], 'yellow'))
            #print("scenario: ", base_case.scenario, "area: ",
             #     colored(conditioned_area * (posterior_of_scn[index]) * (prior_to_condition_area_on[{entry:index_posterior}]), "blue"))

            '''print("in here")
            print(posterior_of_scn)
            print(colored(posterior_of_scn[{'constraint':'NA'}], 'blue'))
            print(colored(posterior_of_scn[{'constraint':'scn1'}], 'blue'))
            print(colored(posterior_of_scn[{'constraint':'scn2'}], 'blue'))
            print("posterior entry!!!")
            print("posterior entry", entry, colored(prior_to_condition_area_on[{entry:'yes'}], 'yellow'))'''


            #print(" & ", '{:0.2e}'.format(1 - posterior_of_scn[1]), " & ", '{:0.2e}'.format(1 - posterior_of_scn[2]), "& ", '{:0.2e}'.format((1 - posterior_of_scn[1])/(1 - posterior_of_scn[2])), "\\\\")

            '''
            print("evidence:", new_evidence_dict)
            print("posterior: ", posterior_of_scn)
            print("\t posterior scenario: ", (posterior_of_scn[index]))

            print("scenario: ", base_case.scenario, "area: ",
                  conditioned_area * (posterior_of_scn[index]) * (posterior_entry[index_posterior]))
            print("\t conditioned: ", conditioned_area)
            print("\t posterior entry: ", (posterior_entry[index_posterior]))
            '''
            if imported == 1:
                new_case = single_case.Case("None", dict(new_evidence_dict), new_width,
                                            conditioned_area * (1 - posterior_of_scn[index]) * (
                                            prior_to_condition_area_on[{entry:'yes'}]),
                                            # index_posterior always 1 on the first call and 0 on the second
                                            dict(full_dict),
                                            base_case.scenario)
            else:

                new_case = single_case.Case("None", dict(new_evidence_dict), new_width,
                                            conditioned_area * posterior_of_scn[index] *
                                            prior_to_condition_area_on[{entry:index_posterior}],
                                            # index_posterior always 1 on the first call and 0 on the second
                                            dict(full_dict),
                                            base_case.scenario)
            old_prior_dict[entry] = (posterior_entry[index_posterior])
            new_case.add_prior_dict(dict(old_prior_dict))
        except Exception:
            new_case = single_case.Case("Incompatible evidence", dict(new_evidence_dict), 0, 0,
                                        # index_posterior always 1 on the first call and 0 on the second
                                        dict(full_dict),
                                        base_case.scenario)
        return new_case


    def add_new_evidence_scenario(self, entry, truth_value, posterior_entry, ie, width, imported):
        self.old_cases.append(self.cases)
        list_1 = []
        for case in self.cases:
            if truth_value == 1:
                neg_truth_value = 0
            else:
                neg_truth_value = 1
            if imported == 1:
                list_1.append(self.generate_new_case(case, entry, truth_value, ie, width, posterior_entry, 0, imported))
                #list_1.append(self.generate_new_case(case, entry, neg_truth_value, ie, width, posterior_entry, 1, imported))
            else:
                print("adding new evidence: ", entry, truth_value)
                list_1.append(self.generate_new_case(case, entry, truth_value, ie, width, posterior_entry, 1, imported))
                list_1.append(self.generate_new_case(case, entry, neg_truth_value, ie, width, posterior_entry, 0, imported))
        self.cases = []
        for item in list_1:
            self.add_case(item)

    def find_posterior_events(self, entry, parent_of_entry, ie, imported):
        for case in self.cases:
            evidence_in_case = case.dict_evidence_value
            ie.setEvidence(evidence_in_case)
            check_list = list(case.event_list)
            case.event_list = []


            # get the posterior of the aspect node.
            try:
                posterior_parent_node = ie.posterior(parent_of_entry).tolist()
                # TODO: figure out how to deal with this -> at which point is the parent node "sustained"?
                if imported == 0:
                    if posterior_parent_node[0] > posterior_parent_node[1]:  # parent node is false
                        case.add_to_event_list(parent_of_entry, "neg")
                    else:  # parent node is true
                        case.add_to_event_list(parent_of_entry, "pos")
                else:
                    if posterior_parent_node[0] > posterior_parent_node[1]:  # parent node is false
                        case.add_to_event_list(parent_of_entry, "pos")
                    else:  # parent node is true
                        case.add_to_event_list(parent_of_entry, "neg")

                for item in check_list:  # recalculate for this as well
                    if "!" in item:
                        name = item[1:]
                    else:
                        name = item
                    posterior_parent_node = ie.posterior(name).tolist()
                    if posterior_parent_node[0] > posterior_parent_node[1]:  # parent node is false
                        case.add_to_event_list(name, "neg")
                    else:  # parent node is true
                        case.add_to_event_list(name, "pos")
            except Exception:
                case.add_to_event_list("incompatible evidence", "pos")



    def get_evidence_dict(self):
        return self.evidence

    def print_preference_ordering(self):
        newList = sorted(self.cases, key=lambda x: x.val, reverse=True)
        for case in newList:
            print(case.name, case.area_case)

    def print_preference_ordering_relevant_cases(self):  # only show greter than 0
        newList = sorted(self.cases, key=lambda x: x.val, reverse=True)
        for case in newList:
            if case.area_case > 0:
                print(case.name, case.area_case)
            else:
                break

    def print_case_model(self, full_case_model):
        self.get_figure_scenario_based(full_case_model)

    def get_figure_scenario_based(self, full_case_model):
        area_dict = {}
        for case in self.cases:
            area_dict[case.scenario] = 0
        for case in self.cases:
            area_dict[case.scenario] = area_dict[case.scenario] + case.area_case
        for case in self.cases:
            scn = case.scenario
            #case.scn_width = area_dict[scn]
        for case in self.cases:
            first_scn = case.scenario
            break

        figure = go.Figure()
        stack = 0
        width = 0
        scn = first_scn
        total_sum_area = 0
        for case in self.cases:
            val_val = case.check_with_evidence(self.evidence)
            total_sum_area = case.area_case + total_sum_area
            height_of_case = case.get_case_height()
            # if scenario changes, stack-height must reset and we must move to the right
            if case.scenario != scn:
                width = width_of_case + width
                stack = 0
                scn = case.scenario

            if val_val == True or val_val == False:
                print(case.get_case_width())
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
                figure.update_layout(yaxis_type='log')

            stack = stack + height_of_case


        print("\n")
        print(total_sum_area)
        figure.show()

    def get_figure_stacked(self, figure_stack, full_case_model, base_y_pos):
        self.get_figure_scenario_based(full_case_model)
        return
        area_dict = {}
        for case in self.cases:
            area_dict[case.scenario] = 0
        for case in self.cases:
            area_dict[case.scenario] = area_dict[case.scenario] + case.area_case
        for case in self.cases:
            scn = case.scenario
            #case.scn_width = area_dict[scn]
        for case in self.cases:
            first_scn = case.scenario
            break
        next_round = []
        figure = figure_stack
        stack = 0 + base_y_pos
        width = 0
        scn = first_scn
        total_sum_area = 0
        # add the evidence
        figure.add_trace(
            go.Scatter(x=[1.2], y=[stack + 1],
                       text=[self.get_string_evidence_added_this_step()], mode="text"))
        for case in self.cases:
            val_val = case.check_with_evidence(self.evidence)
            total_sum_area = case.area_case + total_sum_area
            #print(case.all_ev, case.get_case_width(), case.get_case_area())
            height_of_case = case.get_case_height()
            # if scenario changes, stack-height must reset and we must move to the right
            #print(case.scenario, scn)

            if case.scenario != scn:
                width = width_of_case + width
                stack = 0 + base_y_pos
                scn = case.scenario

            if val_val == True:
                width_of_case = case.get_case_width()
                case.collect_known_evidence()
                figure.add_trace(
                    go.Scatter(x=[width, width, width+width_of_case, width+width_of_case], y=[stack, stack+height_of_case, stack+height_of_case, stack], fill="toself"))
                figure.add_trace(
                    go.Scatter(x=[(case.get_case_width()/4)+width], y=[(height_of_case/2) + stack], text=[case.return_known_events()], mode="text"))

                figure.add_trace(
                    go.Scatter(x=[(case.get_case_width() / 2) + width], y=[(height_of_case / 4) + stack],
                               text=[round(case.area_case, 3)], mode="text"))

                figure.update_xaxes(range=[-0.1, 1.6])
                next_round.append(case)
            stack = stack + height_of_case

        #print("&",'{:0.2e}'.format(next_round[1].area_case), "&", '{:0.2e}'.format(next_round[0].area_case), "&", '{:0.2e}'.format(next_round[1].area_case/next_round[0].area_case), "\\\\")

        #self.cases = next_round # pruning
        #print("\n")
        #print(total_sum_area)

        return figure


