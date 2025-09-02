from c_module.parameters.defines import (VarNames, ParamNames, CarbonConstants)
from c_module.parameters.paths import (PKL_ADD_INFO_START_YEAR)
from c_module.data_management.data_manager import DataManager

import pandas as pd
import numpy as np
from tqdm import tqdm
from pathlib import Path


class CarbonCalculator:
    @staticmethod
    def calc_carbon_forest_biomass(self):
        self.logger.info(
            f"C-Module - Calculating carbon stocks and fluxes for forest biomass (aboveground and belowground)")
        for sc in self.sc_list:
            self.carbon_data[sc][VarNames.carbon_forest_biomass.value] = CarbonCalculator.calc_carbon_forest(
                carbon_data=self.carbon_data[sc][VarNames.carbon_forest_biomass.value],
                add_carbon_data=self.add_carbon_data,
                add_data=self.add_data[VarNames.country_data.value],
                forest_data=self.timba_data[sc][VarNames.timba_data_forest.value],
                monte_carlo=[VarNames.carbon_agb.value, VarNames.carbon_bgb.value])

    @staticmethod
    def calc_carbon_forest_soil(self):
        self.logger.info(f"C-Module - Calculating carbon stocks and fluxes for forest soil")
        for sc in self.sc_list:
            self.carbon_data[sc][VarNames.carbon_soil.value] = CarbonCalculator.calc_carbon_forest(
                carbon_data=self.carbon_data[sc][VarNames.carbon_soil.value],
                add_carbon_data=self.add_carbon_data,
                add_data=self.add_data[VarNames.country_data.value],
                forest_data=self.timba_data[sc][VarNames.timba_data_forest.value],
                monte_carlo=[VarNames.carbon_agb.value, VarNames.carbon_bgb.value])

    @staticmethod
    def calc_carbon_forest_dwl(self):
        self.logger.info(f"C-Module - Calculating carbon stocks and fluxes for dead wood and litter")
        for sc in self.sc_list:
            self.carbon_data[sc][VarNames.carbon_dwl.value] = CarbonCalculator.calc_carbon_forest(
                carbon_data=self.carbon_data[sc][VarNames.carbon_dwl.value],
                add_carbon_data=self.add_carbon_data,
                add_data=self.add_data[VarNames.country_data.value],
                forest_data=self.timba_data[sc][VarNames.timba_data_forest.value],
                monte_carlo=[VarNames.carbon_agb.value, VarNames.carbon_bgb.value])

    @staticmethod
    def calc_carbon_forest(carbon_data, add_carbon_data, add_data, forest_data, monte_carlo):
        """
        Carbon stock calculation for forest biomass (aboveground and belowground), forest soil, and dead wood and litter.
        Calculations for carbon in forest biomass are based on forest stock and calculations for carbon in forest soil,
        dead wood, and litter are based on forest area.
        Depending on input for CarbonData (DataFrame from carbon data container) carbon is calculated for specific carbon
        pool. If specific carbon pool is in monte_carlo list then randomized carbon density is used otherwise FRA-based
        carbon density is used.
        New carbon stock is calculated as carbon stock from previous period + changes in carbon stock during actual period.
        Changes in carbon stocks depend on changes in forest stock or area. Calculations based on equations xxx.
        :param forest_data: Data from forest domain (forest area and stock)
        :param carbon_data: Data from selected carbon pool (CarbonAboveGround, CarbonBelowGround, CarbonSoil,
        CarbonLitter, CarbonDeadWood)
        :param add_data: Additional data with country and commodity information
        :param add_carbon_data: DataContainer with carbon data
        :param monte_carlo: List storing names of carbon pools quantified with randomized emission factor
        :return: Updated dataframe of selected carbon pool
        """
        c_dens_avg = VarNames.carbon_density_avg.value
        c_dens_avg_rnd = VarNames.carbon_density_avg_rand.value

        if VarNames.carbon_forest_biomass.value in carbon_data.columns:
            unit_conversion_param = CarbonConstants.CARBON_MIO_FACTOR.value
            forest_data_col = VarNames.forest_stock_var.value

            if VarNames.carbon_agb.value in monte_carlo:
                carbon_above_ground_col = c_dens_avg_rnd
            else:
                carbon_above_ground_col = c_dens_avg
            if VarNames.carbon_bgb.value in monte_carlo:
                carbon_below_ground_col = c_dens_avg_rnd
            else:
                carbon_below_ground_col = c_dens_avg

            emission_factor = ((add_carbon_data[VarNames.carbon_agb.value][carbon_above_ground_col] +
                                add_carbon_data[VarNames.carbon_bgb.value][carbon_below_ground_col]) *
                               CarbonConstants.CO2_FACTOR.value)
            col_name, col_name_change = VarNames.carbon_forest_biomass.value, VarNames.carbon_forest_biomass_chg.value
        else:
            unit_conversion_param = CarbonConstants.CARBON_TSD_FACTOR.value
            forest_data_col = VarNames.forest_area_var.value
            if VarNames.carbon_soil.value in carbon_data.columns:

                if VarNames.carbon_soil.value in monte_carlo:
                    carbon_soil_col = c_dens_avg_rnd
                else:
                    carbon_soil_col = c_dens_avg

                emission_factor = (add_carbon_data[VarNames.carbon_soil.value][carbon_soil_col] *
                                   CarbonConstants.CO2_FACTOR.value)

                col_name, col_name_change = VarNames.carbon_soil.value, VarNames.carbon_soil_chg.value
            else:

                if VarNames.carbon_litter.value in monte_carlo:
                    carbon_litter_col = c_dens_avg_rnd
                else:
                    carbon_litter_col = c_dens_avg
                if VarNames.carbon_dw.value in monte_carlo:
                    carbon_dead_wood_col = c_dens_avg_rnd
                else:
                    carbon_dead_wood_col = c_dens_avg

                emission_factor = ((add_carbon_data[VarNames.carbon_litter.value][carbon_litter_col] +
                                    add_carbon_data[VarNames.carbon_dw.value][carbon_dead_wood_col]) *
                                   CarbonConstants.CO2_FACTOR.value)
                col_name, col_name_change = VarNames.carbon_dwl.value, VarNames.carbon_dwl_chg.value

        carbon_data = pd.DataFrame()
        for period in forest_data[VarNames.period_var.value].unique():
            forest_data_period = forest_data[forest_data[VarNames.period_var.value] == period].copy().reset_index(drop=True)
            forest_data_period = forest_data_period.merge(add_data[[VarNames.region_code.value, VarNames.ISO3.value]],
                                                          left_on=VarNames.region_code.value,
                                                          right_on=VarNames.region_code.value,
                                                          how="left")
            if period == 0:
                forest_variable_prev = pd.DataFrame(np.zeros(len(forest_data_period)))[0]
                carbonstock_prev = pd.DataFrame(np.zeros(len(forest_data_period)))[0]
            else:
                forest_variable_prev = (
                    forest_data[forest_data[VarNames.period_var.value] == period - 1][forest_data_col]).copy().reset_index(drop=True)
                carbonstock_prev = (
                    carbon_data[carbon_data[VarNames.period_var.value] == period - 1][col_name]).copy().reset_index(drop=True)

            forest_variable_new = forest_data_period[forest_data_col].copy().reset_index(drop=True)
            carbonstock_change = (
                    emission_factor * (forest_variable_new - forest_variable_prev) * unit_conversion_param)
            carbonstock_new = carbonstock_change + carbonstock_prev

            if period == 0:
                carbonstock_change = pd.DataFrame(
                    np.zeros(len(carbonstock_change))).rename(columns={0: col_name_change})
            else:
                pass

            carbonstock_forest = pd.concat([
                forest_data_period[[VarNames.region_code.value, VarNames.ISO3.value, VarNames.period_var.value,
                                    forest_data_col]],
                pd.DataFrame(data=carbonstock_new, columns=[col_name]),
                pd.DataFrame(data=carbonstock_change, columns=[col_name_change])
            ], axis=1)
            carbon_data = pd.concat([carbon_data, carbonstock_forest.copy()], axis=0).reset_index(drop=True)

        carbon_data = carbon_data.drop_duplicates().reset_index(drop=True)
        carbon_data[col_name] = carbon_data[col_name] / CarbonConstants.CARBON_MIO_FACTOR.value
        carbon_data[col_name_change] = carbon_data[col_name_change] / CarbonConstants.CARBON_MIO_FACTOR.value
        return carbon_data

    @staticmethod
    def calc_carbon_hwp(self):
        self.logger.info(f"C-Module - Calculating carbon stocks and fluxes for harvested wood products")
        add_carbon_data = self.add_carbon_data[VarNames.carbon_hwp.value]
        add_data = self.add_data
        faostat_data = self.faostat_data[VarNames.data_aligned.value]
        period_var = VarNames.period_var.value
        for sc in self.sc_list:
            timba_data = self.timba_data[sc][VarNames.timba_data_all.value]
            for period in timba_data[period_var].unique():
                if period == 0:
                    carbon_data = CarbonCalculator.calc_historic_carbon_hwp(
                        timba_data=timba_data,
                        faostat_data=faostat_data,
                        add_carbon_data=add_carbon_data,
                        add_data=add_data,
                        user_input=self.UserInput
                    )
                else:
                    carbon_data = CarbonCalculator.calc_projection_carbon_hwp(
                        timba_data=timba_data,
                        carbon_data=carbon_data,
                        add_carbon_data=add_carbon_data,
                        add_data=add_data,
                        user_input=self.UserInput,
                        period=period
                    )
            carbon_data[VarNames.carbon_hwp.value] = (carbon_data[VarNames.carbon_hwp.value] /
                                                      CarbonConstants.CARBON_MIO_FACTOR.value)
            carbon_data[VarNames.carbon_hwp_chg.value] = (carbon_data[VarNames.carbon_hwp_chg.value] /
                                                          CarbonConstants.CARBON_MIO_FACTOR.value)

            hwp_category = self.add_carbon_data[VarNames.carbon_hwp.value][[VarNames.commodity_code.value,
                                                                            VarNames.hwp_category.value]].drop_duplicates()

            carbon_data = carbon_data.merge(hwp_category, left_on=VarNames.commodity_code.value,
                                            right_on=VarNames.commodity_code.value, how="left")
            carbon_data = carbon_data.dropna(axis=0).reset_index(drop=True)
            carbon_data = carbon_data.groupby(
                [VarNames.region_code.value, VarNames.hwp_category.value, VarNames.ISO3.value,
                 VarNames.period_var.value, VarNames.year_name.value]
            )[[VarNames.carbon_hwp.value, VarNames.carbon_hwp_chg.value]].sum().reset_index()

            self.carbon_data[sc][VarNames.carbon_hwp.value] = carbon_data

    @staticmethod
    def calc_historic_carbon_hwp(timba_data: pd.DataFrame, faostat_data: pd.DataFrame, add_data: pd.DataFrame,
                                 add_carbon_data: pd.DataFrame, user_input: dict):
        """
        Calculates the historical carbon stock in semi-finished HWP based on the production or stock-change approach as
        defined by the IPCC (2019). Historical statistics for the semi-finished HWP from the FAOSTAT are used for the
        calculations. The start year from which the historical carbon stock is calculated is either based on the data
        availability for each country and semi-finished HWP or a default value defined by the user.
        :param timba_data: TiMBA projections data for the production, import, export of semi-finished HWP
        :param faostat_data: FAOSTAT historical statistics
        :param add_data: Additional data related to the country and HWP structure in TiMBA
        :param add_carbon_data: Additional data for carbon calculations
        :param user_input: Input from user
        :return: Historical carbon stocks in semi-finished HWP for all countries represented in TiMBA
        """
        carbon_factor = VarNames.carbon_factor.value
        half_life = VarNames.half_life.value
        faostat_country_code = VarNames.fao_country_code.value
        faostat_item_code = VarNames.faostat_item_code.value
        faostat_production = VarNames.faostat_production.value
        faostat_import = VarNames.faostat_import.value
        faostat_export = VarNames.faostat_export.value
        faostat_domestic_consumption = VarNames.faostat_domestic_consumption.value
        faostat_production_domestic_feedstock = VarNames.faostat_production_domestic_feedstock.value
        iso3_code = VarNames.ISO3.value
        sh_domestic_feed = VarNames.share_domestic_feedstock.value
        start_year = VarNames.start_year.value
        hwp_category_var = VarNames.hwp_category.value
        production_approach = VarNames.production_approach.value
        stock_change_approach = VarNames.stock_change_approach.value

        timba_region_code = VarNames.region_code.value
        timba_commodity_code = VarNames.commodity_code.value
        country_data = VarNames.country_data.value
        commodity_data = VarNames.commodity_data.value
        commodity = VarNames.commodity_dict.value
        year_name = VarNames.year_name.value
        period_var = VarNames.period_var.value
        domain_name = VarNames.domain_name.value
        supply_var = VarNames.supply_var.value

        carbon_hwp_col = VarNames.carbon_hwp.value
        carbon_hwp_chg_col = VarNames.carbon_hwp_chg.value
        carbon_hwp_inflow_col = VarNames.carbon_hwp_inflow.value
        zy_region_var = VarNames.dummy_region.value

        country_data = add_data[country_data].copy()
        commodity_data = add_data[commodity][commodity_data].copy()

        data_aligned = timba_data[(timba_data[period_var] == 0) &
                                  (timba_data[domain_name] == supply_var)].copy().reset_index(drop=True)
        data_aligned = data_aligned[[timba_region_code, timba_commodity_code]].copy()
        data_aligned = data_aligned.merge(country_data[[timba_region_code, iso3_code]],
                                          left_on=timba_region_code,
                                          right_on=timba_region_code,
                                          how='left')

        cf_hwp = add_carbon_data[carbon_factor]
        hl_hwp = add_carbon_data[half_life]
        log_decay_rate = np.log(2) / hl_hwp
        log_decay_rate[log_decay_rate == np.inf] = 0
        period = 0

        if Path(f"{PKL_ADD_INFO_START_YEAR}.pkl").is_file():
            country_spec_start_year = DataManager.restore_from_pickle(f"{PKL_ADD_INFO_START_YEAR}.pkl")
        else:
            country_spec_start_year = (CarbonCalculator.determine_start_year
                                       (user_input=user_input,
                                        faostat_data=faostat_data,
                                        add_carbon_data=add_carbon_data))

        # Check if current user settings correspond to serialized start year data
        if ((len(country_spec_start_year[start_year].unique()) > 1) &
                (user_input[ParamNames.hist_hwp_start_year.value] != "country-specific")):
            country_spec_start_year = (CarbonCalculator.determine_start_year
                                       (user_input=user_input,
                                        faostat_data=faostat_data,
                                        add_carbon_data=add_carbon_data))
        else:
            pass

        faostat_data = faostat_data.fillna(0).reset_index(drop=True)

        fao_country = country_data[[timba_region_code, faostat_country_code]].copy()
        fao_country[timba_region_code] = fao_country[timba_region_code].replace(np.nan, zy_region_var)
        country_spec_start_year = country_spec_start_year.merge(fao_country[[timba_region_code, faostat_country_code]],
                                                                left_on=faostat_country_code,
                                                                right_on=faostat_country_code,
                                                                how='left')

        if user_input[ParamNames.c_hwp_accounting_approach.value] == production_approach:
            # Calculating domestic feedstock shares for industrial roundwood, pulp, recovered paper
            if len(commodity_data) == 14:
                ind_rndwood = faostat_data[faostat_data[faostat_item_code] == 1865].copy().reset_index(
                    drop=True)  # Todo set as defines

            elif (len(commodity_data) == 16) or (len(commodity_data) == 20):
                ind_rndwood = faostat_data[
                    (faostat_data[faostat_item_code] == 1866) |  # Todo set as defines
                    (faostat_data[faostat_item_code] == 1867)].copy().reset_index(drop=True)
                ind_rndwood = ind_rndwood.groupby(
                    [faostat_country_code, iso3_code, year_name])[
                    [faostat_production, faostat_export, faostat_import]].sum().reset_index()
            else:
                print("Unvalide commodity structure, verify input data")

            share_domestic_feedstock_ind_rndw = CarbonCalculator.calc_domestic_feedstock(data=ind_rndwood)
            pulp = faostat_data[faostat_data[faostat_item_code] == 1668].copy().reset_index(
                drop=True)  # Todo set as defines
            share_domestic_feedstock_pulp = CarbonCalculator.calc_domestic_feedstock(data=pulp)
            recov_paper = faostat_data[faostat_data[faostat_item_code] == 1669].copy().reset_index(
                drop=True)  # Todo set as defines
            share_domestic_feedstock_recov_paper = CarbonCalculator.calc_domestic_feedstock(data=recov_paper)

        if user_input[ParamNames.hist_hwp_start_year.value] == "default":
            # Adapt the number of years to the available years in FAOSTAT
            faostat_data_last_year = max(set(faostat_data[year_name]))
            default_year = user_input[ParamNames.hist_hwp_start_year_default.value]
            num_year = (faostat_data_last_year - default_year) + 1
        else:
            pass

        past_hwp_data = pd.DataFrame()
        for fao_com_code, timba_com_code in zip(commodity_data[faostat_item_code],
                                                commodity_data[timba_commodity_code]):
            start_year_data = country_spec_start_year[
                country_spec_start_year[faostat_item_code] == fao_com_code].reset_index(drop=True)
            start_year_data = start_year_data.sort_values(by=[timba_region_code], ascending=True).reset_index(drop=True)
            temp_hwp_data = pd.DataFrame(
                data_aligned[data_aligned[timba_commodity_code] == timba_com_code]).reset_index(drop=True)
            temp_hwp_data = pd.concat([temp_hwp_data, start_year_data[start_year]], axis=1)

            for year in range(0, num_year):
                temp_start_year = start_year_data.copy()
                temp_start_year[start_year] = temp_start_year[start_year] + year
                temp_faostat_data = faostat_data[(faostat_data[faostat_item_code] == fao_com_code)]
                temp_faostat_data = temp_start_year.merge(temp_faostat_data,
                                                          left_on=[start_year, faostat_country_code, faostat_item_code],
                                                          right_on=[year_name, faostat_country_code, faostat_item_code],
                                                          how="left")

                if user_input[ParamNames.c_hwp_accounting_approach.value] == stock_change_approach:
                    target_var = faostat_domestic_consumption
                    temp_faostat_data[faostat_domestic_consumption] = (
                            temp_faostat_data[faostat_production] +
                            temp_faostat_data[faostat_import] -
                            temp_faostat_data[faostat_export])

                elif user_input[ParamNames.c_hwp_accounting_approach.value] == production_approach:
                    target_var = faostat_production_domestic_feedstock

                    hwp_category = (
                        add_carbon_data[add_carbon_data[timba_commodity_code] == timba_com_code][hwp_category_var])
                    hwp_category = hwp_category.reset_index(drop=True)[0]

                    share_domestic_feedstock_ind_rndw_temp = temp_start_year.merge(
                        share_domestic_feedstock_ind_rndw,
                        left_on=[faostat_country_code, start_year],
                        right_on=[faostat_country_code, year_name],
                        how="left")
                    share_domestic_feedstock_pulp_temp = temp_start_year.merge(
                        share_domestic_feedstock_pulp,
                        left_on=[faostat_country_code, start_year],
                        right_on=[faostat_country_code, year_name],
                        how="left")
                    share_domestic_feedstock_recov_paper_temp = temp_start_year.merge(
                        share_domestic_feedstock_recov_paper,
                        left_on=[faostat_country_code, start_year],
                        right_on=[faostat_country_code, year_name],
                        how="left")

                    if (hwp_category == "sawnwood") or (hwp_category == "wood-based panels"):
                        share_domestic_harvest = share_domestic_feedstock_ind_rndw_temp[
                            [faostat_country_code, iso3_code, sh_domestic_feed]]
                    elif hwp_category == "paper and paperboard":
                        recov_paper_rate = 0.8  # from TiMBA input (change if TiMBA input is changed)

                        share_domestic_harvest = (
                                (share_domestic_feedstock_ind_rndw_temp[sh_domestic_feed] *
                                 (1 - recov_paper_rate) *
                                 share_domestic_feedstock_pulp_temp[sh_domestic_feed]) +
                                recov_paper_rate * share_domestic_feedstock_recov_paper_temp[sh_domestic_feed])
                        share_domestic_harvest = pd.concat([
                            share_domestic_feedstock_ind_rndw_temp[[faostat_country_code, iso3_code]],
                            share_domestic_harvest], axis=1)

                    else:
                        share_domestic_harvest = pd.DataFrame(np.zeros(len(temp_faostat_data)),
                                                              columns=[sh_domestic_feed])
                        share_domestic_harvest = pd.concat([
                            share_domestic_feedstock_ind_rndw_temp[[faostat_country_code, iso3_code]],
                            share_domestic_harvest], axis=1)

                    temp_faostat_data = temp_faostat_data.merge(share_domestic_harvest,
                                                                left_on=[faostat_country_code, iso3_code],
                                                                right_on=[faostat_country_code, iso3_code],
                                                                how="left")

                    temp_faostat_data[faostat_production_domestic_feedstock] = (
                            temp_faostat_data[faostat_production] *
                            temp_faostat_data[sh_domestic_feed])
                else:
                    print("Selected accounting approach is not implemented")

                # Merge not covered countries into zy dummy region
                country_subsets = [96, 128, 214, 41]  # To avoid double counting TODO Hard coded (future work)

                mask = (
                        (temp_faostat_data[timba_region_code] == zy_region_var) &
                        (~temp_faostat_data[faostat_country_code].isin(country_subsets))
                )

                temp_zy_data = {
                    timba_region_code: [zy_region_var],
                    target_var: [temp_faostat_data[mask][target_var].sum()]
                }
                temp_zy_data = pd.DataFrame(data=temp_zy_data)
                temp_faostat_data = pd.concat([
                    temp_faostat_data[temp_faostat_data[timba_region_code] != zy_region_var][
                        [timba_region_code, target_var]],
                    temp_zy_data], axis=0).sort_values(by=[timba_region_code]).reset_index(drop=True)

                mask_index = temp_faostat_data[temp_faostat_data[target_var] < 0].index
                temp_faostat_data.loc[mask_index, target_var] = 0
                temp_hwp_data[year] = temp_faostat_data[target_var]

            past_hwp_data = pd.concat([past_hwp_data, temp_hwp_data], axis=0).reset_index(drop=True)

        past_hwp_data = past_hwp_data.sort_values(by=[timba_region_code, timba_commodity_code],
                                                  ascending=[True, True]).fillna(0).reset_index(drop=True)

        carbonstock_hwp = past_hwp_data[[timba_region_code, timba_commodity_code, iso3_code, start_year]].copy()
        for year in range(0, num_year):
            temp_carbonstock_hwp = (cf_hwp * (past_hwp_data[year])) * CarbonConstants.CO2_FACTOR.value
            carbonstock_hwp[year] = temp_carbonstock_hwp
            carbonstock_hwp = carbonstock_hwp.reset_index(drop=True)

        data_info = carbonstock_hwp[[timba_region_code, timba_commodity_code, iso3_code, start_year]].copy()

        # For stock-change approach:
        # past_hwp_data = Average historical domestic consumption of semi-finished products
        # For production approach:
        # past_hwp_data = Average historical production of semi-finished products with domestic feedstock

        past_hwp_data = (past_hwp_data[range(0, num_year)].sum(axis=1) / len(range(0, num_year))) / 1000
        historic_carbonstock_hwp = (carbonstock_hwp[range(0, num_year)].sum(axis=1) / len(range(0, num_year))
                                    ) / log_decay_rate

        carboninflow_hwp = pd.DataFrame(data=np.zeros((len(data_aligned), 1)))[0]
        carbonstock_hwp = historic_carbonstock_hwp + carboninflow_hwp
        carbonstockchange_hwp = pd.DataFrame(data=np.zeros((len(data_aligned), 1)))[0]

        historic_carbonstock_hwp = pd.concat([
            data_info.rename(columns={start_year: year_name}),
            pd.DataFrame(data=[period] * len(data_aligned)).rename(columns={0: period_var}),
            pd.DataFrame(data=past_hwp_data).rename(columns={0: target_var}),
            pd.DataFrame(data=carboninflow_hwp).rename(columns={0: carbon_hwp_inflow_col}),
            pd.DataFrame(data=carbonstock_hwp).rename(columns={0: carbon_hwp_col}),
            pd.DataFrame(data=carbonstockchange_hwp).rename(columns={0: carbon_hwp_chg_col}),
        ], axis=1)

        return historic_carbonstock_hwp

    @staticmethod
    def calc_projection_carbon_hwp(timba_data: pd.DataFrame, carbon_data: pd.DataFrame, add_data: pd.DataFrame,
                                   add_carbon_data: pd.DataFrame, user_input: dict, period: int):
        """
        Calculates the future development of carbon stocks and fluxes related to semi-finished HWP based the production
        or the stock-change approach depending on the user input (IPCC 2019). Future developments of HWP carbon stocks
        are calculated based on TiMBA projections for the production, import, and export of semi-finished HWP.
        :param timba_data: TiMBA projections data for the production, import, export of semi-finished HWP
        :param carbon_data: Projections for carbon stocks in semi-finished HWP
        :param add_data: Additional data related to the country and HWP structure in TiMBA
        :param add_carbon_data: Additional data for carbon calculations
        :param user_input: Input from user
        :param period: Current period of the TiMBA projections
        :return: Historical carbon stocks in semi-finished HWP for all countries represented in TiMBA
        """
        carbon_factor = VarNames.carbon_factor.value
        half_life = VarNames.half_life.value
        faostat_country_code = VarNames.fao_country_code.value
        faostat_production = VarNames.faostat_production.value
        faostat_import = VarNames.faostat_import.value
        faostat_export = VarNames.faostat_export.value
        faostat_domestic_consumption = VarNames.faostat_domestic_consumption.value
        faostat_production_domestic_feedstock = VarNames.faostat_production_domestic_feedstock.value
        sh_domestic_feed = VarNames.share_domestic_feedstock.value
        iso3_code = VarNames.ISO3.value
        hwp_category_var = VarNames.hwp_category.value
        production_approach = VarNames.production_approach.value
        stock_change_approach = VarNames.stock_change_approach.value

        timba_region_code = VarNames.region_code.value
        timba_commodity_code = VarNames.commodity_code.value
        country_data = VarNames.country_data.value
        commodity_data = VarNames.commodity_data.value
        commodity = VarNames.commodity_dict.value
        year_name = VarNames.year_name.value
        period_var = VarNames.period_var.value
        domain_name = VarNames.domain_name.value
        supply_var = VarNames.supply_var.value
        production_var = VarNames.production_var.value
        import_var = VarNames.import_var.value
        export_var = VarNames.export_var.value
        quantity_var = VarNames.quantity_col.value

        carbon_hwp_col = VarNames.carbon_hwp.value
        carbon_hwp_chg_col = VarNames.carbon_hwp_chg.value
        carbon_hwp_inflow_col = VarNames.carbon_hwp_inflow.value

        country_data = add_data[country_data].copy()
        commodity_data = add_data[commodity][commodity_data].copy()

        data_aligned = timba_data[(timba_data[period_var] == period) &
                                  (timba_data[domain_name] == VarNames.supply_var.value)].copy().reset_index(drop=True)
        data_aligned = data_aligned[[timba_region_code, timba_commodity_code, period_var, year_name]].copy()
        data_aligned = data_aligned.merge(country_data[[timba_region_code, iso3_code]],
                                          left_on=timba_region_code,
                                          right_on=timba_region_code,
                                          how='left')

        cf_hwp = add_carbon_data[carbon_factor]
        hl_hwp = add_carbon_data[half_life]
        log_decay_rate = np.log(2) / hl_hwp
        log_decay_rate[log_decay_rate == np.inf] = 0

        timba_supply_prev = timba_data[(timba_data[domain_name] == supply_var) &
                                       (timba_data[period_var] == period - 1)].copy().reset_index(drop=True)
        timba_prod_prev = timba_data[(timba_data[domain_name] == production_var) &
                                     (timba_data[period_var] == period - 1)].copy().reset_index(drop=True)
        timba_prod_prev = pd.concat([timba_supply_prev, timba_prod_prev], axis=0).reset_index(drop=True)
        timba_prod_prev = timba_prod_prev.groupby([timba_region_code, timba_commodity_code, year_name])[
            quantity_var].sum().reset_index()
        timba_import_prev = timba_data[(timba_data[domain_name] == import_var) &
                                       (timba_data[period_var] == period - 1)].copy().reset_index(drop=True)
        timba_export_prev = timba_data[(timba_data[domain_name] == export_var) &
                                       (timba_data[period_var] == period - 1)].copy().reset_index(drop=True)

        timba_data_prev_info = timba_supply_prev[[timba_region_code, timba_commodity_code, year_name]].copy()
        timba_data_prev = pd.concat([
            timba_data_prev_info,
            pd.DataFrame(timba_prod_prev[quantity_var]).rename(columns={quantity_var: faostat_production}),
            pd.DataFrame(timba_import_prev[quantity_var]).rename(columns={quantity_var: faostat_import}),
            pd.DataFrame(timba_export_prev[quantity_var]).rename(columns={quantity_var: faostat_export})], axis=1)

        timba_data_prev = timba_data_prev.merge(country_data[[timba_region_code, faostat_country_code, iso3_code]],
                                                left_on=timba_region_code,
                                                right_on=timba_region_code,
                                                how='left')

        if user_input[ParamNames.c_hwp_accounting_approach.value] == stock_change_approach:
            target_var = faostat_domestic_consumption
            # Domestic consumption of semi-finished HWP
            timba_data_prev[faostat_domestic_consumption] = (timba_data_prev[faostat_production] +
                                                             timba_data_prev[faostat_import] -
                                                             timba_data_prev[faostat_export])

            negativ_data_index = timba_data_prev[timba_data_prev[faostat_domestic_consumption] < 0].index
            timba_data_prev.loc[negativ_data_index, faostat_domestic_consumption] = 0

        elif user_input[ParamNames.c_hwp_accounting_approach.value] == production_approach:
            target_var = faostat_production_domestic_feedstock
            # Share of domestic feedstock input:
            if len(commodity_data) == 14:
                ind_rndwood = timba_data_prev[
                    timba_data_prev[timba_commodity_code] == 81].copy().reset_index(drop=True)  # Todo set as defines

            elif (len(commodity_data) == 16) or (len(commodity_data) == 20):
                ind_rndwood = timba_data_prev[
                    (timba_data_prev[timba_commodity_code] == 78) |  # Todo set as defines
                    (timba_data_prev[timba_commodity_code] == 81)
                    ].copy().reset_index(drop=True)
                ind_rndwood = ind_rndwood.groupby(
                    [faostat_country_code, iso3_code, year_name])[
                    [faostat_production, faostat_export, faostat_import]].sum().reset_index()

            else:
                print("Unvalide commodity structure, verify input data")

            share_domestic_feedstock_ind_rndw = CarbonCalculator.calc_domestic_feedstock(data=ind_rndwood)

            pulp = timba_data_prev[timba_data_prev[timba_commodity_code] == 89].copy().reset_index(
                drop=True)  # Todo set as defines
            share_domestic_feedstock_pulp = CarbonCalculator.calc_domestic_feedstock(data=pulp)

            recov_paper = timba_data_prev[timba_data_prev[timba_commodity_code] == 90].copy().reset_index(
                drop=True)  # Todo set as defines
            share_domestic_feedstock_recov_paper = CarbonCalculator.calc_domestic_feedstock(data=recov_paper)

            timba_data_prev = pd.concat([timba_data_prev, add_carbon_data[hwp_category_var]], axis=1)

            timba_data_prev_lum = timba_data_prev[
                [commodity in ["sawnwood", "wood-based panels"] for commodity in timba_data_prev[hwp_category_var]]
            ].copy()
            timba_data_prev_ppp = timba_data_prev[timba_data_prev[hwp_category_var] == "paper and paperboard"].copy()

            timba_data_prev_other = timba_data_prev[timba_data_prev[hwp_category_var].isna()].copy()
            timba_data_prev_other[sh_domestic_feed] = 0

            share_domestic_harvest_lumber = share_domestic_feedstock_ind_rndw[
                [faostat_country_code, iso3_code, sh_domestic_feed]]

            timba_data_prev_lum = timba_data_prev_lum.merge(share_domestic_harvest_lumber,
                                                            left_on=[iso3_code, faostat_country_code],
                                                            right_on=[iso3_code, faostat_country_code],
                                                            how="left")

            recov_paper_rate = 0.8  # from TiMBA input (change if TiMBA input is changed) TODO shift to defines

            share_domestic_harvest_paper = (share_domestic_feedstock_ind_rndw[sh_domestic_feed] *
                                            (1 - recov_paper_rate) *
                                            share_domestic_feedstock_pulp[sh_domestic_feed]
                                            ) + recov_paper_rate * share_domestic_feedstock_recov_paper[
                                               sh_domestic_feed]

            share_domestic_harvest_paper = pd.concat([
                share_domestic_feedstock_ind_rndw[[faostat_country_code, iso3_code]],
                share_domestic_harvest_paper], axis=1)

            timba_data_prev_ppp = timba_data_prev_ppp.merge(share_domestic_harvest_paper,
                                                            left_on=[iso3_code, faostat_country_code],
                                                            right_on=[iso3_code, faostat_country_code],
                                                            how="left")
            timba_data_prev = pd.concat([
                timba_data_prev_lum,
                timba_data_prev_ppp,
                timba_data_prev_other], axis=0
            ).sort_values(by=[timba_region_code, timba_commodity_code]).reset_index(drop=True)

            # Production of semi-finished HWP with domestic feedstock
            timba_data_prev[faostat_production_domestic_feedstock] = (timba_data_prev[faostat_production] *
                                                                      timba_data_prev[sh_domestic_feed])

        carboninflow_prev = ((cf_hwp * timba_data_prev[target_var] * CarbonConstants.CARBON_TSD_FACTOR.value)
                             * CarbonConstants.CO2_FACTOR.value)

        carbonstock_hwp_prev = (
            carbon_data[carbon_data[period_var] == period - 1][carbon_hwp_col]).reset_index(drop=True)

        carboninflow_prev[(carboninflow_prev <= CarbonConstants.NON_ZERO_PARAMETER.value) &
                          (carboninflow_prev >= - CarbonConstants.NON_ZERO_PARAMETER.value)] = 0
        carbonstock_hwp_prev[(carbonstock_hwp_prev <= CarbonConstants.NON_ZERO_PARAMETER.value) &
                             (carbonstock_hwp_prev >= - CarbonConstants.NON_ZERO_PARAMETER.value)] = 0

        carbonstock_hwp_new = (carbonstock_hwp_prev * np.exp(-log_decay_rate) +
                               carboninflow_prev * ((1 - np.exp(-log_decay_rate)) / log_decay_rate))

        carbonstock_hwp_new = carbonstock_hwp_new.fillna(0)
        carbonstockchange_hwp = carbonstock_hwp_new - carbonstock_hwp_prev

        carbonstock_hwp = pd.concat([
            data_aligned[[timba_region_code, iso3_code, timba_commodity_code, period_var, year_name]],
            pd.DataFrame(data=timba_data_prev[target_var]),
            pd.DataFrame(data=carboninflow_prev).rename(columns={0: carbon_hwp_inflow_col}),
            pd.DataFrame(data=carbonstock_hwp_new, columns=[carbon_hwp_col]),
            pd.DataFrame(data=carbonstockchange_hwp, columns=[carbon_hwp_chg_col])], axis=1)
        carbon_data = pd.concat([carbon_data, carbonstock_hwp.copy()], axis=0).reset_index(drop=True)

        return carbon_data

    @staticmethod
    def calc_substitution_effect(self):
        self.logger.info(f"C-Module - Calculating substitution effect")
        for sc in self.sc_list:
            self.carbon_data[sc][VarNames.carbon_substitution.value] = CarbonCalculator.calc_constant_substitution_effect(
                add_carbon_data=self.add_carbon_data[VarNames.carbon_hwp.value],
                timba_data=self.timba_data[sc][VarNames.timba_data_all.value],
                add_data=self.add_data[VarNames.country_data.value])

    @staticmethod
    def calc_domestic_feedstock(data: pd.DataFrame):
        """
        Calculates domestic feedstock for production accounting approach
        :param data: FAOSTAT data for the selected commodity
        :return: domestic feedstock shares
        """
        faostat_production = VarNames.faostat_production.value
        faostat_import = VarNames.faostat_import.value
        faostat_export = VarNames.faostat_export.value
        faostat_country_code = VarNames.fao_country_code.value
        iso3_code = VarNames.ISO3.value
        year = VarNames.year_name.value
        sh_domestic_feed = VarNames.share_domestic_feedstock.value

        share_domestic_feedstock = (
                (data[faostat_production] - data[faostat_export]) /
                (data[faostat_production] + data[faostat_import] - data[faostat_export])
        )
        share_domestic_feedstock = pd.DataFrame(share_domestic_feedstock, columns=[sh_domestic_feed])
        share_domestic_feedstock[sh_domestic_feed] = (
            share_domestic_feedstock[sh_domestic_feed].fillna(0)
        )
        mask_index = share_domestic_feedstock[share_domestic_feedstock[sh_domestic_feed] < 0].index
        share_domestic_feedstock.loc[mask_index, sh_domestic_feed] = 0

        share_domestic_feedstock = pd.concat([
            data[[faostat_country_code, iso3_code, year]],
            share_domestic_feedstock], axis=1).sort_values(by=[faostat_country_code, year],
                                                           ascending=[True, True]).reset_index(drop=True)

        return share_domestic_feedstock

    @staticmethod
    def determine_start_year(faostat_data: pd.DataFrame, add_carbon_data: pd.DataFrame, user_input: dict):
        """
        Determines dynamically the start year for the historic HWP carbon pool calculation based on the data
        availability of FAOSTAT. The start year is determined for each country and product. The start year is determined
        by checking if production, import, and export quantities are reported for 5 consecutive years (IPCC guideline).
        To harmonized the start year for each country, the highest start year for all semi-finished products is taken.
        :param faostat_data: Processed FAOSTAT data
        :param add_carbon_data: Additional carbon data
        :param user_input: Input from user
        :return: DataFrame with start years
        """
        faostat_country_code = VarNames.fao_country_code.value
        faostat_commodity_code = VarNames.faostat_item_code.value
        year_var = VarNames.year_name.value
        start_year_var = VarNames.start_year.value

        faostat_production = VarNames.faostat_production.value
        faostat_import = VarNames.faostat_import.value
        faostat_export = VarNames.faostat_export.value
        hwp_category = VarNames.hwp_category.value

        country_data = pd.DataFrame(faostat_data[faostat_country_code].unique(), columns=[faostat_country_code])
        commodity_data = pd.DataFrame(faostat_data[faostat_commodity_code].unique(), columns=[faostat_commodity_code])

        start_year_data = country_data.join(commodity_data, how="cross")
        start_year_data[start_year_var] = 0

        if user_input[ParamNames.hist_hwp_start_year.value] == "country-specific":
            for country in tqdm(faostat_data[faostat_country_code].unique(), desc=f"Determining start year for hist HWP carbon pool"):
                for commodity in faostat_data[faostat_commodity_code].unique():
                    year_counter = 0
                    for year in faostat_data[year_var].unique():
                        temp_data = faostat_data[(faostat_data[faostat_country_code] == country) &
                                                 (faostat_data[faostat_commodity_code] == commodity) &
                                                 (faostat_data[year_var] == year)].reset_index(drop=True)
                        # Criteria for year selection: data availability for production, import, and export for 5
                        # consecutive years. Change selection criteria if too restrictive
                        if ((pd.notna(temp_data[faostat_production].iloc[0])) &
                                (pd.notna(temp_data[faostat_import].iloc[0])) &
                                (pd.notna(temp_data[faostat_export].iloc[0]))):
                            year_counter += 1
                            data_index = start_year_data[(start_year_data[faostat_country_code] == country) &
                                                         (start_year_data[faostat_commodity_code] == commodity)].index
                            if start_year_data.iloc[data_index][start_year_var].iloc[0] == 0:  # save year if no entry
                                start_year_data.loc[data_index, start_year_var] = year
                            else:
                                pass
                            if year_counter == 5:  # change to new product if 5 consecutive years are fulfilled
                                break
                            else:
                                pass

                        else:
                            data_index = start_year_data[(start_year_data[faostat_country_code] == country) &
                                                         (start_year_data[faostat_commodity_code] == commodity)].index
                            start_year_data.loc[data_index, start_year_var] = 0

            # Select last year with complete data
            semi_finished_commodity = add_carbon_data[
                                          [faostat_commodity_code, hwp_category]].iloc[0:len(commodity_data)].copy()
            semi_finished_commodity = semi_finished_commodity.dropna(axis=0)
            semi_finished_commodity = list(semi_finished_commodity[faostat_commodity_code])

            for country in start_year_data[faostat_country_code].unique():
                temp_data = start_year_data[(start_year_data[faostat_country_code] == country)].copy()
                temp_index = temp_data.index
                temp_data = temp_data[
                    [temp_item in semi_finished_commodity for temp_item in temp_data[faostat_commodity_code]]]
                year_max = max(temp_data[start_year_var])
                start_year_data.loc[temp_index, start_year_var] = year_max
        elif user_input[ParamNames.hist_hwp_start_year.value] == "default":
            start_year_data[start_year_var] = user_input[ParamNames.hist_hwp_start_year_default.value]

        else:
            print(f"Selected user setting for hist_hwp_start_year is not available")

        if not Path(f"{PKL_ADD_INFO_START_YEAR}.pkl").is_file():
            DataManager.serialize_to_pickle(start_year_data, f"{PKL_ADD_INFO_START_YEAR}.pkl")

        return start_year_data

    @staticmethod
    def calc_constant_substitution_effect(add_carbon_data, timba_data, add_data):
        """
        Calculate potential substitution of fossil based products by wood based products differentiating between material
        and energy uses. Calculations are based on constant displacement factors. Calculations based on equations xxx.
        :param timba_data: Projection data from TiMBA
        :param add_carbon_data: Additional carbon data
        :param add_data: DataFrame holding additional information related to countries
        :return: substitution_hwp as Dataframe of substitution hwp of fosil based equivalence (given in tCO2)
        """
        period_num = len(timba_data[VarNames.period_var.value].unique())
        displacement_factor = pd.concat([add_carbon_data[VarNames.displacement_factor.value]] * period_num
                                        ).reset_index(drop=True)
        cf_hwp = pd.concat([add_carbon_data[VarNames.carbon_factor.value]] * period_num).reset_index(drop=True)
        hl_hwp = pd.concat([add_carbon_data[VarNames.half_life.value]] * period_num).reset_index(drop=True)

        log_decay_rate = np.log(2) / hl_hwp
        log_decay_rate[log_decay_rate == np.inf] = 0

        data_aligned = timba_data[
            timba_data[VarNames.domain_name.value] == VarNames.supply_var.value].copy().reset_index(drop=True)
        data_aligned = data_aligned[[VarNames.region_code.value, VarNames.commodity_code.value,
                                     VarNames.period_var.value]].copy()
        data_aligned = data_aligned.merge(add_data[[VarNames.region_code.value, VarNames.ISO3.value]],
                                          left_on=VarNames.region_code.value,
                                          right_on=VarNames.region_code.value,
                                          how='left')

        cf_fuelwood = pd.concat([add_carbon_data[VarNames.commodity_code.value]] * period_num).reset_index(drop=True)
        cf_fuelwood = pd.DataFrame(np.where(np.array(cf_fuelwood) == 80, 1, 0))[0]

        supply_quantity = timba_data[
            timba_data[VarNames.domain_name.value] == VarNames.supply_var.value
        ][VarNames.quantity_col.value].reset_index(drop=True)
        production_quantity = timba_data[
            timba_data[VarNames.domain_name.value] == VarNames.production_var.value
        ][VarNames.quantity_col.value].reset_index(drop=True)
        export_quantity = timba_data[
            timba_data[VarNames.domain_name.value] == VarNames.export_var.value
        ][VarNames.quantity_col.value].reset_index(drop=True)
        import_quantity = timba_data[
            timba_data[VarNames.domain_name.value] == VarNames.import_var.value
        ][VarNames.quantity_col.value].reset_index(drop=True)

        apparent_consumption = ((supply_quantity + production_quantity + import_quantity - export_quantity) *
                                CarbonConstants.CARBON_TSD_FACTOR.value)

        # Material substitution
        carbon_inflow = apparent_consumption * cf_hwp
        carbon_inflow = carbon_inflow * ((1 - np.exp(-log_decay_rate)) / log_decay_rate)
        material_substitution = carbon_inflow * displacement_factor * CarbonConstants.CO2_FACTOR.value  # conversion to tCO2
        material_substitution = pd.concat([
            data_aligned,
            material_substitution.rename(VarNames.material_substitution.value)], axis=1)

        # Energy substitution
        energy_substitution = apparent_consumption * displacement_factor * cf_fuelwood * CarbonConstants.CO2_FACTOR.value  # conversion to tCO2
        energy_substitution = pd.concat([
            data_aligned,
            energy_substitution.rename(VarNames.energy_substitution.value)], axis=1)

        # Total substitution
        total_substitution = (material_substitution[VarNames.material_substitution.value] +
                              energy_substitution[VarNames.energy_substitution.value])
        total_substitution = pd.concat([
            data_aligned,
            total_substitution.rename(VarNames.total_substitution.value)], axis=1)
        mask_index = total_substitution[total_substitution[VarNames.total_substitution.value] <= 0].index
        total_substitution.loc[mask_index, VarNames.total_substitution.value] = 0

        substitution_data = pd.DataFrame()
        for period in timba_data[VarNames.period_var.value].unique():
            data_aligned_period = data_aligned[data_aligned[VarNames.period_var.value] == period].reset_index(drop=True)
            if period == 0:
                substitution_prev = pd.DataFrame(np.zeros(len(data_aligned_period)))[0]
            else:
                substitution_prev = substitution_data[substitution_data[VarNames.period_var.value] == period - 1
                ].copy().reset_index(drop=True)
                substitution_prev = pd.DataFrame(substitution_prev[VarNames.total_substitution.value]).rename(
                    columns={VarNames.total_substitution.value: 0})[0]

            total_substitution_period = total_substitution[
                total_substitution[VarNames.period_var.value] == period
            ][VarNames.total_substitution.value].reset_index(drop=True)

            substitution_change = total_substitution_period - substitution_prev
            if period == 0:
                substitution_change = pd.DataFrame(np.zeros(len(data_aligned_period)))[0]
            else:
                pass

            material_substitution_period = material_substitution[
                material_substitution[VarNames.period_var.value] == period
            ][VarNames.material_substitution.value].reset_index(drop=True)

            energy_substitution_period = energy_substitution[
                energy_substitution[VarNames.period_var.value] == period
            ][VarNames.energy_substitution.value].reset_index(drop=True)

            substitution_hwp = pd.concat([
                    data_aligned_period,
                    pd.DataFrame(data=material_substitution_period),
                    pd.DataFrame(data=energy_substitution_period),
                    pd.DataFrame(data=total_substitution_period),
                    pd.DataFrame(data=substitution_change).rename(
                        columns={0: VarNames.total_substitution_chg.value})],
                    axis=1)

            substitution_data = pd.concat([substitution_data, substitution_hwp], axis=0).reset_index(drop=True)

        substitution_data[VarNames.material_substitution.value] = (
                substitution_data[VarNames.material_substitution.value] / CarbonConstants.CARBON_MIO_FACTOR.value)
        substitution_data[VarNames.energy_substitution.value] = (
                substitution_data[VarNames.energy_substitution.value] / CarbonConstants.CARBON_MIO_FACTOR.value)
        substitution_data[VarNames.total_substitution.value] = (
                substitution_data[VarNames.total_substitution.value] / CarbonConstants.CARBON_MIO_FACTOR.value)
        substitution_data[VarNames.total_substitution_chg.value] = (
                substitution_data[VarNames.total_substitution_chg.value] / CarbonConstants.CARBON_MIO_FACTOR.value)

        return substitution_data

    @staticmethod
    def calc_total_carbon(self):
        """
        Calculate sum of all carbon stocks. Carbon stocks are expressed in MtCO2 (= 1.000.000 tonnes of CO2).
        Calculations based on equations xxx.
        :param self: C-Module object containing all module data.
        """
        self.logger.info(f"C-Module - Calculating total carbon stocks and fluxes")
        for sc in self.sc_list:
            timba_data = self.timba_data[sc][VarNames.timba_data_all.value]
            len_region = len(timba_data[VarNames.region_code.value].unique())
            timba_period = timba_data[VarNames.period_var.value].unique()
            len_period = len(timba_period)
            country_data = self.add_data[VarNames.country_data.value][[VarNames.region_code.value, VarNames.ISO3.value]]
            period_df = pd.concat([pd.DataFrame(timba_data[VarNames.period_var.value].unique())] * len_region
                                  ).reset_index(drop=True).rename(columns={0: VarNames.period_var.value})
            region_df = pd.concat([pd.DataFrame(timba_data[VarNames.region_code.value].unique())]
                                  ).reset_index(drop=True).rename(columns={0: VarNames.region_code.value})
            region_df = region_df.merge(country_data, left_on=VarNames.region_code.value,
                                        right_on=VarNames.region_code.value, how='left')

            carbon_hwp = self.carbon_data[sc][VarNames.carbon_hwp.value].copy()
            substitution = self.carbon_data[sc][VarNames.carbon_substitution.value].copy()
            carbon_biomass = self.carbon_data[sc][VarNames.carbon_forest_biomass.value].copy()
            carbon_soil = self.carbon_data[sc][VarNames.carbon_soil.value].copy()
            carbon_dwl = self.carbon_data[sc][VarNames.carbon_dwl.value].copy()

            carbonstock_hwp_total = pd.concat([(carbon_hwp.groupby([
                VarNames.region_code.value,
                VarNames.period_var.value])[VarNames.carbon_hwp.value].sum()
                                                ).reset_index(drop=True), period_df], axis=1)

            substitution_hwp_total = pd.concat([(substitution.groupby([
                VarNames.region_code.value,
                VarNames.period_var.value])[VarNames.total_substitution.value].sum()
                                                 ).reset_index(drop=True), period_df], axis=1)

            carbonstock_biomass_zy = pd.DataFrame([0] * len_period)
            carbonstock_biomass_total = pd.concat([
                pd.DataFrame((carbon_biomass.groupby([
                    VarNames.region_code.value,
                    VarNames.period_var.value])[VarNames.carbon_forest_biomass.value].sum())
                             ).reset_index(drop=True),
                carbonstock_biomass_zy.rename(columns={0: VarNames.carbon_forest_biomass.value})
            ], axis=0).reset_index(drop=True)[VarNames.carbon_forest_biomass.value]

            carbonstock_biomass_total = pd.concat([carbonstock_biomass_total, period_df], axis=1)

            carbonstock_soil_total = pd.concat([
                pd.DataFrame((carbon_soil.groupby([
                    VarNames.region_code.value,
                    VarNames.period_var.value])[VarNames.carbon_soil.value].sum())
                 ).reset_index(drop=True), carbonstock_biomass_zy.rename(columns={0: VarNames.carbon_soil.value})
            ], axis=0).reset_index(drop=True)[VarNames.carbon_soil.value]

            carbonstock_soil_total = pd.concat([carbonstock_soil_total, period_df], axis=1)

            carbonstock_dwl_total = pd.concat([
                pd.DataFrame((carbon_dwl.groupby([
                    VarNames.region_code.value,
                    VarNames.period_var.value])[VarNames.carbon_dwl.value].sum())
                 ).reset_index(drop=True), carbonstock_biomass_zy.rename(columns={0: VarNames.carbon_dwl.value})], axis=0
            ).reset_index(drop=True)[VarNames.carbon_dwl.value]

            carbonstock_dwl_total = pd.concat([carbonstock_dwl_total, period_df], axis=1)

            carbonstock_total = (carbonstock_biomass_total[VarNames.carbon_forest_biomass.value] +
                                 carbonstock_soil_total[VarNames.carbon_soil.value] +
                                 carbonstock_dwl_total[VarNames.carbon_dwl.value] +
                                 carbonstock_hwp_total[VarNames.carbon_hwp.value] +
                                 substitution_hwp_total[VarNames.total_substitution.value]
                                 ).rename(VarNames.carbon_total.value)

            carbonstock_total = pd.concat([carbonstock_total, period_df], axis=1)

            carbonstock_total_collector = pd.DataFrame()
            for period in timba_period:
                period_df = carbonstock_total[
                    carbonstock_total[VarNames.period_var.value] == period
                    ][VarNames.period_var.value].copy().reset_index(drop=True)
                if period == 0:
                    carbonstock_total_prev = pd.DataFrame(np.zeros(len(period_df)),
                                                          columns=[VarNames.carbon_total.value])
                    carbonstock_total_prev = carbonstock_total_prev[VarNames.carbon_total.value]
                else:
                    carbonstock_total_prev = carbonstock_total_collector[
                        carbonstock_total_collector[VarNames.period_var.value] == period - 1
                        ][VarNames.carbon_total.value].copy().reset_index(drop=True)

                carbonstock_total_period = carbonstock_total[
                    carbonstock_total[VarNames.period_var.value] == period
                    ][VarNames.carbon_total.value].copy().reset_index(drop=True)
                carbonstock_total_change = carbonstock_total_period - carbonstock_total_prev

                carbonstock_biomass_total_period = carbonstock_biomass_total[
                    carbonstock_biomass_total[VarNames.period_var.value] == period].copy().reset_index(drop=True)
                carbonstock_soil_total_period = carbonstock_soil_total[
                    carbonstock_soil_total[VarNames.period_var.value] == period].copy().reset_index(drop=True)
                carbonstock_dwl_total_period = carbonstock_dwl_total[
                    carbonstock_dwl_total[VarNames.period_var.value] == period].copy().reset_index(drop=True)
                carbonstock_hwp_total_period = carbonstock_hwp_total[
                    carbonstock_hwp_total[VarNames.period_var.value] == period].copy().reset_index(drop=True)
                substitution_hwp_total_period = substitution_hwp_total[
                    substitution_hwp_total[VarNames.period_var.value] == period].copy().reset_index(drop=True)

                carbonstock_total_period = pd.concat([
                    region_df,
                    period_df,
                    pd.DataFrame(data=carbonstock_biomass_total_period[VarNames.carbon_forest_biomass.value]),
                    pd.DataFrame(data=carbonstock_soil_total_period[VarNames.carbon_soil.value]),
                    pd.DataFrame(data=carbonstock_dwl_total_period[VarNames.carbon_dwl.value]),
                    pd.DataFrame(data=carbonstock_hwp_total_period[VarNames.carbon_hwp.value]),
                    pd.DataFrame(data=substitution_hwp_total_period[VarNames.total_substitution.value]),
                    pd.DataFrame(data=carbonstock_total_period),
                    pd.DataFrame(data=carbonstock_total_change).rename(
                        columns={VarNames.carbon_total.value: VarNames.carbon_total_chg.value})],
                    axis=1)

                carbonstock_total_collector = pd.concat([carbonstock_total_collector, carbonstock_total_period],
                                                        axis=0).reset_index(drop=True)

            self.carbon_data[sc][VarNames.carbon_total.value] = carbonstock_total_collector

    @staticmethod
    def run_carbon_calc(self):
        CarbonCalculator.calc_carbon_forest_biomass(self)
        CarbonCalculator.calc_carbon_forest_soil(self)
        CarbonCalculator.calc_carbon_forest_dwl(self)
        CarbonCalculator.calc_carbon_hwp(self)
        CarbonCalculator.calc_substitution_effect(self)
        CarbonCalculator.calc_total_carbon(self)
