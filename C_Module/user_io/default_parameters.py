# Overall parameters
calc_c_ex_post = True
calc_c_ex_ante = True

start_year = 2020
end_year = 2050

read_in_pkl = True
save_data_as = "csv"  # Options: "pkl", "csv", "all"

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

user_input = {
    "calc_c_ex_post": calc_c_ex_post,
    "calc_c_ex_ante": calc_c_ex_ante,
    "start_year": start_year,
    "end_year": end_year,
    "read_in_pkl": read_in_pkl,
    "save_data_as": save_data_as,
    "calc_c_forest_agb": calc_c_forest_agb,
    "calc_c_forest_bgb": calc_c_forest_bgb,
    "calc_c_forest_soil": calc_c_forest_soil,
    "calc_c_forest_dwl": calc_c_forest_dwl,
    "calc_c_hwp": calc_c_hwp,
    "c_hwp_accounting_approach": c_hwp_accounting_approach,
    "historical_c_hwp": historical_c_hwp,
    "hist_hwp_start_year": hist_hwp_start_year,
    "hist_hwp_start_year_default": hist_hwp_start_year_default
}
