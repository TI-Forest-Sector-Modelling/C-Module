import datetime as dt
import re
import os
from pathlib import Path
from c_module.user_io.default_parameters import user_input
from c_module.parameters.defines import ParamNames

current_dt = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")


def get_latest_file(folder_path, pattern, use_timestamp, n_latest):
    """
    Get the N-latest generated file with the provided pattern in the provided folder.
    :param folder_path: Path of the folder where the file is located
    :param pattern: Pattern of the file to match
    :param use_timestamp: Use timestamp when matching
    :param n_latest: How many latest files to return (1 = just the latest, 2 = latest & second latest, etc.)
    :return: The latest generated file and its timestamp
    """
    files = []
    for fname in os.listdir(folder_path):
        if pattern and not re.match(pattern, fname):
            continue

        full_path = os.path.join(folder_path, fname)
        if not os.path.isfile(full_path):
            continue

        if use_timestamp:
            match = re.match(pattern, fname)
            if match:
                ts_str = match.group(1)
                ts = dt.datetime.strptime(ts_str, "%Y%m%dT%H-%M-%S")
                files.append((ts, ts_str, os.path.splitext(full_path)[0]))
        else:
            ts = dt.datetime.fromtimestamp(os.path.getmtime(full_path))
            files.append((ts, None, os.path.splitext(full_path)[0]))

    files.sort(key=lambda x: x[0], reverse=True)

    latest_files = files[:n_latest]

    result = []
    for f in latest_files:
        ts, ts_str, fpath = f
        scenario_name = None
        match = re.match(r"DataContainer_Sc_(.*)", os.path.basename(fpath))
        if match:
            scenario_name = match.group(1)
        result.append((ts, ts_str, fpath, scenario_name))

    return result


def count_files_in_folder(folder_path):
    """
    Count the number of files in a specific folder.
    :param folder_path: Path of the folder
    :return: Number of files in the folder
    """
    return sum(1 for fname in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, fname)))


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
TIMBADIR_INPUT = TIMBADIR / Path("TiMBA") / Path("data") / Path("input") / Path("01_Input_Files")
TIMBADIR_OUTPUT = TIMBADIR / Path("TiMBA") / Path("data") / Path("output")
INPUT_FOLDER = PACKAGEDIR / Path("data") / Path("input")

if user_input[ParamNames.add_on_activated.value] or not cmodule_is_standalone():
    # input paths for add-on c-module
    AO_RESULTS_INPUT_PATTERN = r"results_D(\d{8}T\d{2}-\d{2}-\d{2})_.*"
    AO_FOREST_INPUT_PATTERN = r"forest_D(\d{8}T\d{2}-\d{2}-\d{2})_.*"
    AO_PKL_RESULTS_INPUT_PATTERN = r"DataContainer_Sc_.*"

    n_sc_files = count_files_in_folder(TIMBADIR_INPUT)

    datetime, latest_timestamp_results, latest_result_input = get_latest_file(folder_path=TIMBADIR_OUTPUT,
                                                                              pattern=AO_RESULTS_INPUT_PATTERN,
                                                                              use_timestamp=True,
                                                                              n_latest=n_sc_files)
    datetime, latest_timestamp_results, latest_forest_input = get_latest_file(folder_path=TIMBADIR_OUTPUT,
                                                                              pattern=AO_FOREST_INPUT_PATTERN,
                                                                              use_timestamp=True,
                                                                              n_latest=n_sc_files)
    datetime, latest_timestamp, latest_pkl_input, sc_name = get_latest_file(folder_path=TIMBADIR_OUTPUT,
                                                                            pattern=AO_PKL_RESULTS_INPUT_PATTERN,
                                                                            use_timestamp=False,
                                                                            n_latest=n_sc_files)
    RESULTS_INPUT = latest_result_input
    FOREST_INPUT = latest_forest_input
    PKL_RESULTS_INPUT = latest_pkl_input

    # output paths for add-on c-module
    OUTPUT_FOLDER = TIMBADIR_OUTPUT
    PKL_UPDATED_TIMBA_OUTPUT = latest_pkl_input
    PKL_CARBON_OUTPUT = OUTPUT_FOLDER / Path(f"c_module_output_{latest_timestamp_results}")
    PKL_CARBON_OUTPUT_AGG = OUTPUT_FOLDER / Path(f"carbon_results_agg_{latest_timestamp_results}")
    SC_NAME = sc_name

else:
    # input paths for standalone c-module
    RESULTS_INPUT = INPUT_FOLDER / Path("default_Sc_results")
    FOREST_INPUT = INPUT_FOLDER / Path("default_Sc_forest")
    PKL_RESULTS_INPUT = list(INPUT_FOLDER.glob("default_Sc_results_*.pkl"))

    # output paths for standalone c-module
    OUTPUT_FOLDER = PACKAGEDIR / Path("data") / Path("output")
    PKL_UPDATED_TIMBA_OUTPUT = OUTPUT_FOLDER / Path("updated_timba_output")
    PKL_CARBON_OUTPUT = OUTPUT_FOLDER / Path("c_module_output_D")
    PKL_CARBON_OUTPUT_AGG = OUTPUT_FOLDER / Path("carbon_results_agg_D")


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
