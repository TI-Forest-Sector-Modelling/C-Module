import datetime as dt
import re
import os
from pathlib import Path
from c_module.user_io.default_parameters import user_input
from c_module.parameters.defines import ParamNames

current_dt = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")


def extract_scenarios(input_folder, output_folder):
    """
    Extract scenario names from Excel files in a folder and merge them with 'DataContainer_Sc_' prefix.
    :param input_folder: Path to the folder containing scenario files.
    :param output_folder: Path to the folder where the output files will be stored.
    :return: List of merged scenario names.
    """
    folder_path = Path(input_folder)
    scenarios = []
    for file in folder_path.glob("*.xlsx"):
        scenario_name = f"DataContainer_Sc_{file.stem}.pkl"
        scenario_path = Path(output_folder) / Path(scenario_name)
        scenarios.append(scenario_path)
    return scenarios


def cmodule_is_standalone():
    """
    Check if cmodule is standalone or not, covering if the code is run as the main program, covering CLI, script, IDE,
     and entry point runs.
    :return: Bool if cmodule is standalone or not.
    """
    import __main__
    import sys

    if getattr(__main__, "__file__", None):
        main_file = Path(__main__.__file__).resolve()
        package_root = Path(__file__).resolve().parents[1]

        if package_root in main_file.parents:
            return True

        if "pytest" in sys.modules and Path.cwd().resolve() == package_root.parent:
            return True

        if any("unittest" in mod for mod in sys.modules):
            return True

    return False


PACKAGEDIR = Path(__file__).parent.parent.absolute()
TIMBADIR = Path(__file__).parent.parent.parent.parent.parent.parent.absolute()
TIMBADIR_INPUT = TIMBADIR / Path("TiMBA") / Path("data") / Path("input") / Path("01_Input_Files")
TIMBADIR_OUTPUT = TIMBADIR / Path("TiMBA") / Path("data") / Path("output")
INPUT_FOLDER = PACKAGEDIR / Path("data") / Path("input")

if user_input[ParamNames.add_on_activated.value] or not cmodule_is_standalone():
    # input paths for add-on c-module
    AO_RESULTS_INPUT_PATTERN = r"results_D(\d{8}T\d{2}-\d{2}-\d{2})_(.*)"
    AO_FOREST_INPUT_PATTERN = r"forest_D(\d{8}T\d{2}-\d{2}-\d{2})_(.*)"
    AO_PKL_RESULTS_INPUT_PATTERN = r"DataContainer_Sc_(.*)"

    scenarios = extract_scenarios(TIMBADIR_INPUT, TIMBADIR_OUTPUT)
    PKL_RESULTS_INPUT = scenarios

    # output paths for add-on c-module
    OUTPUT_FOLDER = TIMBADIR_OUTPUT

else:
    # input paths for standalone c-module
    RESULTS_INPUT = list((INPUT_FOLDER / Path("projection_data")).glob(r"*results.pkl"))
    FOREST_INPUT = list((INPUT_FOLDER / Path("projection_data")).glob(r"*forest.pkl"))
    PKL_RESULTS_INPUT = list((INPUT_FOLDER / Path("projection_data")).glob(r"*.pkl"))

    # output paths for standalone c-module
    OUTPUT_FOLDER = PACKAGEDIR / Path("data") / Path("output")


# Official statistics from the Food and Agriculture Organization
FAOSTAT_DATA = INPUT_FOLDER / Path("historical_data") / Path("20250703_faostat_data")
FRA_DATA = INPUT_FOLDER / Path("historical_data") / Path("20250703_fra_data")

# additional information
ADD_INFO_FOLDER = PACKAGEDIR / INPUT_FOLDER / Path("additional_information")
ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
PKL_ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
ADD_INFO_COUNTRY = ADD_INFO_FOLDER / Path("country_data")
PKL_ADD_INFO_START_YEAR = ADD_INFO_FOLDER / Path("hist_hwp_carbon_start_year")

LOGGING_OUTPUT_FOLDER = OUTPUT_FOLDER
