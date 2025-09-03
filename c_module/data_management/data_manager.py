from c_module.parameters.paths import (PKL_RESULTS_INPUT, ADD_INFO_CARBON_PATH, ADD_INFO_COUNTRY, FAOSTAT_DATA,
                                       FRA_DATA, OUTPUT_FOLDER)
from c_module.parameters.defines import (VarNames, ParamNames, CountryConstants)

import pandas as pd
from tqdm import tqdm
from pathlib import Path


class DataManager:

    @staticmethod
    def load_data(filepath, table_name, input_source):
        if input_source.lower() == "excel":
            return DataManager.read_excel(filepath, table_name)
        elif input_source.lower() == "csv":
            return DataManager.read_csv(filepath)
        else:
            raise TypeError(f"Input source type {input_source} is not defined.")

    @staticmethod
    def read_excel(input_filepath, table_name):
        xlsx_connection = pd.ExcelFile(input_filepath)
        return xlsx_connection.parse(table_name)

    @staticmethod
    def read_csv(input_filepath):
        try:
            data = pd.read_csv(input_filepath, delimiter=';')
        except UnicodeDecodeError:
            data = pd.read_csv(input_filepath, encoding="ISO-8859-1")
        return data

    @staticmethod
    def serialize_to_pickle(obj, target_filepath: str):
        """
        Write ("wb") object as pickle file to target path.
        :param obj: Object to save
        :param target_filepath: file path to save the object
        """
        import pickle
        import gzip
        with gzip.open(target_filepath, "wb") as pkl_file:
            pickle.dump(obj, pkl_file)

    @staticmethod
    def restore_from_pickle(src_filepath: str):
        """
        Read ("rb") object from pickle file in source path.
        :param src_filepath: source path to read the object from pkl
        """
        import pickle
        import gzip
        with gzip.open(src_filepath, "rb") as pkl_file:
            obj = pickle.load(pkl_file)
        return obj

    @staticmethod
    def load_timba_data(self):
        if self.UserInput[ParamNames.read_in_pkl.value]:
            timba_data = {}
            sc_list = []
            for pkl_file in PKL_RESULTS_INPUT:
                timba_data_tmp = DataManager.restore_from_pickle(pkl_file)
                sc_name = pkl_file.stem
                sc_list.append(sc_name)
                timba_data[sc_name] = timba_data_tmp

            self.timba_data = timba_data
            self.sc_list = sc_list

        else:
            # TODO implement possibility to read in xlsx data
            pass

    @staticmethod
    def save_data(self):
        for sc in self.sc_list:
            carbon_data_ext = DataManager.flattening_data(data=self.carbon_data[sc])
            carbon_data_ext = DataManager.add_additional_info(self, data=carbon_data_ext, sc=sc)
            self.timba_data[sc][VarNames.timba_data_carbon.value] = self.carbon_data[sc][VarNames.carbon_total.value]
            self.timba_data[sc][VarNames.timba_data_carbon_flat.value] = carbon_data_ext
            if not self.UserInput[ParamNames.add_on_activated.value]:
                DataManager.serialize_to_pickle(self.timba_data[sc], OUTPUT_FOLDER / Path(f"{sc}.pkl"))
            else:
                DataManager.serialize_to_pickle(
                    self.carbon_data[sc], OUTPUT_FOLDER / Path(f"{self.time_stamp}_{sc}.pkl"))

            for df_key in self.carbon_data[sc].keys():
                carbon_data = self.carbon_data[sc][df_key]
                carbon_data_path = OUTPUT_FOLDER / Path(f"{df_key}_D{self.time_stamp}_{sc}")
                carbon_data.to_csv(f"{carbon_data_path}.csv", index=False)

    @staticmethod
    def merge_sc_data(self):
        carbon_data_all_sc = pd.DataFrame()
        for sc in self.sc_list:
            carbon_data_sc = self.timba_data[sc][VarNames.timba_data_carbon_flat.value].copy()
            carbon_data_sc[VarNames.scenario.value] = sc
            carbon_data_all_sc = pd.concat([carbon_data_all_sc, carbon_data_sc], axis=0).reset_index(drop=True)

        self.timba_data[VarNames.all_scenarios.value] = carbon_data_all_sc

    @staticmethod
    def load_additional_data(self):
        self.add_data["country_data"] = DataManager.load_data(
            f"{ADD_INFO_COUNTRY}.csv", ADD_INFO_COUNTRY, "csv")

    @staticmethod
    def retrieve_commodity_num(self):

        timba_data_all = VarNames.timba_data_all.value
        commodity_dict = VarNames.commodity_dict.value
        commodity_code = VarNames.commodity_code.value
        commodity_num_name = VarNames.commodity_num.value

        commodity_num = len(self.timba_data[self.sc_list[0]][timba_data_all][commodity_code].unique())
        self.add_data[commodity_dict] = {}
        self.add_data[commodity_dict][commodity_num_name] = commodity_num

    @staticmethod
    def retrieve_commodity_data(self):
        carbon_hwp_name = VarNames.carbon_hwp.value
        commodity_dict_name = VarNames.commodity_dict.value
        commodity_data_name = VarNames.commodity_data.value
        commodity_name = VarNames.commodity_name.value
        commodity_code = VarNames.commodity_code.value
        fao_item_code = VarNames.faostat_item_code.value

        commodity_data = self.add_carbon_data[carbon_hwp_name][[commodity_name, commodity_code, fao_item_code]].copy()
        self.add_data[commodity_dict_name][commodity_data_name] = commodity_data

    @staticmethod
    def load_additional_data_carbon(self):
        """
        Additional information for projections of carbon removals and emissions are readin
        :param self: object of class C-Module
        """
        commodity_code = VarNames.commodity_code.value
        for sheet_name in pd.ExcelFile(f"{ADD_INFO_CARBON_PATH}.xlsx").sheet_names:
            if "CarbonHWP_" in sheet_name:
                commodity_data_timba = pd.DataFrame(self.timba_data[self.sc_list[0]][VarNames.timba_data_all.value]
                                                    [f"{VarNames.commodity_code.value}"].unique())
                commodity_data_add_info = DataManager.load_data(f"{ADD_INFO_CARBON_PATH}.xlsx", sheet_name, "Excel")
                new_sheet_name = sheet_name.split('_')[0]

                if commodity_data_timba[0].astype('int64').equals(
                        commodity_data_add_info[commodity_code]):
                    self.add_carbon_data[new_sheet_name] = commodity_data_add_info

            else:
                self.add_carbon_data[sheet_name] = DataManager.load_data(f"{ADD_INFO_CARBON_PATH}.xlsx", sheet_name,
                                                                              "Excel")

    @staticmethod
    def load_faostat_data(self):
        """
        Loads the Forestry data with no flags from the bulk data provided by FAOSTAT
        (Forestry_E_All_Data/Forestry_E_All_Data_NOFLAG.csv). See README.md for details.
        :param self: object of class C-Module
        """
        if Path(f"{FAOSTAT_DATA}.pkl").is_file():
            self.faostat_data["data_aligned"] = DataManager.restore_from_pickle(f"{FAOSTAT_DATA}.pkl")
        else:
            self.faostat_data["data"] = DataManager.load_data(f"{FAOSTAT_DATA}.csv", FAOSTAT_DATA, "csv")

    @staticmethod
    def prep_faostat_data(self):
        """
        Processes bulk data from FAOStat for the products included in the input data for the calculation of historical
        HWP carbon stocks. Saves aligned FAO data in the carbon data container.
        :param self: object of class C-Module
        """
        commodity_dict_name = VarNames.commodity_dict.value
        commodity_data_name = VarNames.commodity_data.value
        item_code_name = VarNames.faostat_item_code.value
        item_name = VarNames.faostat_item_name.value
        element_name = VarNames.faostat_element_name.value
        fao_country_code = VarNames.fao_country_code.value
        iso3_code = VarNames.ISO3.value
        year_name = VarNames.year_name.value
        data_aligned_name = VarNames.data_aligned.value

        fao_data_info = self.add_data["country_data"].copy()
        commodity_data = self.add_data[commodity_dict_name][commodity_data_name].copy()

        fao_df = self.faostat_data["data"].copy()
        fao_data_new = pd.DataFrame()
        for item in tqdm(fao_df[item_code_name].unique(), desc=f"Processing FAOSTAT data"):
            # Add item code of products to aggregate
            if item in list(commodity_data[item_code_name]) + [1634, 1646, 1606]:

                fao_data_element = pd.DataFrame()
                for element in fao_df[element_name].unique():
                    fao_data_tmp = fao_df[(fao_df[item_code_name] == item) &
                                          (fao_df[element_name] == element) &
                                          (fao_df[fao_country_code] < CountryConstants.FAO_REGION_CODE.value)
                                          ].reset_index(drop=True).copy()
                    fao_data_year = pd.DataFrame()
                    for year_col in fao_data_tmp.columns[["Y" in x for x in fao_data_tmp.columns]]:
                        year_int = pd.DataFrame(
                            [int(year_col.split('Y')[1])] * len(fao_data_info)).rename(columns={0: year_name})
                        if len(fao_data_tmp) > 0:
                            item_tmp = pd.DataFrame([fao_data_tmp[[
                                item_name,
                                item_code_name]].iloc[0]] * len(fao_data_info)).reset_index(drop=True)
                        else:
                            fao_data_except = fao_df[
                                (fao_df[item_name] == item) &
                                (fao_df[fao_country_code] < CountryConstants.FAO_REGION_CODE.value)
                                ].reset_index(drop=True)
                            item_tmp = pd.DataFrame([fao_data_except[[
                                item_name,
                                item_code_name]].iloc[0]] * len(fao_data_info)).reset_index(drop=True)

                        fao_data_info_tmp = pd.concat([fao_data_info, item_tmp, year_int], axis=1)

                        fao_data_tmp_year = fao_data_info_tmp.merge(
                            fao_data_tmp[[fao_country_code, year_col]],
                            left_on=fao_country_code, right_on=fao_country_code, how="left")
                        fao_data_tmp_year = fao_data_tmp_year[[fao_country_code, iso3_code, item_name, item_code_name,
                                                               year_name, year_col]]
                        fao_data_tmp_year = fao_data_tmp_year.rename(columns={year_col: element})
                        # fao_data_tmp_year[element] = fao_data_tmp_year[element].fillna(0)
                        fao_data_year = pd.concat([fao_data_year, fao_data_tmp_year], axis=0).reset_index(drop=True)

                    if len(fao_data_element) == 0:
                        fao_data_element = pd.concat([fao_data_element, fao_data_year], axis=0).reset_index(drop=True)
                    else:
                        fao_data_element = pd.concat([fao_data_element, pd.DataFrame(fao_data_year[element])],
                                                     axis=1).reset_index(drop=True)

                fao_data_new = pd.concat([fao_data_new, fao_data_element], axis=0).reset_index(drop=True)
        self.faostat_data[data_aligned_name] = fao_data_new

    @staticmethod
    def aggregate_faostat_data(self):
        self.logger.info(f"Aggregating FAOSTAT item data")
        fao_country_code = VarNames.fao_country_code.value
        iso3_code = VarNames.ISO3.value
        year_name = VarNames.year_name.value
        production_name = VarNames.faostat_production.value
        import_name = VarNames.faostat_import.value
        export_name = VarNames.faostat_export.value
        import_value_name = VarNames.faostat_import_value.value
        export_value_name = VarNames.faostat_export_value.value
        data_aligned_name = VarNames.data_aligned.value

        plywood_item_code = 1640
        veneer_item_code = 1634
        particleb_item_code_post_1995 = 1697
        particleb_item_code_ante_1995 = 1646
        osb_item_code = 1606

        faostat_data = self.faostat_data[data_aligned_name].copy()
        faostat_data_col = [fao_country_code, iso3_code, year_name]
        col_to_aggregate = [production_name, import_name, import_value_name, export_name, export_value_name]

        # Post-processing data aggregation

        # Merge plywood and veneer data
        self.logger.info(f"Aggregating FAOSTAT data for plywood and veneer sheets")
        faostat_data = DataManager.faostat_data_aggregator(
            faostat_data=faostat_data,
            items_to_aggregate=[plywood_item_code, veneer_item_code],
            faostat_data_col=faostat_data_col,
            col_to_aggregate=col_to_aggregate,
            aggregated_item_name="Plywood and LVL",  # TODO move to defines
            aggregated_item_code=plywood_item_code
        )

        # Merge Particle board and OSB (1961-1995) and Particle board and Oriented Strand Board (OSB)
        self.logger.info(f"Aggregating FAOSTAT data for particle board before and after 1995, and OSB")
        faostat_data = DataManager.faostat_data_aggregator(
            faostat_data=faostat_data,
            items_to_aggregate=[particleb_item_code_post_1995, particleb_item_code_ante_1995, osb_item_code],
            faostat_data_col=faostat_data_col,
            col_to_aggregate=col_to_aggregate,
            aggregated_item_name="Particle board",  # TODO move to defines
            aggregated_item_code=particleb_item_code_post_1995
        )

        # Add new merging calls if needed

        self.faostat_data[data_aligned_name] = faostat_data

    @staticmethod
    def faostat_data_aggregator(faostat_data, items_to_aggregate, faostat_data_col, col_to_aggregate,
                                aggregated_item_name, aggregated_item_code):
        country_code_name = VarNames.fao_country_code.value
        item_code_name = VarNames.faostat_item_code.value
        item_name = VarNames.faostat_item_name.value
        faostat_data_merged = faostat_data[
            [temp_item in items_to_aggregate for temp_item in faostat_data[item_code_name]]
        ].copy().reset_index(drop=True)
        faostat_data_merged = faostat_data_merged.groupby(faostat_data_col)[col_to_aggregate].sum().reset_index()
        faostat_data_merged[item_name] = aggregated_item_name
        faostat_data_merged[item_code_name] = aggregated_item_code

        faostat_data = faostat_data[
            [temp_item not in items_to_aggregate for temp_item in faostat_data[item_code_name]]
        ].copy().reset_index(drop=True)
        faostat_data = pd.concat([faostat_data, faostat_data_merged], axis=0).reset_index(drop=True)
        faostat_data = faostat_data.sort_values(by=[country_code_name, item_code_name], ascending=[True, True]
                                                ).reset_index(drop=True)

        return faostat_data

    @staticmethod
    def load_fra_data(self):
        if Path(f"{FRA_DATA}.pkl").is_file():
            self.fra_data["data_aligned"] = DataManager.restore_from_pickle(f"{FRA_DATA}.pkl")
        else:
            self.fra_data["data"] = DataManager.load_data(f"{FRA_DATA}.csv", FRA_DATA, "csv")

    @staticmethod
    def prep_fra_data(self):
        self.fra_data["data_aligned"] = pd.DataFrame()

    @staticmethod
    def align_carbon_data(self):
        """
        Data related to the quantification of carbon removals and emissions from forest biomass, forest soil, dead wood,
        litter and HWP are aligned to the standard length (len(regions) * len(commodities)). Aligned data are saved as a
        new attribute "data_aligned" in AdditionalInfo.CarbonForestBiomass and AdditionalInfo.CarbonHWP.
        :param self: object of class C-Module
        """
        timba_country_name = VarNames.timba_country_name.value
        timba_country_code = VarNames.timba_country_code.value
        iso3 = VarNames.ISO3.value
        carbon_region = VarNames.carbon_region.value
        dummy_region = VarNames.dummy_region.value

        carbon_forest_biomass_name = VarNames.carbon_forest_biomass.value
        carbon_hwp_name = VarNames.carbon_hwp.value
        carbon_agb_name = VarNames.carbon_agb.value
        carbon_bgb_name = VarNames.carbon_bgb.value
        carbon_dw_name = VarNames.carbon_dw.value
        carbon_soil_name = VarNames.carbon_soil.value
        carbon_litter_name = VarNames.carbon_litter.value

        country_data = VarNames.country_data.value
        commodity_dict_name = VarNames.commodity_dict.value
        commodity_num = VarNames.commodity_num.value

        country_data = self.add_data[country_data][[timba_country_name, timba_country_code, iso3, carbon_region]].copy()
        carbon_forest_biomass = country_data.merge(self.add_carbon_data[carbon_forest_biomass_name],
                                                   left_on=[carbon_region],
                                                   right_on=[carbon_region], how="left")
        commodity_num = self.add_data[commodity_dict_name][commodity_num]
        country_num = len(country_data)

        carbon_forest_biomass = pd.concat([carbon_forest_biomass] * commodity_num).sort_values(
            by=[timba_country_code]).reset_index(drop=True)
        carbon_forest_biomass = carbon_forest_biomass[
            carbon_forest_biomass[timba_country_code] != dummy_region]
        self.add_carbon_data[carbon_forest_biomass_name] = carbon_forest_biomass

        carbon_hwp = pd.concat([self.add_carbon_data[carbon_hwp_name]] * country_num).reset_index(
            drop=True)
        self.add_carbon_data[carbon_hwp_name] = carbon_hwp

        carbon_above_ground = pd.concat([self.add_carbon_data[carbon_agb_name]] * commodity_num).sort_values(
            by=[timba_country_code]).reset_index(drop=True)
        self.add_carbon_data[carbon_agb_name] = carbon_above_ground

        carbon_below_ground = pd.concat([self.add_carbon_data[carbon_bgb_name]] * commodity_num).sort_values(
            by=[timba_country_code]).reset_index(drop=True)
        self.add_carbon_data[carbon_bgb_name] = carbon_below_ground

        carbon_dead_wood = pd.concat([self.add_carbon_data[carbon_dw_name]] * commodity_num).sort_values(
            by=[timba_country_code]).reset_index(drop=True)
        self.add_carbon_data[carbon_dw_name] = carbon_dead_wood

        carbon_litter = pd.concat(
            [self.add_carbon_data[carbon_litter_name]] * commodity_num).sort_values(
            by=[timba_country_code]).reset_index(drop=True)
        self.add_carbon_data[carbon_litter_name] = carbon_litter

        carbon_soil = pd.concat([self.add_carbon_data[carbon_soil_name]] * commodity_num).sort_values(
            by=[timba_country_code]).reset_index(drop=True)
        self.add_carbon_data[carbon_soil_name] = carbon_soil

    @staticmethod
    def set_up_carbon_data_dict(self):
        carbon_forest_biomass_name = VarNames.carbon_forest_biomass.value
        carbon_dwl_name = VarNames.carbon_dwl.value
        carbon_soil_name = VarNames.carbon_soil.value
        carbon_hwp_name = VarNames.carbon_hwp.value
        carbon_substitution_name = VarNames.carbon_substitution.value
        carbon_total_name = VarNames.carbon_total.value

        for sc in self.sc_list:
            self.carbon_data[sc] = {}
            if self.UserInput[ParamNames.calc_c_forest_agb.value] or self.UserInput[ParamNames.calc_c_forest_bgb.value]:
                self.carbon_data[sc][carbon_forest_biomass_name] = pd.DataFrame(
                    [0], columns=[carbon_forest_biomass_name])
            if self.UserInput[ParamNames.calc_c_forest_dwl.value]:
                self.carbon_data[sc][carbon_dwl_name] = pd.DataFrame([0], columns=[carbon_dwl_name])
            if self.UserInput[ParamNames.calc_c_forest_soil.value]:
                self.carbon_data[sc][carbon_soil_name] = pd.DataFrame([0], columns=[carbon_soil_name])
            if self.UserInput[ParamNames.calc_c_hwp.value]:
                self.carbon_data[sc][carbon_hwp_name] = pd.DataFrame([0], columns=[carbon_hwp_name])
            self.carbon_data[sc][carbon_substitution_name] = pd.DataFrame([0], columns=[carbon_substitution_name])
            self.carbon_data[sc][carbon_total_name] = pd.DataFrame([0], columns=[carbon_total_name])

    @staticmethod
    def flattening_data(data):
        """
        Flattens dictionary data into 2D dataframe.
        :param data: dictionary data
        :return: flattened dataframe
        """
        flat_data = pd.DataFrame()
        change_var_list = [VarNames.carbon_forest_biomass_chg.value, VarNames.carbon_dwl_chg.value,
                           VarNames.carbon_soil_chg.value, VarNames.carbon_hwp_chg.value,
                           VarNames.total_substitution_chg.value, VarNames.carbon_total_chg.value]
        for key, key_change in zip(data.keys(), change_var_list):
            data_tmp = data[key].copy()
            if key == VarNames.carbon_hwp.value:
                data_tmp[VarNames.output_variable.value] = "Carbon" + "_" + data_tmp[VarNames.hwp_category.value]
            else:
                data_tmp[VarNames.output_variable.value] = key

            if key == VarNames.carbon_substitution.value:
                key = VarNames.total_substitution.value
                data_tmp = data_tmp.groupby([VarNames.region_code.value, VarNames.ISO3.value,
                                             VarNames.period_var.value, VarNames.output_variable.value], as_index=False
                                            ).agg({key: "sum", key_change: "sum"})

            data_tmp = data_tmp.rename(columns={key: VarNames.carbon_stock.value,
                                                key_change: VarNames.carbon_stock_chg.value})

            data_tmp = data_tmp[[VarNames.region_code.value, VarNames.ISO3.value, VarNames.period_var.value,
                                 VarNames.output_variable.value, VarNames.carbon_stock.value,
                                 VarNames.carbon_stock_chg.value]]
            flat_data = pd.concat([flat_data, data_tmp], axis=0).reset_index(drop=True)

        data_hwp = flat_data[flat_data[VarNames.output_variable.value].str.contains("Carbon_", na=False)]
        data_hwp = data_hwp.groupby([VarNames.region_code.value,
                                     VarNames.ISO3.value, VarNames.period_var.value],
                                    as_index=False).agg({VarNames.carbon_stock.value: "sum",
                                                         VarNames.carbon_stock_chg.value: "sum"})
        data_hwp[VarNames.output_variable.value] = VarNames.carbon_hwp.value
        flat_data = pd.concat([flat_data, data_hwp], axis=0).reset_index(drop=True)
        flat_data = flat_data[flat_data[VarNames.ISO3.value] != "WRL"].reset_index(drop=True)
        return flat_data

    @staticmethod
    def add_additional_info(self, data, sc):
        """
        Adds additional information related to regional aggregation and projection years
        :param self: C-Module object
        :param data: Data to which the additional information will be added
        :param sc: Scenario name
        :return: Data enhanced by additional information
        """
        geo_data = self.add_data[VarNames.country_data.value]
        geo_data = geo_data[[VarNames.ISO3.value, VarNames.continent.value, VarNames.carbon_region.value]]
        year_data = self.timba_data[sc][VarNames.timba_data_all.value]
        year_data = year_data[[VarNames.period_var.value,
                               VarNames.year_name.value]].drop_duplicates().reset_index(drop=True)

        data = data.merge(geo_data, left_on=VarNames.ISO3.value, right_on=VarNames.ISO3.value, how='left')
        data = data.merge(year_data, left_on=VarNames.period_var.value, right_on=VarNames.period_var.value, how='left')

        return data

    @staticmethod
    def generate_tickvals(n_scenarios, n_years):
        tickvals = []
        for i in range(n_years):
            start_index = i * n_scenarios
            tickvals.append(start_index + (n_scenarios - 1) / 2)
        return tickvals


