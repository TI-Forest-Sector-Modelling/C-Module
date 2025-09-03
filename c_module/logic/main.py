import datetime as dt
from c_module.data_management.process_manager import ProcessManager
from c_module.logic.carbon_calc import CarbonCalculator
from c_module.logic.base_logger import get_logger
from c_module.parameters.defines import ParamNames


class C_Module(object):
    def __init__(self, UserInput):
        self.UserInput = UserInput
        self.add_on_activated = UserInput[ParamNames.add_on_activated.value]
        self.time_stamp = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")
        self.logger = get_logger(None, add_on_activated=self.add_on_activated)
        self.sc_list = []
        self.timba_data = {}
        self.add_data = {}
        self.carbon_data = {}
        self.add_carbon_data = {}
        self.faostat_data = {}
        self.fra_data = {}

    def run(self):
        ProcessManager.start_header(self)
        ProcessManager.run_readin_process(self)
        CarbonCalculator.run_carbon_calc(self)
        ProcessManager.save_carbon_data(self)
        if self.UserInput[ParamNames.show_carbon_dashboard.value]:
            ProcessManager.call_carbon_dashboard(self)


