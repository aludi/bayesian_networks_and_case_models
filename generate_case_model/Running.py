import generate_case_model.Case as single_case
import generate_case_model.CaseModel as case_model
import generate_case_model.Prop as prop
import pyAgrum as gum

class Running:
    def __init__(self, bayesian_network):
        self.caseModel = self.run_cm_conversion_on_bn(bayesian_network)
        self.evidence = None

    def set_evidence(self):
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
        return caseModel
