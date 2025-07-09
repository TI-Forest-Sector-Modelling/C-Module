from C_Module.data_management.data_manager import DataManager
from C_Module.parameters.paths import (FAOSTAT_DATA, FRA_DATA, PKL_CARBON_OUTPUT, PKL_UPDATED_TIMBA_OUTPUT,
                                       OUTPUT_FOLDER)
from C_Module.parameters.defines import VarNames
from pathlib import Path


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
        self.logger.info("Reading in additional data")
        DataManager.load_additional_data(self)


    @staticmethod
    def readin_timba_process(self):
        self.logger.info("Reading in input data")
        DataManager.load_timba_data(self)
        DataManager.retrieve_commodity_num(self)

    @staticmethod
    def readin_carbon_process(self):
        self.logger.info("Reading in carbon data")
        DataManager.load_additional_data_carbon(self)
        DataManager.retrieve_commodity_data(self)
        DataManager.align_carbon_data(self)
        DataManager.set_up_carbon_data_dict(self)

    @staticmethod
    def readin_faostat_process(self):
        self.logger.info("Reading in FAOSTAT data")
        DataManager.load_faostat_data(self)
        if not Path(f"{FAOSTAT_DATA}.pkl").is_file():
            DataManager.prep_faostat_data(self)
            DataManager.serialize_to_pickle(self.faostat_data["data_aligned"], f"{FAOSTAT_DATA}.pkl")

    @staticmethod
    def readin_fra_process(self):
        self.logger.info("Reading in FRA data")
        # TODO implement fra processing steps
        DataManager.load_fra_data(self)
        if not Path(f"{FRA_DATA}.pkl").is_file():
            DataManager.prep_fra_data(self)
            DataManager.serialize_to_pickle(self.fra_data["data_aligned"], f"{FRA_DATA}.pkl")

    @staticmethod
    def save_carbon_data(self):
        self.logger.info("Saving carbon stock and flux data")

        if self.UserInput["save_data_as"] == "all":
            self.timba_data[VarNames.timba_data_carbon.value] = self.carbon_data[VarNames.carbon_total.value]
            DataManager.serialize_to_pickle(self.timba_data, f"{PKL_UPDATED_TIMBA_OUTPUT}{self.time_stamp}.pkl")
            DataManager.serialize_to_pickle(self.carbon_data, f"{PKL_CARBON_OUTPUT}{self.time_stamp}.pkl")

            for df_key in self.carbon_data.keys():
                carbon_data = self.carbon_data[df_key]
                carbon_data_path = OUTPUT_FOLDER / Path(f"{df_key}_D{self.time_stamp}")
                carbon_data.to_csv(f"{carbon_data_path}.csv", index=False)

        elif self.UserInput["save_data_as"] == "pkl":
            self.timba_data[VarNames.timba_data_carbon.value] = self.carbon_data[VarNames.carbon_total.value]
            DataManager.serialize_to_pickle(self.timba_data, f"{PKL_UPDATED_TIMBA_OUTPUT}{self.time_stamp}.pkl")
            DataManager.serialize_to_pickle(self.carbon_data, f"{PKL_CARBON_OUTPUT}{self.time_stamp}.pkl")

        elif self.UserInput["save_data_as"] == "csv":
            for df_key in self.carbon_data.keys():
                carbon_data = self.carbon_data[df_key]
                carbon_data_path = OUTPUT_FOLDER / Path(f"{df_key}_D{self.time_stamp}")
                carbon_data.to_csv(f"{carbon_data_path}.csv", index=False)

        else:
            self.logger.error(f"Unvalide user input {self.UserInput['save_data_as']}")

    @staticmethod
    def start_header(self):
        print("            ---------------------------------")
        print("                  Starting the C-Module      ")
        print("            ---------------------------------")
        print(f"               Time: {self.time_stamp}")
        print(f"")
        print(f"            Module settings:")
        print(f"            Carbon ex-post calculation: {self.UserInput["calc_c_ex_post"]}")
        print(f"            Carbon ex-ante calculation: {self.UserInput["calc_c_ex_ante"]}")
        print(f"            Start year: {self.UserInput['start_year']}")
        print(f"            End year: {self.UserInput['end_year']}")
        print(f"            ---------------------------------")
        print(f"")
        print(f"            Forest carbon related parameters: ")
        print(f"            Quantify forest aboveground carbon: {self.UserInput['calc_c_forest_agb']}")
        print(f"            Quantify forest belowground carbon: {self.UserInput['calc_c_forest_bgb']}")
        print(f"            Quantify forest soil carbon: {self.UserInput['calc_c_forest_soil']}")
        print(f"            Quantify forest dwl carbon: {self.UserInput['calc_c_forest_dwl']}")
        print(f"            ---------------------------------")
        print(f"")
        print(f"            HWP carbon related parameters:")
        print(f"            Quantify HWP carbon: {self.UserInput['calc_c_hwp']}")
        print(f"            Accounting approach: {self.UserInput['c_hwp_accounting_approach']}")
        print(f"            Accounting approach for historical HWP pool: {self.UserInput['historical_c_hwp']}")
        print(f"            ---------------------------------")
