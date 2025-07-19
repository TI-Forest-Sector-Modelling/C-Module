import datetime as dt
from pathlib import Path

current_dt = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")
PACKAGEDIR = Path(__file__).parent.parent.absolute()


# input
INPUT_FOLDER = PACKAGEDIR / Path("data") / Path("input")
RESULTS_INPUT = PACKAGEDIR / INPUT_FOLDER / Path("default_Sc_results")
FOREST_INPUT = PACKAGEDIR / INPUT_FOLDER / Path("default_Sc_forest")
PKL_RESULTS_INPUT = PACKAGEDIR / INPUT_FOLDER / Path("default_Sc_results")

FAOSTAT_DATA = INPUT_FOLDER / Path("20250703_faostat_data")
FRA_DATA = INPUT_FOLDER / Path("20250703_fra_data")

# additional information
ADD_INFO_FOLDER = PACKAGEDIR / INPUT_FOLDER / Path("additional_information")
ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
PKL_ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
ADD_INFO_COUNTRY = ADD_INFO_FOLDER / Path("country_data")
PKL_ADD_INFO_START_YEAR = ADD_INFO_FOLDER / Path("hist_hwp_carbon_start_year")

# output
OUTPUT_FOLDER = PACKAGEDIR / Path("data") / Path("output")

PKL_UPDATED_TIMBA_OUTPUT = OUTPUT_FOLDER / Path("updated_timba_output_D")
PKL_CARBON_OUTPUT = OUTPUT_FOLDER / Path("c_module_output_D")
PKL_CARBON_OUTPUT_AGG = OUTPUT_FOLDER / Path("carbon_results_agg_D")


LOGGING_OUTPUT_FOLDER = OUTPUT_FOLDER