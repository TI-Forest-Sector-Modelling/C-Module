from c_module.data_management.data_manager import DataManager
from c_module.parameters.paths import (FAOSTAT_DATA, FRA_DATA)
from c_module.parameters.defines import (VarNames, ParamNames)
from pathlib import Path
from c_module.logic.visualisation import Carbon_DashboardPlotter


class ProcessManager:
    @staticmethod
    def run_readin_process(self):
        ProcessManager.readin_add_data_process(self)
        ProcessManager.readin_timba_process(self)
        ProcessManager.readin_carbon_process(self)
        ProcessManager.readin_faostat_process(self)
        ProcessManager.readin_fra_process(self)

    @staticmethod
    def readin_add_data_process(self):
        self.logger.info("C-Module - Reading in additional data")
        DataManager.load_additional_data(self)


    @staticmethod
    def readin_timba_process(self):
        self.logger.info("C-Module - Reading in input data")
        DataManager.load_timba_data(self)
        DataManager.retrieve_commodity_num(self)

    @staticmethod
    def readin_carbon_process(self):
        self.logger.info("C-Module - Reading in carbon data")
        DataManager.load_additional_data_carbon(self)
        DataManager.retrieve_commodity_data(self)
        DataManager.align_carbon_data(self)
        DataManager.set_up_carbon_data_dict(self)

    @staticmethod
    def readin_faostat_process(self):
        self.logger.info("C-Module - Reading in FAOSTAT data")
        DataManager.load_faostat_data(self)
        if not Path(f"{FAOSTAT_DATA}.pkl").is_file():
            DataManager.prep_faostat_data(self)
            DataManager.aggregate_faostat_data(self)
            DataManager.serialize_to_pickle(self.faostat_data["data_aligned"], f"{FAOSTAT_DATA}.pkl")

    @staticmethod
    def readin_fra_process(self):
        self.logger.info("C-Module - Reading in FRA data")
        # TODO implement fra processing steps
        DataManager.load_fra_data(self)
        if not Path(f"{FRA_DATA}.pkl").is_file():
            DataManager.prep_fra_data(self)
            DataManager.serialize_to_pickle(self.fra_data["data_aligned"], f"{FRA_DATA}.pkl")

    @staticmethod
    def save_carbon_data(self):
        self.logger.info("C-Module - Saving carbon stock and flux data")
        DataManager.save_data(self)
        DataManager.merge_sc_data(self)

    @staticmethod
    def call_carbon_dashboard(self):
        self.logger.info("C-Module - Generating carbon dashboard")
        timba_data = self.timba_data[VarNames.all_scenarios.value].copy()
        timba_data = timba_data[timba_data[VarNames.year_name.value] % 5 == 0].reset_index(drop=True)
        Carbon_DashboardPlotter(data=timba_data).run()

    @staticmethod
    def start_header(self):
        if not self.add_on_activated:
            print("            ---------------------------------")
            print("                  Starting the C-Module      ")
            print("            ---------------------------------")
            print(f"               Time: {self.time_stamp}")
            print(f"")
            print(f"            Module settings:")

            print(f"            Used as standalone module: {self.UserInput[ParamNames.add_on_activated.value]}")
            print(f"            Start year: {self.UserInput[ParamNames.start_year.value]}")
            print(f"            End year: {self.UserInput[ParamNames.end_year.value]}")
            print(f"            ---------------------------------")
            print(f"")
            print(f"            Forest carbon related parameters: ")
            print(f"            Quantify forest aboveground carbon:"
                  f" {self.UserInput[ParamNames.calc_c_forest_agb.value]}")
            print(f"            Quantify forest belowground carbon:"
                  f" {self.UserInput[ParamNames.calc_c_forest_bgb.value]}")
            print(f"            Quantify forest soil carbon: {self.UserInput[ParamNames.calc_c_forest_soil.value]}")
            print(f"            Quantify forest dwl carbon: {self.UserInput[ParamNames.calc_c_forest_dwl.value]}")
            print(f"            ---------------------------------")
            print(f"")
            print(f"            HWP carbon related parameters:")
            print(f"            Quantify HWP carbon: {self.UserInput[ParamNames.calc_c_hwp.value]}")
            print(f"            Accounting approach: {self.UserInput[ParamNames.c_hwp_accounting_approach.value]}")
            print(f"            Accounting approach for historical HWP pool: "
                  f"{self.UserInput[ParamNames.historical_c_hwp.value]}")
            print(f"            ---------------------------------")
