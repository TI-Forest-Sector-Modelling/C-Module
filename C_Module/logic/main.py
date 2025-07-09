import datetime as dt
from C_Module.data_management.process_manager import ProcessManager
from C_Module.logic.carbon_calc import CarbonCalculator
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

    def run(self):
        ProcessManager.start_header(self)
        ProcessManager.run_readin_process(self)
        CarbonCalculator.run_carbon_calc(self)
        ProcessManager.save_carbon_data(self)


