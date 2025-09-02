from c_module.parameters.defines import ParamNames

# Overall parameters
add_on_activated = False

# Activate the option of controling start and end year of the calculations if the module is used as standalone
start_year = 2020  # Not activated
end_year = 2050  # Not activated

read_in_pkl = True  # Caution False option is not implemented yet

# Forest carbon related parameters
calc_c_forest_agb = True
calc_c_forest_bgb = True
calc_c_forest_soil = True
calc_c_forest_dwl = True

# HWP carbon related parameters
calc_c_hwp = True
c_hwp_accounting_approach = "stock-change"  # Options: "stock-change" or "production"
historical_c_hwp = "average"  # Options: "average" or "historical"
hist_hwp_start_year = "default"  # Options: "country-specific", "default"
hist_hwp_start_year_default = 2020

# Visualization parameters
show_carbon_dashboard = True

user_input = {
    ParamNames.add_on_activated.value: add_on_activated,
    ParamNames.start_year.value: start_year,
    ParamNames.end_year.value: end_year,
    ParamNames.read_in_pkl.value: read_in_pkl,
    ParamNames.calc_c_forest_agb.value: calc_c_forest_agb,
    ParamNames.calc_c_forest_bgb.value: calc_c_forest_bgb,
    ParamNames.calc_c_forest_soil.value: calc_c_forest_soil,
    ParamNames.calc_c_forest_dwl.value: calc_c_forest_dwl,
    ParamNames.calc_c_hwp.value: calc_c_hwp,
    ParamNames.c_hwp_accounting_approach.value: c_hwp_accounting_approach,
    ParamNames.historical_c_hwp.value: historical_c_hwp,
    ParamNames.hist_hwp_start_year.value: hist_hwp_start_year,
    ParamNames.hist_hwp_start_year_default.value: hist_hwp_start_year_default,
    ParamNames.show_carbon_dashboard.value: show_carbon_dashboard
}
