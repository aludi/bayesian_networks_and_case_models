import generate_case_model.Case as single_case
import generate_case_model.CaseModel as case_model
import generate_case_model.Prop as prop
import pyAgrum as gum
import anytree.search
from anytree import RenderTree, PreOrderIter
import plotly.graph_objects as go



def createBN():
    bn = gum.BayesNet("test")
    # to implement a constraint node, necessarily, can't use anytree (Tree) structure,
    # but need to use a graph structure, because the constraint node has two parents (not allowed in tree)

    scn_1 = bn.add(gum.LabelizedVariable('scn_1', 'scn_1', 2))
    scn_2 = bn.add(gum.LabelizedVariable('scn_2', 'scn_2', 2))
    constraint = bn.add(gum.LabelizedVariable('constraint', 'constraint', 3))
    bn.addArc(scn_1, constraint)
    bn.addArc(scn_2, constraint)

    test1 = bn.add(gum.LabelizedVariable('test1', 'test1', 2))
    test2 = bn.add(gum.LabelizedVariable('test2', 'test2', 2))
    bn.addArc(scn_1, test1)
    bn.addArc(scn_2, test2)

    testEv1 = bn.add(gum.LabelizedVariable('testEv1', 'testEv1', 2))
    testEv2 = bn.add(gum.LabelizedVariable('testEv2', 'testEv2', 2))
    testEv3 = bn.add(gum.LabelizedVariable('testEv3', 'testEv3', 2))

    bn.addArc(test1, testEv1)
    bn.addArc(test2, testEv2)
    bn.addArc(test1, testEv3)
    bn.addArc(test2, testEv3)


    #bn.cpt(scn_1).fillWith([0.99,0.01])  # probability of murder (lol) -> prior on murder is really low.
    #bn.cpt(scn_2).fillWith([0.02, 0.98])  # probability of accident

    #test
    bn.cpt(scn_1).fillWith([0.8, 0.2])  # probability of murder (lol) -> prior on murder is really low.
    bn.cpt(scn_2).fillWith([0.3, 0.7])  # probability of accident


    bn.cpt(constraint)[{'scn_1':0, 'scn_2':0}] = [0.5, 0, 0.5]
    bn.cpt(constraint)[{'scn_1':0, 'scn_2':1}] = [0, 0, 1]
    bn.cpt(constraint)[{'scn_1':1, 'scn_2':0}] = [0, 1, 0]
    bn.cpt(constraint)[{'scn_1':1, 'scn_2':1}] = [1, 0, 0]

    bn.cpt(test1)[{'scn_1':0}]=[0.8, 0.2]
    bn.cpt(test1)[{'scn_1':1}]=[0, 1]

    bn.cpt(test2)[{'scn_2':0}]=[0.6, 0.4]
    bn.cpt(test2)[{'scn_2':1}]=[0.02, 0.98]

    bn.cpt(testEv1)[{'test1':0}]=[0.67, 0.33]
    bn.cpt(testEv1)[{'test1':1}]=[0.13, 0.87]
    bn.cpt(testEv2)[{'test2':0}]=[0.99, 0.01]
    bn.cpt(testEv2)[{'test2':1}]=[0.09, 0.91]
    bn.cpt(testEv3)[{'test1':0, 'test2': 0}]=[0.01, 0.99]
    bn.cpt(testEv3)[{'test1':0, 'test2': 1}]=[0.7, 0.3]
    bn.cpt(testEv3)[{'test1':1, 'test2': 0}]=[0.3, 0.7]
    bn.cpt(testEv3)[{'test1':1, 'test2': 1}]=[0, 1]
    return bn


def return_dict_for_cpt(value_dict, parentNode):
    if parentNode.name[0] == "!":
        actual_name = parentNode.name[1:]
        value = 0
        value_dict[actual_name] = value
    elif parentNode.name != "Root" and parentNode.name[0] != "!":
        actual_name = parentNode.name
        value = 1
        value_dict[actual_name] = value
    return value_dict

