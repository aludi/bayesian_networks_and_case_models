class Case:
    '''
    def __init__(self, list_props, value, dict_priors, leaf, scn):
        self.list_case = list_props
        self.val = value
        self.dict_priors = dict_priors
        self.dict_current_posterior = dict_priors
        self.evidence_added = None
        self.base_leaf = leaf
        self.corresponding_scenario = scn
    '''

    def __init__(self, name, ev_dict_case, scn_area, total_area_case, all_ev, scenario_name):
        self.name = name
        self.all_ev = all_ev
        self.dict_evidence_value = ev_dict_case
        self.scn_width = scn_area
        self.scenario = scenario_name
        self.area_case = total_area_case
        self.list_known_evidence = []
        self.prior_dict = {}
        self.event_list = []

    def add_prior_dict(self, new_prior_dict):
        self.prior_dict = new_prior_dict

    def improve_name_list(self, entry, truth_value, flag):
        if flag == "changing evidence":
            if truth_value == 1:
                self.list_known_evidence.remove("!"+entry)
            elif truth_value == 0:
                self.list_known_evidence.remove(entry)

        if truth_value == 0:
            list_add = "!"+entry
        else:
            list_add = entry
        self.list_known_evidence.append(list_add)

    def add_to_event_list(self, event, value_string):
        if value_string == "neg":
            self.event_list.append("!"+event)
        else:
            self.event_list.append(event)


    def print_case_scn(self):
        print(self.scenario)

    def get_case_scenario(self):
        return self.scenario

    def get_case_width(self):
        return self.scn_width

    def get_case_area(self):
        return self.area_case

    def set_case_area(self, case_area_val):
        self.area_case = case_area_val

    def update_dict(self, dict_new):
        self.all_ev = dict_new
        self.dict_evidence_value = dict_new
        return

    def collect_known_evidence(self):
        self.list_known_evidence = [self.scenario]
        dict_of_evidence = self.all_ev
        for key in dict_of_evidence:
            if dict_of_evidence[key] == 1:
                self.list_known_evidence.append(key)
            if dict_of_evidence[key] == 0:
                self.list_known_evidence.append("!"+key)
        for item in self.event_list:
            self.list_known_evidence.append(item)

    def check_with_evidence(self, evidence_from_case_model):
        for key in evidence_from_case_model:
            if "scn" in key or "constraint" in key:
                continue
            if self.all_ev[key] != evidence_from_case_model[key]:
                #print(key, self.all_ev[key], evidence_from_case_model[key])
                return False
        return True



    # case width * case height = case area
    # this must always be true
    # width of a case must always corresponds to the width of the scenario
    # case area is determined by ?? -> impact of evidence on the case. but this is also determined
    # so we can easily find case height always
    def get_case_height(self):
        return self.area_case/self.scn_width

    #def get_case_prop_areas_dict(self):
    #    return self.dict_area_value
