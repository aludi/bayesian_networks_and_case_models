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

    def __init__(self, name, ev_dict_case, area_dict_case, all_ev):
        self.name = name
        self.all_ev = all_ev
        #self.total_dict_case = dict_case
        self.dict_evidence_value = ev_dict_case
        self.dict_area_value = area_dict_case

        total_area_case = 1
        for key in ev_dict_case.keys():
            print(key.name, ev_dict_case[key])
            self.scenario = key.get_scenario()
            area_val = self.dict_evidence_value[key]
            if 'scn' in key.name:
                self.width = area_val
            if area_val is None:
                total_area_case = total_area_case*1
            else:
                total_area_case = total_area_case*area_val

        self.area_case = total_area_case
        self.list_known_evidence = [self.scenario]

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

    def print_case_scn(self):
        print(self.scenario)

    def get_case_scenario(self):
        return self.scenario

    def get_case_width(self):
        return self.width

    def get_case_area(self):
        return self.area_case

    def set_case_area(self, case_area_val):
        self.area_case = case_area_val


    # case width * case height = case area
    # this must always be true
    # width of a case must always corresponds to the width of the scenario
    # case area is determined by ?? -> impact of evidence on the case. but this is also determined
    # so we can easily find case height always
    def get_case_height(self):
        return self.area_case/self.width

    def get_case_prop_areas_dict(self):
        return self.dict_area_value