def recursing_children1(name, parent, tree):
    print("CHILDREN OF NAME: ", bn.children(name), name)
    if str(bn.children(name)) == "set()":   # we found a leaf
        parentName = bn.variable(parent).name()
        #value_dict = {}
        #value_dict = return_dict_for_cpt(value_dict, parentName)
        #print(name, value_dict)
        #for node in parentName.ancestors:
        #    value_dict = return_dict_for_cpt(value_dict, node)
        #final_array = bn.cpt(name)[value_dict]
        #print(final_array)
        good_name = bn.variable(name).name()
        node_pos = prop.Prop(good_name)
        node_neg = prop.Prop("!" + good_name)
        #node_pos.add_scenario(scenario.get_scenarios())
        #node_neg.add_scenario(scenario.get_scenarios())
        #node_pos.set_area(final_array[1])
        #node_neg.set_area(final_array[0])
        print("leaf nodes pos and neg", node_pos, node_neg)
        return node_pos, node_neg
    else:
        name_string = bn.variable(name).name()
        for child in bn.children(name):
            print("CHILD:", child, "NAME CHILD: ",bn.variable(child).name())
            name = bn.variable(child).name()
            if name != "constraint":
                pos, neg = recursing_children1(child, name, tree)
                print("leaf nodes pos ans neg in base: ", pos, neg)
                pos.parent(child.name)
                neg.parent("!"+child.name)

                for pre, fill, node in RenderTree(scenario):
                    print("%s%s %s %s  %s" % (pre, node.name, node.area, node.truth_value, node.tag))

def recursing_children(parent, ie):
    name_parent = parent.name
    if "!" in name_parent:
        name_parent = name_parent[1:]
    children = bn.children(name_parent)
    if str(children) != "set()":
        for child in children:
            good_name = bn.variable(child).name()
            value_dict = {}
            if "!" in parent.name:
                value_dict[parent.name[1:]] = parent.truth_value
            else:
                value_dict[parent.name] = parent.truth_value

            if good_name != 'constraint':
                for node in parent.ancestors:
                    if "!" in node.name:
                        value_dict[node.name[1:]] = node.truth_value
                    else:
                        value_dict[node.name] = node.truth_value
                #print(value_dict)
                node_pos = prop.Prop(good_name, parent=parent)
                node_neg = prop.Prop("!" + good_name, parent=parent)
                #print("\t", good_name, " : ", bn.cpt(good_name)[value_dict].tolist())
                final_array = bn.cpt(good_name)[value_dict].tolist()
                if type(final_array[0]) != float:
                    #get ie.posterior for preconditions -> weighted sum
                    ie.setEvidence(value_dict)
                    #print("name node: ", good_name, "values : ", ie.posterior(good_name), "dict vals : ", value_dict)
                    final_array = ie.posterior(good_name).tolist()
                    ie.eraseAllEvidence()
                node_pos.set_area(final_array[1])
                node_neg.set_area(final_array[0])
                node_pos.add_scenario(parent.get_scenario())
                node_neg.add_scenario(parent.get_scenario())

                '''
                parentName = bn.variable(name_parent).name()
                value_dict = {}
                value_dict = return_dict_for_cpt(value_dict, parent)
                print(good_name, value_dict)
                for node in parent.ancestors:
                    value_dict = return_dict_for_cpt(value_dict, node)
                final_array = bn.cpt(good_name)[value_dict]
                print(final_array)
                node_pos.set_area(final_array[1])
                node_neg.set_area(final_array[0])

                #node_pos.add_scenario(parent.get_scenarios())
                #node_neg.add_scenario(parent.get_scenarios())
                '''
                recursing_children(node_pos, ie)
                recursing_children(node_neg, ie)

            else:
                ie.posterior('constraint')


def recursing_children_for_dict(parent, ie, scn_dict_ev, scn_dict_area):
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
                recursing_children_for_dict(node, ie, scn_dict_ev, scn_dict_area)
            else:
                ie.posterior('constraint')
    else:
        parent.set_tag("EVIDENCE")
    return scn_dict_ev, scn_dict_area

def find_posterior_events(bn, caseModel, evidence, ie):
    print(evidence)
    x = bn.variable(evidence).name()
    parent_node = bn.parents(x).pop()        # evidence/entry has one parent because evidence supports one node (TODO: more nodes) -> parent is a set
    parent_node = bn.variable(parent_node).name()
    print(parent_node)

    caseModel.find_posterior_events(evidence, parent_node, ie)


bn = gum.loadBN("final_2020_reordered_constraint_node.net")
print(bn)
#bn = createBN()
caseModelDomainSpace = 1
cases = [({}, 1)]  # ([], 1)
bn.names()
list_of_scenarios = []
ie = gum.LazyPropagation(bn)

