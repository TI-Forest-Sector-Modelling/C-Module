from C_Module.parameters.defines import (VarNames, CarbonConstants)

import pandas as pd
import numpy as np

class CarbonCalculator:
    @staticmethod
    def calc_carbon_forest_biomass(self):
        self.logger.info(f"Calculating carbon stocks and fluxes for forest biomass (aboveground and belowground)")
        self.carbon_data[VarNames.carbon_forest_biomass.value] = CarbonCalculator.calc_carbon_forest(
            carbon_data=self.carbon_data[VarNames.carbon_forest_biomass.value],
            add_carbon_data=self.add_carbon_data,
            forest_data=self.timba_data[VarNames.timba_data_forest.value],
            monte_carlo=[VarNames.carbon_agb.value, VarNames.carbon_bgb.value])

    @staticmethod
    def calc_carbon_forest_soil(self):
        self.logger.info(f"Calculating carbon stocks and fluxes for forest soil")
        self.carbon_data[VarNames.carbon_soil.value] = CarbonCalculator.calc_carbon_forest(
            carbon_data=self.carbon_data[VarNames.carbon_soil.value],
            add_carbon_data=self.add_carbon_data,
            forest_data=self.timba_data[VarNames.timba_data_forest.value],
            monte_carlo=[VarNames.carbon_agb.value, VarNames.carbon_bgb.value])

    @staticmethod
    def calc_carbon_forest_dwl(self):
        self.logger.info(f"Calculating carbon stocks and fluxes for dead wood and litter")
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
        if self.UserInput["c_hwp_accounting_approach"] == "stock-change":
            self.logger.info(
                f"Calculating carbon stocks and fluxes for harvested wood products (stock-change approach)")
            self.carbon_data[VarNames.carbon_hwp.value] = CarbonCalculator.calc_carbon_hwp_stock_change(
                add_carbon_data=self.add_carbon_data[VarNames.carbon_hwp.value],
                add_data=self.add_data,
                timba_data=self.timba_data[VarNames.timba_data_all.value],
                faostat_data=self.faostat_data[VarNames.data_aligned.value])
        elif self.UserInput["c_hwp_accounting_approach"] == "production":
            self.logger.info(
                f"Calculating carbon stocks and fluxes for harvested wood products (production approach)")
            self.carbon_data[VarNames.carbon_hwp.value] = CarbonCalculator.calc_carbon_hwp_production(
                add_carbon_data=self.add_carbon_data[VarNames.carbon_hwp.value],
                add_data=self.add_data,
                timba_data=self.timba_data[VarNames.timba_data_all.value],
                faostat_data=self.faostat_data[VarNames.data_aligned.value])
        else:
            self.logger.info(f"Chosen option {self.UserInput['c_hwp_accounting_approach']} is not available.")

    @staticmethod
    def calc_carbon_hwp_stock_change(add_carbon_data, add_data, timba_data, faostat_data):
        """
        Carbon stock calculation for harvested wood products (hwp) based on IPCC-approach ("Stock-change" or "Production").
        For base period, FAOStat data is process and historical carbon pool of hwp is calculated based on processed data
        using apparent consumption.
        For all following periods, carbon stock in hwp in determined by carbon stock in previous periods, carbon inflows
        related to hwp apparent consumption in current period, and carbon outflow related to product decay.
        Calculations based on equations xxx.
        :param timba_data: Complete data of World Data container
        :param carbon_data: Dataframe from world data container with carbon data
        :param add_carbon_data: Complete data of carbon Data container
        """
        carbon_hwp = VarNames.carbon_hwp.value
        carbon_factor = VarNames.carbon_factor.value
        half_life = VarNames.half_life.value
        faostat_country_code = VarNames.fao_country_code.value
        faostat_item_code = VarNames.faostat_item_code.value
        faostat_year = VarNames.faostat_year.value
        faostat_production = VarNames.faostat_production.value
        faostat_import = VarNames.faostat_import.value
        faostat_export = VarNames.faostat_export.value
        faostat_domestic_consumption = VarNames.faostat_domestic_consumption.value

        timba_region_code = VarNames.region_code.value
        timba_commodity_code = VarNames.commodity_code.value
        country_data = VarNames.country_data.value
        commodity_data = VarNames.commodity_data.value
        commodity = VarNames.commodity_dict.value
        year_name = VarNames.year_name.value
        period_var = VarNames.period_var.value
        domain_name = VarNames.domain_name.value

        carbon_hwp_col = VarNames.carbon_hwp.value
        carbon_hwp_chg_col = VarNames.carbon_hwp_chg.value
        carbon_hwp_inflow_col = VarNames.carbon_hwp_inflow.value
        zy_region_var = VarNames.dummy_region.value

        country_data = add_data[country_data].copy()
        commodity_data = add_data[commodity][commodity_data].copy()

        data_aligned = timba_data[(timba_data[period_var] == 0) &
                                  (timba_data[domain_name] == VarNames.supply_var.value)].copy().reset_index(drop=True)
        data_aligned = data_aligned[[timba_region_code, timba_commodity_code]].copy()

        cf_hwp = add_carbon_data[carbon_factor]
        hl_hwp = add_carbon_data[half_life]
        log_decay_rate = np.log(2) / hl_hwp
        log_decay_rate[log_decay_rate == np.inf] = 0
        projection_start_year = min(timba_data[year_name].unique())

        carbon_data = pd.DataFrame()
        for period in timba_data[period_var].unique():
            if period == 0:
                year_average_inflow = list(range(projection_start_year, projection_start_year + 5))

                fao_country = pd.concat([country_data[timba_region_code],
                                         country_data[faostat_country_code]], axis=1)
                fao_country[timba_region_code] = fao_country[timba_region_code].replace(np.nan, zy_region_var)
                fao_data_year = faostat_data[faostat_year].unique()
                year_average_inflow = list(set(year_average_inflow) & set(fao_data_year))

                past_domestic_consumption = pd.DataFrame()
                for fao_com_code, timba_com_code in zip(commodity_data[VarNames.faostat_item_code.value],
                                                       commodity_data[VarNames.commodity_code.value]):

                    commodity_domestic_consumption = pd.DataFrame(
                        data_aligned[data_aligned[timba_commodity_code] == timba_com_code]).reset_index(drop=True)

                    for year in year_average_inflow:
                        if fao_com_code == 1640:  # TODO Hard coded (future work)
                            # Merge fao data for plywood and veneer
                            temp_fao_data_plywood = faostat_data[
                                (faostat_data[faostat_item_code] == fao_com_code) &
                                (faostat_data[faostat_year] == year)].reset_index(drop=True)
                            temp_fao_data_veneer = faostat_data[
                                (faostat_data[faostat_item_code] == 1634) &
                                (faostat_data[faostat_year] == year)].reset_index(drop=True)

                            if len(temp_fao_data_veneer) == 0:
                                temp_fao_data_veneer = pd.DataFrame(
                                    np.zeros([len(temp_fao_data_plywood), len(temp_fao_data_plywood.columns)]))
                                temp_fao_data_veneer.columns = temp_fao_data_plywood.columns

                            temp_fao_data = temp_fao_data_plywood.copy()
                            temp_fao_data[faostat_production] = (temp_fao_data_plywood[faostat_production] +
                                                                 temp_fao_data_veneer[faostat_production])
                            temp_fao_data[faostat_import] = (temp_fao_data_plywood[faostat_import] +
                                                             temp_fao_data_veneer[faostat_import])
                            temp_fao_data[faostat_export] = (temp_fao_data_plywood[faostat_export] +
                                                             temp_fao_data_veneer[faostat_export])
                        else:
                            temp_fao_data = faostat_data[
                                (faostat_data[faostat_item_code] == fao_com_code) &
                                (faostat_data[faostat_year] == year)]
                        temp_fao_data = temp_fao_data.merge(fao_country,left_on=faostat_country_code,
                                                            right_on=faostat_country_code, how="left")
                        temp_fao_data[faostat_domestic_consumption] = (temp_fao_data[faostat_production] +
                                                                       temp_fao_data[faostat_import] -
                                                                       temp_fao_data[faostat_export])

                        country_subsets = [96, 128, 214, 41]  # To avoid double counting TODO Hard coded (future work)

                        mask = (
                                (temp_fao_data[timba_region_code] == zy_region_var) &
                                (~temp_fao_data[faostat_country_code].isin(country_subsets))
                        )

                        temp_zy_data = {
                            timba_region_code: [zy_region_var],
                            faostat_domestic_consumption: [
                                temp_fao_data[mask][faostat_domestic_consumption].sum()]}

                        temp_zy_data = pd.DataFrame(data=temp_zy_data)

                        temp_fao_data = pd.concat([
                            temp_fao_data[temp_fao_data[timba_region_code] != zy_region_var][
                                [timba_region_code, faostat_domestic_consumption]],
                            temp_zy_data], axis=0).sort_values(by=[timba_region_code]).reset_index(drop=True)

                        mask_index = temp_fao_data[temp_fao_data[faostat_domestic_consumption] < 0].index
                        temp_fao_data.loc[mask_index, faostat_domestic_consumption] = 0
                        commodity_domestic_consumption[year] = temp_fao_data[faostat_domestic_consumption]

                    past_domestic_consumption = pd.concat([
                        past_domestic_consumption, commodity_domestic_consumption], axis=0).reset_index(drop=True)

                past_domestic_consumption = past_domestic_consumption.sort_values(
                    by=[timba_region_code, timba_commodity_code], ascending=[True, True]
                ).fillna(0).reset_index(drop=True)

                carbonstock_hwp = past_domestic_consumption[data_aligned.columns].copy()
                for year in year_average_inflow:
                    temp_carbonstock_hwp = (cf_hwp * (past_domestic_consumption[year])
                                            ) * CarbonConstants.CO2_FACTOR.value
                    carbonstock_hwp[year] = temp_carbonstock_hwp
                    carbonstock_hwp = carbonstock_hwp.reset_index(drop=True)

                historic_domestic_consumption = (
                        past_domestic_consumption[year_average_inflow].sum(axis=1) / len(year_average_inflow)) / 1000
                historic_carbonstock_hwp = (
                        (carbonstock_hwp[year_average_inflow].sum(axis=1) / len(year_average_inflow)) / log_decay_rate)

                carboninflow_hwp = pd.DataFrame(data=np.zeros((len(data_aligned), 1)))[0]
                carbonstock_hwp_prev = pd.DataFrame(data=np.zeros((len(data_aligned), 1)))[0]
                carbonstock_hwp = historic_carbonstock_hwp + carboninflow_hwp
                carbonstockchange_hwp = historic_carbonstock_hwp - carbonstock_hwp_prev

                carbonstock_hwp = pd.concat([
                    data_aligned[[timba_region_code, timba_commodity_code]],
                    pd.DataFrame(data=[period] * len(data_aligned)).rename(columns={0: period_var}),
                    pd.DataFrame(data=historic_domestic_consumption).rename(columns={0: faostat_domestic_consumption}),
                    pd.DataFrame(data=carboninflow_hwp).rename(columns={0: carbon_hwp_inflow_col}),
                    pd.DataFrame(data=carbonstock_hwp).rename(columns={0: carbon_hwp_col}),
                    pd.DataFrame(data=carbonstockchange_hwp).rename(columns={0: carbon_hwp_chg_col}),
                ], axis=1)

                carbon_data = pd.concat([carbon_data, carbonstock_hwp.copy()], axis=0).reset_index(drop=True)

            else:
                supply_quantity_prev = timba_data[
                    (timba_data[VarNames.domain_name.value] == VarNames.supply_var.value) &
                    (timba_data[period_var] == period - 1)][VarNames.quantity_col.value].copy().reset_index(drop=True)

                production_quantity_prev = timba_data[
                    (timba_data[VarNames.domain_name.value] == VarNames.production_var.value) &
                    (timba_data[period_var] == period - 1)][VarNames.quantity_col.value].copy().reset_index(drop=True)

                import_quantity_prev = timba_data[
                    (timba_data[VarNames.domain_name.value] == VarNames.import_var.value) &
                    (timba_data[period_var] == period - 1)][VarNames.quantity_col.value].copy().reset_index(drop=True)

                export_quantity_prev = timba_data[
                    (timba_data[VarNames.domain_name.value] == VarNames.export_var.value) &
                    (timba_data[period_var] == period - 1)][VarNames.quantity_col.value].copy().reset_index(drop=True)

                domestic_consumption = (supply_quantity_prev + production_quantity_prev +
                                        import_quantity_prev - export_quantity_prev)

                domestic_consumption[domestic_consumption < 0] = 0

                carboninflow_prev = ((cf_hwp * domestic_consumption * CarbonConstants.CARBON_TSD_FACTOR.value)
                                     * CarbonConstants.CO2_FACTOR.value)

                carbonstock_hwp_prev = (
                    carbon_data[carbon_data[period_var] == period - 1][carbon_hwp_col]).reset_index(drop=True)

                carboninflow_prev[(carboninflow_prev <= CarbonConstants.NON_ZERO_PARAMETER.value) &
                                  (carboninflow_prev >= - CarbonConstants.NON_ZERO_PARAMETER.value)] = 0
                carbonstock_hwp_prev[(carboninflow_prev <= CarbonConstants.NON_ZERO_PARAMETER.value) &
                                     (carboninflow_prev >= - CarbonConstants.NON_ZERO_PARAMETER.value)] = 0

                carbonstock_hwp_new = (carbonstock_hwp_prev * np.exp(-log_decay_rate) +
                                       carboninflow_prev * ((1 - np.exp(-log_decay_rate)) / log_decay_rate))

                carbonstock_hwp_new = carbonstock_hwp_new.fillna(0)
                carbonstockchange_hwp = carbonstock_hwp_new - carbonstock_hwp_prev

                data_carbonstock_hwp_rest = (
                    carbon_data[carbon_data[period_var] != period - 1]).reset_index(drop=True)
                data_carbonstock_hwp_prev = (
                    carbon_data[carbon_data[period_var] == period - 1]).reset_index(drop=True)

                data_carbonstock_hwp_prev[carbon_hwp_inflow_col] = carboninflow_prev
                carbonstock_hwp_prev = (pd.concat([data_carbonstock_hwp_rest, data_carbonstock_hwp_prev], axis=0)
                                        ).sort_values(by=[period_var, timba_region_code], ascending=[True, True]
                                                      ).reset_index(drop=True)
                carboninflow = pd.DataFrame(data=np.zeros((len(data_aligned), 1)))

                carbonstock_hwp = pd.concat([
                    data_aligned[[timba_region_code, timba_commodity_code]],
                    pd.DataFrame(data=domestic_consumption).rename(
                        columns={VarNames.quantity_col.value: faostat_domestic_consumption}),
                    pd.DataFrame(data=carboninflow_prev).rename(columns={0: carbon_hwp_inflow_col}),
                    pd.DataFrame(data=carbonstock_hwp_new, columns=[carbon_hwp_col]),
                    pd.DataFrame(data=carbonstockchange_hwp, columns=[carbon_hwp_chg_col]),
                    pd.DataFrame(data=[period] * len(data_aligned)).rename(columns={0: period_var})],
                    axis=1)
                carbon_data = pd.concat([carbon_data, carbonstock_hwp.copy()], axis=0).reset_index(drop=True)

        return carbon_data


    @staticmethod
    def calc_carbon_hwp_production(add_carbon_data, add_data, timba_data, faostat_data):
        placeholder = pd.DataFrame()
        return placeholder

    @staticmethod
    def calc_substitution_effect(self):
        self.logger.info(f"Calculating substitution effect")
        self.carbon_data[VarNames.carbon_substitution.value] = CarbonCalculator.calc_constant_substitution_effect(
            add_carbon_data=self.add_carbon_data[VarNames.carbon_hwp.value],
            timba_data=self.timba_data[VarNames.timba_data_all.value]
        )

    @staticmethod
    def calc_constant_substitution_effect(add_carbon_data, timba_data):
        """
        Calculate potential substitution of fossil based products by wood based products differentiating between material
        and energy uses. Calculations are based on constant displacement factors. Calculations based on equations xxx.
        :param timba_data: Projection data from TiMBA
        :param add_carbon_data: Additional carbon data
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

        return substitution_data

    @staticmethod
    def calc_total_carbon(self):
        self.logger.info(f"Calculating total carbon stocks and fluxes")
        pass

    @staticmethod
    def run_carbon_calc(self):
        CarbonCalculator.calc_carbon_forest_biomass(self)
        CarbonCalculator.calc_carbon_forest_soil(self)
        CarbonCalculator.calc_carbon_forest_dwl(self)
        CarbonCalculator.calc_carbon_hwp(self)
        CarbonCalculator.calc_substitution_effect(self)
        CarbonCalculator.calc_total_carbon(self)
