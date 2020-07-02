import generate_case_model.CaseModel as case_model
import generate_case_model.Case as case

import generate_case_model.Prop as prop
import plotly.graph_objects as go
import pyAgrum as gum


class CMBN:

    def __init__(self, bn, truth_values):
        self.truth_values = truth_values
        self.scenario_nodes = []
        try:
            bn.variable('constraint')
            try:
                bn.variable('aux')
            except:
                print("No aux node found, restructuring network into Fenton 2016 style")
                self.restructure_bn_fenton(bn)
        except:
            #print("No constraint-aux construction implemented yet. Doing that now.")
            self.implement_aux_constraint_structure(bn)
        self.bn = bn
        self.casemodel = case_model.CaseModel([({}, 1)])
        ie = gum.LazyPropagation(bn)
        self.ie = ie
        self.global_evidence_dict = {'constraint': truth_values[0]}
        ie.setEvidence(self.global_evidence_dict)
        self.create_first_cases()

    def add_evidence(self, evidence, truth_value):
        add_or_change = 'add'
        prior_evidence = self.ie.posterior(evidence)[{evidence: truth_value}]  # not actually a true prior, conditioned on other pieces of evidence that are already added
        if evidence in self.global_evidence_dict.keys():
            add_or_change = 'change'
            # we're updating our evidence.
        self.global_evidence_dict[evidence] = truth_value
        self.ie.setEvidence(self.global_evidence_dict)
        for case in self.casemodel.cases:
            case.update_conditional_prior_dict(evidence, prior_evidence, add_or_change)
            conditioned_case_area = case.calculate_conditioned_area()
            posterior_scn = self.ie.posterior('aux')[{'aux':case.scenario}]
            case.evidence_dict[evidence] = truth_value
            case.area = conditioned_case_area * posterior_scn
            self.deal_with_event_nodes(case, evidence)


    def deal_with_event_nodes(self, case, evidence):
        event_nodes_scn = self.check_event_nodes_in_scenario(case.scenario)
        if len(event_nodes_scn) > 0:
            for event_node in event_nodes_scn:  # only do this for direct parents of node. Bad assumption
                if event_node in self.bn.parents(evidence):
                    name_node = self.bn.variable(event_node).name()
                    if self.ie.posterior(event_node)[{name_node: self.truth_values[1]}] > self.ie.posterior(event_node)[
                        {name_node: self.truth_values[0]}]:  # truth_values[0]: yes/true
                        case.update_event_nodes(name_node, self.truth_values[1])
                    else:
                        case.update_event_nodes(name_node, self.truth_values[0])

    def check_event_nodes_in_scenario(self, scenario_name):
        id_head = self.bn.idFromName(scenario_name)
        list_event_nodes = self.bn.children(id_head)
        return list_event_nodes

    def get_scenario_names(self):
        return self.scenario_nodes

    def create_first_cases(self):
        new_case_list = []
        for scn in self.scenario_nodes:
            p = self.bn.cpt(scn)
            i = gum.Instantiation(p)
            i.setFirst()
            while (not i.end()):
                dict_of_row = i.todict(withLabels=True)
                if dict_of_row[scn] == self.truth_values[0]:      # only select the 'true' priors for the first case model line
                    case_name = scn
                    case_scenario = scn
                    case_area = p.get(i)
                    case_width = p.get(i)
                    case_conditional_prior_dict = {scn : case_area}
                    case_evidence_dict = {}
                    new_case = case.Case(case_name, case_scenario, case_area, case_width,
                                        case_conditional_prior_dict, case_evidence_dict)
                    new_case_list.append(new_case)
                i.inc()
        self.casemodel.cases = new_case_list

    def print_cases(self):
        for one_case in self.casemodel.cases:
            print(one_case.name, one_case.area, one_case.conditional_prior_dict)


    def implement_aux(self, bn):
        p_aux = bn.cpt('aux')
        i_aux = gum.Instantiation(p_aux)
        i_aux.setFirst()
        while (not i_aux.end()):
            dict_of_row = i_aux.todict(withLabels=True)
            values = list(dict_of_row.values())
            num_true = values.count(self.truth_values[0])
            if num_true < 1 or num_true > 1:  # no scenario is true, aux is NA
                if dict_of_row['aux'] == "NA":
                    p_aux.set(i_aux, 1)
                else:
                    p_aux.set(i_aux, 0)
            else:
                true_scenario = False
                for key in dict_of_row.keys():
                    if dict_of_row[key] == self.truth_values[0]:
                        true_scenario = key
                if dict_of_row['aux'] == true_scenario:
                    p_aux.set(i_aux, 1)
                else:
                    p_aux.set(i_aux, 0)
            i_aux.inc()

    def implement_constraint(self, bn):
        bn.cpt('constraint')
        p_con = bn.cpt('constraint')
        i_con = gum.Instantiation(p_con)
        i_con.setFirst()
        while (not i_con.end()):
            dict_of_row = i_con.todict(withLabels=True)
            values = list(dict_of_row.values())
            scn, truth_val = dict_of_row['aux'], dict_of_row['constraint']
            if scn == "NA":
                if truth_val == self.truth_values[1]:
                    p_con.set(i_con, 1)
                else:
                    p_con.set(i_con, 0)
            else:
                index_of_label = bn.variable(scn).index(
                    truth_val)  # i hate this, but this is the only way to access labels in vars
                p_con.set(i_con, 1 - bn.cpt(scn)[index_of_label])
            i_con.inc()

    def implement_aux_constraint_structure(self, bn):
        list_of_scn_node_names = ["NA"]
        for i in bn.nodes():
            if 'scn' in bn.variable(i).name():
                list_of_scn_node_names.append(bn.variable(i).name())
        n_states_in_constraint_node = len(list_of_scn_node_names)  # this is n(scn) + 1
        aux = bn.add(gum.LabelizedVariable('aux', 'aux', list_of_scn_node_names))
        constraint = bn.add(
            gum.LabelizedVariable('constraint', 'constraint', self.truth_values))  # aux always has two states
        # all nodes are added now... Now add links between the nodes.
        list_of_scn_node_names.remove("NA")
        self.scenario_nodes = list_of_scn_node_names
        for node_name in list_of_scn_node_names:
            bn.addArc(node_name, 'aux')
        bn.addArc('aux', 'constraint')
        self.implement_aux(bn)
        self.implement_constraint(bn)

    def restructure_bn_fenton(self, bn):        # could be streamlined
        bn.erase('constraint')
        list_of_scn_node_names = ["NA"]
        exhaustivity_check = 0
        for i in bn.nodes():
            if 'scn' in bn.variable(i).name():
                list_of_scn_node_names.append(bn.variable(i).name())
                exhaustivity_check = exhaustivity_check + bn.cpt(i)[0]
        if exhaustivity_check != 1:
            # add a leak state
            scn_3 = bn.add(gum.LabelizedVariable('scn_leak', 'leak', self.truth_values))
            bn.cpt(scn_3) [{'scn_leak': self.truth_values[0]}] = 1 - exhaustivity_check
            bn.cpt(scn_3)[{'scn_leak': self.truth_values[1]}] = exhaustivity_check
            list_of_scn_node_names.append(bn.variable('scn_leak').name())

        n_states_in_constraint_node = len(list_of_scn_node_names)  # this is n(scn) + 1
        aux = bn.add(gum.LabelizedVariable('aux', 'aux', list_of_scn_node_names))
        constraint = bn.add(
            gum.LabelizedVariable('constraint', 'constraint', self.truth_values))  # aux always has two states
        # all nodes are added now... Now add links between the nodes.
        list_of_scn_node_names.remove("NA")
        self.scenario_nodes = list_of_scn_node_names
        for node_name in list_of_scn_node_names:
            bn.addArc(node_name, 'aux')
        bn.addArc('aux', 'constraint')
        self.implement_aux(bn)
        self.implement_constraint(bn)