for x in bn.names():
    node_name = bn.variable(x).name()
    print(node_name)
    print(ie.posterior(node_name).tolist())
    #print(bn.parents(x))
    if str(bn.parents(x)) != "set()":
        for item in bn.parents(x):
            pass
            #print(bn.variable(item).name())
    if "scn" in node_name:
        ie.setEvidence({'constraint': [0, 1, 1]})       # setting soft evidence to force the constraint node.
        prior_on_scenarios = ie.posterior('constraint').tolist()
        print(ie.posterior('constraint'), node_name)
        index_in_constraint_table = node_name[-1]
        print(index_in_constraint_table)
        prior_scenario_value = prior_on_scenarios[int(index_in_constraint_table)]
        #print("prior scenario value: ", prior_scenario_value)
        node_atom = prop.Prop(node_name, prior_scenario_value, truth_value=1, tag="SCENARIO")
        print(node_name, prior_scenario_value)
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
    #print(cases)

root_arg = prop.Prop("Root", 1, tag="SPACE")
scenario_dict_ev = {}
scenario_dict_area = {}
total_ev_dict = {}

case_list = []
for scenario in list_of_scenarios:
    new_dict_ev = {scenario.name: scenario.truth_value}
    print(new_dict_ev)
    new_dict_area = {scenario.name: scenario.area}
    print(new_dict_area)
    new_dict_ev, new_dict_area = recursing_children_for_dict(scenario, ie, new_dict_ev, new_dict_area)
    scenario_dict_key = scenario.name
    scenario_dict_ev[scenario_dict_key] = new_dict_ev
    total_ev_dict = {**total_ev_dict,  **scenario_dict_ev[scenario_dict_key]}
    case_area = 1
    case = single_case.Case(scenario.name, new_dict_ev, scenario.area, scenario.area, total_ev_dict, scenario.name)
    case_list.append(case)

new_list = []
for case in case_list:
    case.all_ev = dict(total_ev_dict)
    for key in case.all_ev:
        case.all_ev[key] = None
caseModel = case_model.CaseModel(case_list)

full_case_model = True
figure = go.Figure()
base_y_pos = 0

caseModel.set_dict_of_all_ev_nodes(total_ev_dict)
caseModel.evidence['constraint'] = [0, 1, 1]
#caseModel.print_case_model(full_case_model)
figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)

caseModel.add_evidence_scenario('body_found', 1, ie)
find_posterior_events(bn, caseModel, 'body_found', ie)
caseModel.print_case_model(full_case_model)
base_y_pos = base_y_pos - 2
figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)


'''
caseModel.add_evidence_scenario('weapon_found', 1, ie)
find_posterior_events(bn, caseModel, 'weapon_found', ie)
#caseModel.print_case_model(full_case_model)
base_y_pos = base_y_pos - 2
figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)
'''
'''
evidence = 'testEv2'
truth_val = 0
caseModel.add_evidence_scenario(evidence, truth_val, ie)
find_posterior_events(bn, caseModel, evidence, ie)
#caseModel.find_posterior_events(evidence, ie)
#caseModel.print_case_model(full_case_model)
base_y_pos = base_y_pos - 2
figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)


caseModel.add_evidence_scenario('testEv1', 1, ie)
find_posterior_events(bn, caseModel, 'testEv1', ie)
#caseModel.print_case_model(full_case_model)
base_y_pos = base_y_pos - 2
figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)


caseModel.add_evidence_scenario('testEv1', 0, ie)
find_posterior_events(bn, caseModel, 'testEv1', ie)
#caseModel.print_case_model(full_case_model)
base_y_pos = base_y_pos - 2
figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)


caseModel.add_evidence_scenario('testEv1', 1, ie)
find_posterior_events(bn, caseModel, 'testEv1', ie)
#caseModel.print_case_model(full_case_model)
base_y_pos = base_y_pos - 2
figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)


caseModel.add_evidence_scenario('testEv2', 0, ie)
find_posterior_events(bn, caseModel, 'testEv2', ie)
#caseModel.print_case_model(full_case_model)
base_y_pos = base_y_pos - 2
figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)

caseModel.add_evidence_scenario('testEv3', 1, ie)
find_posterior_events(bn, caseModel, 'testEv3', ie)
#caseModel.print_case_model(full_case_model)
base_y_pos = base_y_pos - 2
figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)
'''

