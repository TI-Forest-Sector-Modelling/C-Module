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
    folder = Path(folder_path)
    regex = re.compile(pattern)
    files = []

    for fname in os.listdir(folder):
        full_path = folder / fname
        if not full_path.is_file():
            continue

        match = regex.match(fname)
        if not match:
            continue

        if use_timestamp:
            ts_str = match.group(1)
            ts = dt.datetime.strptime(ts_str, "%Y%m%dT%H-%M-%S")
        else:
            ts = dt.datetime.fromtimestamp(full_path.stat().st_mtime)
            ts_str = ts.strftime("%Y%m%dT%H-%M-%S")

        files.append((ts, ts_str, full_path))

    # Sort newest first
    files.sort(key=lambda x: x[0], reverse=True)
    latest = files[:n_latest]

    # Split into lists
    paths = [f[2] for f in latest]  # Path objects
    timestamps = [f[1] for f in latest]  # string representation

    return paths, timestamps


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

    n_sc_files = count_files_in_folder(TIMBADIR_INPUT)

    latest_result_input, latest_timestamp_results = get_latest_file(folder_path=TIMBADIR_OUTPUT,
                                                                    pattern=AO_RESULTS_INPUT_PATTERN,
                                                                    use_timestamp=True,
                                                                    n_latest=n_sc_files)
    latest_forest_input, latest_timestamp_results = get_latest_file(folder_path=TIMBADIR_OUTPUT,
                                                                    pattern=AO_FOREST_INPUT_PATTERN,
                                                                    use_timestamp=True,
                                                                    n_latest=n_sc_files)
    latest_pkl_input, latest_timestamp = get_latest_file(folder_path=TIMBADIR_OUTPUT,
                                                         pattern=AO_PKL_RESULTS_INPUT_PATTERN,
                                                         use_timestamp=False,
                                                         n_latest=n_sc_files)
    RESULTS_INPUT = latest_result_input
    FOREST_INPUT = latest_forest_input
    PKL_RESULTS_INPUT = latest_pkl_input

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
