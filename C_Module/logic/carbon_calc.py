from C_Module.parameters.defines import (VarNames, CarbonConstants)

import pandas as pd
import numpy as np

class CarbonCalculator:
    @staticmethod
    def calc_carbon_forest_biomass(self):
        self.carbon_data[VarNames.carbon_forest_biomass.value] = CarbonCalculator.calc_carbon_forest(
            carbon_data=self.carbon_data[VarNames.carbon_forest_biomass.value],
            add_carbon_data=self.add_carbon_data,
            forest_data=self.timba_data[VarNames.timba_data_forest.value],
            monte_carlo=[VarNames.carbon_agb.value, VarNames.carbon_bgb.value])

    @staticmethod
    def calc_carbon_forest_soil(self):
        self.carbon_data[VarNames.carbon_soil.value] = CarbonCalculator.calc_carbon_forest(
            carbon_data=self.carbon_data[VarNames.carbon_soil.value],
            add_carbon_data=self.add_carbon_data,
            forest_data=self.timba_data[VarNames.timba_data_forest.value],
            monte_carlo=[VarNames.carbon_agb.value, VarNames.carbon_bgb.value])

    @staticmethod
    def calc_carbon_forest_dwl(self):
        self.carbon_data[VarNames.carbon_dwl.value] = CarbonCalculator.calc_carbon_forest(
            carbon_data=self.carbon_data[VarNames.carbon_dwl.value],
            add_carbon_data=self.add_carbon_data,
            forest_data=self.timba_data[VarNames.timba_data_forest.value],
            monte_carlo=[VarNames.carbon_agb.value, VarNames.carbon_bgb.value])

    @staticmethod
    def calc_carbon_forest(carbon_data, add_carbon_data, forest_data, monte_carlo):
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
        :param add_carbon_data: DataContainer with carbon data
        :param monte_carlo: List storing names of carbon pools quantified with randomized emission factor
        :return: Updated dataframe of selected carbon pool
        """
        c_dens_avg = VarNames.carbon_density_avg.value
        c_dens_avg_rnd = VarNames.carbon_density_avg_rand.value

        if VarNames.carbon_forest_biomass.value in carbon_data.columns:
            unit_conversion_param = CarbonConstants.CARBON_MIO_FACTOR.value
            forest_data_col = "ForStock"

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
            forest_data_col = "ForArea"
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
        for period in forest_data["Period"].unique():
            period_vector = pd.DataFrame([period]).rename(columns={0: "Period"})
            forest_data_period = forest_data[forest_data["Period"] == period].copy().reset_index(drop=True)
            if period == 0:
                forest_variable_prev = pd.DataFrame(np.zeros(len(forest_data_period)))[0]
                carbonstock_prev = pd.DataFrame(np.zeros(len(forest_data_period)))[0]
            else:
                forest_variable_prev = (
                    forest_data[forest_data["Period"] == period - 1][forest_data_col]).copy().reset_index(drop=True)
                carbonstock_prev = (
                    carbon_data[carbon_data["Period"] == period - 1][col_name]).copy().reset_index(drop=True)

            forest_variable_new = forest_data_period[forest_data_col].copy().reset_index(drop=True)
            carbonstock_change = (
                    emission_factor * (forest_variable_new - forest_variable_prev) * unit_conversion_param)
            carbonstock_new = carbonstock_change + carbonstock_prev


            carbonstock_forest = pd.concat([
                forest_data_period[[VarNames.region_code.value, forest_data_col]],
                pd.DataFrame(data=carbonstock_new, columns=[col_name]),
                pd.DataFrame(data=carbonstock_change, columns=[col_name_change]),
                pd.DataFrame(data=pd.concat([period_vector] * len(forest_data_period)).reset_index(drop=True))
            ], axis=1)
            carbon_data = pd.concat([carbon_data, carbonstock_forest.copy()], axis=0).reset_index(drop=True)

        return carbon_data

    @staticmethod
    def calc_carbon_hwp(self):
        pass

    @staticmethod
    def calc_substitution_effect(self):
        pass

    @staticmethod
    def run_carbon_calc(self):
        CarbonCalculator.calc_carbon_forest_biomass(self)
        CarbonCalculator.calc_carbon_forest_soil(self)
        CarbonCalculator.calc_carbon_forest_dwl(self)
        CarbonCalculator.calc_carbon_hwp(self)
        CarbonCalculator.calc_substitution_effect(self)