import generate_case_model.Case as single_case
import generate_case_model.CaseModel as case_model
import generate_case_model.Prop as prop
import generate_case_model.Running as running
import pyAgrum as gum
from termcolor import colored



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


def running_test_1():
    imported = 0
    name_bn_imported = "none"
    bn = createBN()

    ''' virtual evidence: '''
    vE = bn.add(gum.LabelizedVariable('vE', 'vE', 2))
    constraint = bn.variable('constraint').name()
    bn.addArc('constraint', 'vE')
    bn.cpt("vE")[{'constraint': 0}] = [1, 0]
    bn.cpt("vE")[{'constraint': 1}] = [1, 0.5]
    bn.cpt("vE")[{'constraint': 2}] = [1, 0.5]

    ie = gum.LazyPropagation(bn)
    ie.setEvidence({'vE': 1})  # setting VIRTUAL (soft) evidence to force the constraint node.
    initial = running.Running(bn, imported, ie)

    caseModel = initial.get_caseModel()
    total_ev_dict = initial.get_total_ev_dict()
    figure, full_case_model, base_y_pos = initial.get_params_figure()

    caseModel.set_dict_of_all_ev_nodes(total_ev_dict)
    caseModel.evidence['vE'] = 1
    caseModel.add_evidence_scenario("vE", 1, ie, imported)
    caseModel.update_the_dict_with_priors(ie, imported)
    figure = caseModel.get_figure_stacked(figure, full_case_model, base_y_pos)


    evidence = 'testEv2'
    truth_val = 0
    caseModel.add_evidence_scenario(evidence, truth_val, ie, imported=0)

    initial.find_posterior_events(bn, caseModel, evidence, ie, 0)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)
    #print("testev2 0 ", colored(ie.posterior('constraint'), "red"))
    #print("evidence: ", caseModel.evidence)


    caseModel.add_evidence_scenario('testEv1', 1, ie, 0)
    initial.find_posterior_events(bn, caseModel, 'testEv1', ie, 0)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)
    '''print("testev1 1 ", colored(ie.posterior('constraint'), "red"))
    print("evidence: ", caseModel.evidence)'''


    caseModel.add_evidence_scenario('testEv3', 1, ie, 0)
    initial.find_posterior_events(bn, caseModel, 'testEv3', ie, 0)
    # caseModel.print_case_model(full_case_model)
    initial.decrease_y_base()
    figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    '''print("testev3 1 ", colored(ie.posterior('constraint'), "red"))
    print("evidence: ", caseModel.evidence)'''
    initial.set_figure(new_figure)

    initial.get_figure().show()


def running_test_2():
    imported = 1
    name_bn_imported = "real_yes_no_final_network_2020.net"
    bn = gum.loadBN(name_bn_imported)

    # only for Jurix 2019 paper
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

    ''' virtual evidence: '''
    vE = bn.add(gum.LabelizedVariable('vE', 'vE', 2))
    constraint = bn.variable('constraint').name()
    bn.addArc('constraint', 'vE')
    bn.cpt("vE")[{'constraint': 0}] = [1, 0]
    bn.cpt("vE")[{'constraint': 1}] = [1, 0.5]
    bn.cpt("vE")[{'constraint': 2}] = [1, 0.5]

    ie = gum.LazyPropagation(bn)
    ie.setEvidence({'vE': 1})  # setting VIRTUAL (soft) evidence to force the constraint node.
    initial = running.Running(bn, imported, ie)

    caseModel = initial.get_caseModel()
    total_ev_dict = initial.get_total_ev_dict()
    figure, full_case_model, base_y_pos = initial.get_params_figure()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)
    print("body\_found", end=' ')

    body_found = bn.variable('body_found').name()
    caseModel.add_evidence_scenario('body_found', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'body_found', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(new_figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)
    caseModel.get_single_case_model_picture()
    exit()

    '''print("body found ", colored(ie.posterior('constraint'), "green"))
    print("ratio bn (scn2/scn1)", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''

    print("signs\_of\_violence", end=' ')

    ie.setEvidence({'vE': 1})
    caseModel.add_evidence_scenario('signs_of_violence', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'signs_of_violence', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(new_figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)


    '''print("signs of violence ", colored(ie.posterior('constraint'), "green"))
    print("ratio cases", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''

    print("weapon\_found", end=' ')

    ie.setEvidence({'vE': 1})
    caseModel.add_evidence_scenario('weapon_found', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'weapon_found', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(new_figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)


    '''print("weapon found ", colored(ie.posterior('constraint'), "green"))
    print("ratio cases", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''

    print("phonecall\_with\_friend", end=' ')

    caseModel.add_evidence_scenario('phonecall_with_friend', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'phonecall_with_friend', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)

    ''' print("phonecall with friends ", colored(ie.posterior('constraint'), "green"))
    print("ratio", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''

    print("testimony\_kidnapping", end=' ')

    caseModel.add_evidence_scenario('testimony_kidnapping', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'testimony_kidnapping', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)

    '''print("testimony kidnapping ", colored(ie.posterior('constraint'), "green"))
    print("ratio cases", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])
'''
    print("testimony\_amnesia", end=' ')

    caseModel.add_evidence_scenario('testimony_amnesia', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'testimony_amnesia', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)

    '''print("testimony amnesia ", colored(ie.posterior('constraint'), "green"))
    print("ratio cases", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''

    print("car\_with\_bloodstains", end=' ')

    caseModel.add_evidence_scenario('car_with_bloodstains_found', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'car_with_bloodstains_found', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)

    '''print("car with bloodstains ", colored(ie.posterior('constraint'), "green"))
    print("ratio cases", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''

    print("testimony\_conflict", end=' ')


    caseModel.add_evidence_scenario('testimony_conflict', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'testimony_conflict', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)
    '''print("testimony conflict ", colored(ie.posterior('constraint'), "green"))
    print("ratio cases", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''

    print("no\_concrete\_evidence\_for\_kidnapping", end=' ')

    caseModel.add_evidence_scenario('no_concrete_evidence_for_kidnapping', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'no_concrete_evidence_for_kidnapping', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)

    '''print("no concrete evidence for kidnapping ", colored(ie.posterior('constraint'), "green"))
    print("ratio cases", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''

    print("medical\_investigation\_found\_no\_amnesia", end=' ')

    caseModel.add_evidence_scenario('medical_investigation_found_no_amnesia', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'medical_investigation_found_no_amnesia', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)

    '''print("medical investigation found no amnesia ", colored(ie.posterior('constraint'), "green"))
    print("ratio cases", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''

    print("phonecall\_parents", end=' ')

    caseModel.add_evidence_scenario('phonecall_parents', 1, ie, imported)
    initial.find_posterior_events(bn, caseModel, 'phonecall_parents', ie, imported)
    initial.decrease_y_base()
    new_figure = caseModel.get_figure_stacked(figure, full_case_model, initial.get_y_base())
    initial.set_figure(new_figure)

    '''print("phonecall parents ", colored(ie.posterior('constraint'), "green"))
    print("ratio cases", ie.posterior('constraint').tolist()[1]/ie.posterior('constraint').tolist()[2])'''


    initial.get_figure().show()


### start here ###
test = 2
if test == 1:
    running_test_1()

if test == 2:
    running_test_2()
