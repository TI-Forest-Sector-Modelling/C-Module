import datetime as dt

current_dt = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")

# input
RESULTS_INPUT = "data/input/default_Sc_results"
FOREST_INPUT = "data/input/default_Sc_forest"
PKL_RESULTS_INPUT = "data/input/default_Sc_results"

ADDITIONAL_INFORMATION_CARBON_PATH = r"data/input/additional_information/carbon_additional_information.xlsx"
PKL_ADD_INFO_CARBON_PATH = r"data/input/additional_information/AddInfoContentCarbon.pkl"

# output
CARBON_OUTPUT = "data/output/carbon_results_D"
CARBON_OUTPUT_AGG = "data/output/carbon_results_agg_D"

PKL_CARBON_OUTPUT = "data/output/carbon_results_D"
PKL_CARBON_OUTPUT_AGG = "data/output/carbon_results_agg_D"


LOGGING_OUTPUT_FOLDER = r"data/output"