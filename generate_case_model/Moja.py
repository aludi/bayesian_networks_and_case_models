import generate_case_model.Case as single_case
import generate_case_model.CaseModel as case_model
import generate_case_model.Moja_Case as moja_case

import generate_case_model.Prop as prop
import plotly.graph_objects as go
import pyAgrum as gum


class Moja:

    def __init__(self, bn):
        self.scenario_nodes = []
        try:
            bn.variable('aux')
        except:
            #print("No constraint-aux construction implemented yet. Doing that now.")
            self.implement_aux_constraint_structure(bn)
        self.bn = bn
        self.casemodel = case_model.CaseModel([({}, 1)])
        ie = gum.LazyPropagation(bn)
        self.ie = ie
        self.global_evidence_dict = {'constraint': 'true'}
        ie.setEvidence(self.global_evidence_dict)
        self.create_first_cases()
        self.print_cases()

    def add_evidence(self, evidence, truth_value):
        # add the new evidence to the evidence that we already have
        add_or_change = 'add'
        prior_evidence = self.ie.posterior(evidence)[{
            evidence: truth_value}]  # not actually a true prior, conditioned on other pieces of evidence that are already added
        if evidence in self.global_evidence_dict.keys():
            add_or_change = 'change'
            # we're updating our evidence.


        self.global_evidence_dict[evidence] = truth_value
        # find prior of evidence
        print(self.ie.posterior('aux'))
        print(self.ie.posterior(evidence))  # problem!! -> switch evidence around
        #print(self.ie.posterior(evidence)[{evidence:'false'}], self.ie.posterior(evidence)[{evidence:'true'}])


        self.ie.setEvidence(self.global_evidence_dict)
        '''print("aux after new evidence", self.ie.posterior('aux'))'''

        for case in self.casemodel.cases:
            case.update_conditional_prior_dict(evidence, prior_evidence, add_or_change)
            conditioned_case_area = case.calculate_conditioned_area()
            posterior_scn = self.ie.posterior('aux')[{'aux':case.scenario}]
            case.evidence_dict[evidence] = truth_value
            print("posterior scenario  ", posterior_scn)
            print("posterior case  ", conditioned_case_area * posterior_scn)
            case.area = conditioned_case_area * posterior_scn
        #print(self.ie.posterior('aux'))


    def create_first_cases(self):
        new_case_list = []
        for scn in self.scenario_nodes:
            p = self.bn.cpt(scn)
            i = gum.Instantiation(p)
            i.setFirst()
            while (not i.end()):
                dict_of_row = i.todict(withLabels=True)
                if dict_of_row[scn] == 'true':      # only select the 'true' priors for the first case model line
                    case_name = scn
                    case_scenario = scn
                    case_area = p.get(i)
                    case_width = p.get(i)
                    case_conditional_prior_dict = {scn : case_area}
                    case_evidence_dict = {}
                    new_case = moja_case.Moja_Case(case_name, case_scenario, case_area, case_width,
                                        case_conditional_prior_dict, case_evidence_dict)
                    new_case_list.append(new_case)
                i.inc()
        self.casemodel.cases = new_case_list

    def print_cases(self):
        for case in self.casemodel.cases:
            print(case.name, case.area, case.conditional_prior_dict)


    def implement_aux(self, bn):
        p_aux = bn.cpt('aux')
        i_aux = gum.Instantiation(p_aux)
        i_aux.setFirst()
        while (not i_aux.end()):
            dict_of_row = i_aux.todict(withLabels=True)
            values = list(dict_of_row.values())
            num_true = values.count('true')
            if num_true < 1 or num_true > 1:  # no scenario is true, aux is NA
                if dict_of_row['aux'] == "NA":
                    p_aux.set(i_aux, 1)
                else:
                    p_aux.set(i_aux, 0)
            else:
                true_scenario = False
                for key in dict_of_row.keys():
                    if dict_of_row[key] == 'true':
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
                if truth_val == "false":
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
            gum.LabelizedVariable('constraint', 'constraint', ['false', 'true']))  # aux always has two states
        # all nodes are added now... Now add links between the nodes.
        list_of_scn_node_names.remove("NA")
        self.scenario_nodes = list_of_scn_node_names
        for node_name in list_of_scn_node_names:
            bn.addArc(node_name, 'aux')
        bn.addArc('aux', 'constraint')
        self.implement_aux(bn)
        self.implement_constraint(bn)





