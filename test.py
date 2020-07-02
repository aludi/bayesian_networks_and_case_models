import generate_case_model.CaseModel as case_model
import generate_case_model.Prop as prop
import generate_case_model.Running as running
import generate_case_model.CMBN as cmbn
import generate_case_model.CaseModelFigure as cmFig
import unit_tests as unit_test

import pyAgrum as gum
#from termcolor import colored



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

    bn.cpt(scn_1).fillWith([0.8, 0.2])
    bn.cpt(scn_2).fillWith([0.3, 0.7])  # probability of accident

    bn.cpt(constraint)[{'scn_1':0, 'scn_2':0}] = [1, 0, 0]
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


def createBN_no_constraint_node():
    bn = gum.BayesNet("test")
    scn_1 = bn.add(gum.LabelizedVariable('scn_1', 'scn_1', ['false', 'true']))
    scn_2 = bn.add(gum.LabelizedVariable('scn_2', 'scn_2', ['false', 'true']))
    scn_3 = bn.add(gum.LabelizedVariable('scn_3', 'leak', ['false', 'true']))


    test1 = bn.add(gum.LabelizedVariable('test1', 'test1', ['false', 'true']))
    test2 = bn.add(gum.LabelizedVariable('test2', 'test2', ['false', 'true']))
    bn.addArc(scn_1, test1)
    bn.addArc(scn_2, test2)

    testEv1 = bn.add(gum.LabelizedVariable('testEv1', 'testEv1', ['false', 'true']))
    testEv2 = bn.add(gum.LabelizedVariable('testEv2', 'testEv2', ['false', 'true']))
    testEv3 = bn.add(gum.LabelizedVariable('testEv3', 'testEv3', ['false', 'true']))

    bn.addArc(test1, testEv1)
    bn.addArc(test2, testEv2)
    bn.addArc(test1, testEv3)
    bn.addArc(test2, testEv3)

    bn.cpt(scn_1).fillWith([0.8, 0.2])  # on purpose
    bn.cpt(scn_2).fillWith([0.3, 0.7])  # probability of accident
    bn.cpt(scn_3).fillWith([0.9, 0.1])  # something else happened


    bn.cpt(test1)[{'scn_1': 'false'}] = [0.8, 0.2]
    bn.cpt(test1)[{'scn_1': 'true'}] = [0, 1]

    bn.cpt(test2)[{'scn_2': 'false'}] = [0.6, 0.4]
    bn.cpt(test2)[{'scn_2': 'true'}] = [0.02, 0.98]

    bn.cpt(testEv1)[{'test1': 'false'}] = [0.67, 0.33]
    bn.cpt(testEv1)[{'test1': 'true'}] = [0.13, 0.87]
    bn.cpt(testEv2)[{'test2': 'false'}] = [0.99, 0.01]
    bn.cpt(testEv2)[{'test2': 'true'}] = [0.09, 0.91]
    bn.cpt(testEv3)[{'test1': 'false', 'test2': 'false'}] = [0.01, 0.99]
    bn.cpt(testEv3)[{'test1': 'false', 'test2': 'true'}] = [0.7, 0.3]
    bn.cpt(testEv3)[{'test1': 'true', 'test2': 'false'}] = [0.3, 0.7]
    bn.cpt(testEv3)[{'test1': 'true', 'test2': 'true'}] = [0, 1]
    return bn


def case_model_step(combined, cm_figure, evidence, truth_value):
    combined.add_evidence(evidence, truth_value)
    cm_figure.get_figure(evidence, truth_value)
    unit_test.check_ratios(combined)


def running_test_3():
    bn = createBN_no_constraint_node()
    combined = cmbn.CMBN(bn, ['true', 'false'])
    cm_figure = cmFig.CaseModelFigure(combined.casemodel)
    cm_figure.get_figure("", "")
    case_model_step(combined, cm_figure, 'testEv3', 'false')
    case_model_step(combined, cm_figure, 'testEv3', 'true')
    case_model_step(combined, cm_figure, 'testEv2', 'true')
    case_model_step(combined, cm_figure, 'testEv1', 'false')
    cm_figure.show()


def running_test_4():
    name_bn_imported = "real_yes_no_final_network_2020.net"
    bn = gum.loadBN(name_bn_imported)

    # only for Jurix 2019 paper  -> something's weird with Genie
    bn.cpt('gun')[{'motive': 'yes', 'scn1': 'yes'}] = [1, 0]
    bn.cpt('gun')[{'motive': 'yes', 'scn1': 'no'}] = [0.2, 0.8]
    bn.cpt('gun')[{'motive': 'no', 'scn1': 'yes'}] = [0, 1]
    bn.cpt('gun')[{'motive': 'no', 'scn1': 'no'}] = [0, 1]

    bn.cpt('murder_with_gun')[{'seen_in_hallway': 'yes', 'gun': 'yes', 'motive': 'yes', 'scn1': 'no'}] = [0.2, 0.8]
    bn.cpt('murder_with_gun')[{'seen_in_hallway': 'yes', 'gun': 'yes', 'motive': 'no', 'scn1': 'no'}] = [0.1, 0.9]
    bn.cpt('murder_with_gun')[{'seen_in_hallway': 'no', 'gun': 'yes', 'motive': 'yes', 'scn1': 'yes'}] = [0, 1]
    bn.cpt('murder_with_gun')[{'seen_in_hallway': 'no', 'gun': 'no', 'motive': 'yes', 'scn1': 'yes'}] = [0, 1]

    bn.cpt('car_with_bloodstains_found')[{'flees_in_car': 'yes'}] = [0.9, 0.1]
    bn.cpt('car_with_bloodstains_found')[{'flees_in_car': 'no'}] = [0.01, 0.99]

    bn.cpt('flees_in_car')[{'murder_with_gun': 'yes', 'scn1': 'yes'}] = [1, 0]
    bn.cpt('flees_in_car')[{'murder_with_gun': 'yes', 'scn1': 'no'}] = [0.6, 0.4]
    bn.cpt('flees_in_car')[{'murder_with_gun': 'no', 'scn1': 'yes'}] = [1, 0]
    bn.cpt('flees_in_car')[{'murder_with_gun': 'no', 'scn1': 'no'}] = [0.1, 0.9]

    combined = cmbn.CMBN(bn, ['yes', 'no'])

    cm_figure = cmFig.CaseModelFigure(combined.casemodel)
    cm_figure.get_figure("", "")
    case_model_step(combined, cm_figure, 'body_found', 'yes')
    case_model_step(combined, cm_figure, 'signs_of_violence', 'yes')
    case_model_step(combined, cm_figure, 'weapon_found', 'yes')


    case_model_step(combined, cm_figure, 'phonecall_with_friend', 'yes')
    case_model_step(combined, cm_figure, 'testimony_kidnapping', 'yes')
    case_model_step(combined, cm_figure, 'testimony_amnesia', 'yes')

    case_model_step(combined, cm_figure, 'car_with_bloodstains_found', 'yes')
    case_model_step(combined, cm_figure, 'testimony_conflict', 'yes')
    case_model_step(combined, cm_figure, 'no_concrete_evidence_for_kidnapping', 'yes')

    case_model_step(combined, cm_figure, 'medical_investigation_found_no_amnesia', 'yes')
    case_model_step(combined, cm_figure, 'phonecall_parents', 'yes')
    cm_figure.show()


### start here ###
test = 3
if test == 3:
    running_test_3()

if test == 4:
    running_test_4()