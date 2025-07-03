import datetime as dt
from C_Module.data_management.process_manager import ProcessManager
from C_Module.logic.base_logger import get_logger


class C_Module(object):
    def __init__(self, UserInput):
        self.UserInput = UserInput
        self.time_stamp = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")
        self.logger = get_logger(None)
        self.timba_data = None
        self.add_data = {}
        self.carbon_data = {}
        self.add_carbon_data = {}
        self.faostat_data = {}
        self.fra_data = {}

    def calc_carbon_forest_biomass(self):
        pass

    def calc_carbon_forest_soil(self):
        pass

    def calc_carbon_forest_dwl(self):
        pass

    def calc_carbon_hwp(self):
        pass

    def calc_substitution_effect(self):
        pass

    def run(self):
        ProcessManager.start_header(self)
        ProcessManager.run_readin_process(self)

