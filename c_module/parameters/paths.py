import datetime as dt
import re
import os
from pathlib import Path
from c_module.user_io.default_parameters import user_input
from c_module.parameters.defines import ParamNames

current_dt = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")


def get_latest_file(folder_path, pattern, use_timestamp):
    """
    Get the latest generated file with the provided pattern in the provided folder.
    :param folder_path: Path of the folder where the file is located
    :param pattern: Pattern of the file to match
    :param use_timestamp: Use timestamp when matching
    :return: The latest generated file and its timestamp
    """
    files = []
    if use_timestamp:
        for fname in os.listdir(folder_path):
            match = re.match(pattern, fname)
            if match:
                ts_str = match.group(1)
                ts = dt.datetime.strptime(ts_str, "%Y%m%dT%H-%M-%S")
                full_path = os.path.join(folder_path, fname)
                files.append((ts, ts_str, os.path.splitext(full_path)[0]))
                return max(files, key=lambda x: x[0]) if files else (None, None, None)
    else:
        for fname in os.listdir(folder_path):
            if pattern and not re.match(pattern, fname):
                continue
            full_path = os.path.join(folder_path, fname)
            if os.path.isfile(full_path):
                ts = dt.datetime.fromtimestamp(os.path.getmtime(full_path))
                files.append((ts, None, os.path.splitext(full_path)[0]))
        latest_file = max(files, key=lambda x: x[0])
        match = re.match(r"DataContainer_Sc_(.*)", os.path.basename(latest_file[2]))
        scenario_name = match.group(1)
        latest_file = latest_file + (scenario_name,)
        return latest_file


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

    return False


PACKAGEDIR = Path(__file__).parent.parent.absolute()
TIMBADIR = Path(__file__).parent.parent.parent.parent.parent.parent.absolute()
TIMBADIR = TIMBADIR / Path("TiMBA") / Path("data") / Path("output")
INPUT_FOLDER = PACKAGEDIR / Path("data") / Path("input")

if user_input[ParamNames.add_on_activated.value] or not cmodule_is_standalone():
    # input paths for add-on c-module
    AO_RESULTS_INPUT_PATTERN = r"results_D(\d{8}T\d{2}-\d{2}-\d{2})_.*"
    AO_FOREST_INPUT_PATTERN = r"forest_D(\d{8}T\d{2}-\d{2}-\d{2})_.*"
    AO_PKL_RESULTS_INPUT_PATTERN = r"DataContainer_Sc_.*"

    datetime, latest_timestamp_results, latest_result_input = get_latest_file(folder_path=TIMBADIR,
                                                                              pattern=AO_RESULTS_INPUT_PATTERN,
                                                                              use_timestamp=True)
    datetime, latest_timestamp_results, latest_forest_input = get_latest_file(folder_path=TIMBADIR,
                                                                              pattern=AO_FOREST_INPUT_PATTERN,
                                                                              use_timestamp=True)
    datetime, latest_timestamp, latest_pkl_input, sc_name = get_latest_file(folder_path=TIMBADIR,
                                                                            pattern=AO_PKL_RESULTS_INPUT_PATTERN,
                                                                            use_timestamp=False)
    RESULTS_INPUT = latest_result_input
    FOREST_INPUT = latest_forest_input
    PKL_RESULTS_INPUT = latest_pkl_input

    # output paths for add-on c-module
    OUTPUT_FOLDER = TIMBADIR
    PKL_UPDATED_TIMBA_OUTPUT = latest_pkl_input
    PKL_CARBON_OUTPUT = OUTPUT_FOLDER / Path(f"c_module_output_{latest_timestamp_results}")
    PKL_CARBON_OUTPUT_AGG = OUTPUT_FOLDER / Path(f"carbon_results_agg_{latest_timestamp_results}")
    SC_NAME = sc_name

else:
    # input paths for standalone c-module
    RESULTS_INPUT = PACKAGEDIR / INPUT_FOLDER / Path("default_Sc_results")
    FOREST_INPUT = PACKAGEDIR / INPUT_FOLDER / Path("default_Sc_forest")
    PKL_RESULTS_INPUT = PACKAGEDIR / INPUT_FOLDER / Path("default_Sc_results")

    # output paths for standalone c-module
    OUTPUT_FOLDER = PACKAGEDIR / Path("data") / Path("output")
    PKL_UPDATED_TIMBA_OUTPUT = OUTPUT_FOLDER / Path("updated_timba_output_D")
    PKL_CARBON_OUTPUT = OUTPUT_FOLDER / Path("c_module_output_D")
    PKL_CARBON_OUTPUT_AGG = OUTPUT_FOLDER / Path("carbon_results_agg_D")
    SC_NAME = "default_Sc"


# Official statistics from the Food and Agriculture Organization
FAOSTAT_DATA = INPUT_FOLDER / Path("20250703_faostat_data")
FRA_DATA = INPUT_FOLDER / Path("20250703_fra_data")

# additional information
ADD_INFO_FOLDER = PACKAGEDIR / INPUT_FOLDER / Path("additional_information")
ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
PKL_ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
ADD_INFO_COUNTRY = ADD_INFO_FOLDER / Path("country_data")
PKL_ADD_INFO_START_YEAR = ADD_INFO_FOLDER / Path("hist_hwp_carbon_start_year")

LOGGING_OUTPUT_FOLDER = OUTPUT_FOLDER