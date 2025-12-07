import datetime as dt
from pathlib import Path
from c_module.user_io.default_parameters import user_input
from c_module.parameters.defines import ParamNames, PathNames

current_dt = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")


def extract_scenarios(output_folder, sc_num):
    """
    Extract scenario names from Excel files in a folder and merge them with 'DataContainer_Sc_' prefix.
    :param output_folder: Path to the folder where the output files will be stored.
    :param sc_num: Number of scenarios to extract.
    :return: List of merged scenario names.
    """
    folder_path = Path(output_folder)
    files = list(folder_path.glob("*.pkl"))
    files.sort(key=lambda f: f.stat().st_mtime)
    if sc_num is None:
        folder_path = Path(output_folder)
        try:
            sc_num = len(list(folder_path.glob("*.pkl")))
        except FileNotFoundError:
            sc_num = 1
        files = files[-sc_num:]
    else:
        files = files[-user_input[ParamNames.sc_num.value]:]

    scenarios = files

    return scenarios


def set_paths(user_input: dict) -> dict:
    """
    Set paths dynamically based on user input.
    :param user_input: dictionary with user input.
    :return: dictionary of paths.
    """
    PACKAGEDIR = Path(__file__).parent.parent.absolute()

    if user_input["input_folder_path"] is None:
        # take standard paths from the package
        INPUT_FOLDER = PACKAGEDIR / Path("data") / Path("input")
    else:
        # take paths as defined by the user
        INPUT_FOLDER = Path(user_input["input_folder_path"]).absolute()
    if user_input["output_folder_path"] is None:
        # take standard paths from the package
        OUTPUT_FOLDER = PACKAGEDIR / Path("data") / Path("output")
    else:
        # take paths as defined by the user
        OUTPUT_FOLDER = Path(user_input["output_folder_path"]).absolute()

    # Official statistics from the Food and Agriculture Organization
    FAO_DIR = INPUT_FOLDER / Path("historical_data")
    FAOSTAT_URL = "https://bulks-faostat.fao.org/production/Forestry_E_All_Data.zip"
    FAOSTAT_DATA = INPUT_FOLDER / Path("historical_data") / Path("Forestry_E_All_Data_NOFLAG")
    FRA_URL = "https://fra-data.fao.org/api/file/bulk-download?assessmentName=fra&cycleName=2020&countryIso=WO"
    FRA_DATA = INPUT_FOLDER / Path("historical_data") / Path(f"FRA_Years_All_Data")

    # additional information
    CMODULE_ZIP_URL = "https://github.com/TI-Forest-Sector-Modelling/C-Module/archive/refs/heads/main.zip"
    ADD_INFO_DIR = "C-Module-main/c_module/data/input/additional_information"
    ADD_INFO_FOLDER = PACKAGEDIR / INPUT_FOLDER / Path("additional_information")
    ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
    PKL_ADD_INFO_CARBON_PATH = ADD_INFO_FOLDER / Path("carbon_additional_information")
    ADD_INFO_COUNTRY = ADD_INFO_FOLDER / Path("country_data")
    PKL_ADD_INFO_START_YEAR = ADD_INFO_FOLDER / Path("hist_hwp_carbon_start_year")
    DEFAULT_PROJECTION_DIR = "C-Module-main/c_module/data/input/projection_data"

    LOGGING_OUTPUT_FOLDER = OUTPUT_FOLDER

    path_dict = {
        PathNames.INPUT_FOLDER.value: INPUT_FOLDER,
        PathNames.OUTPUT_FOLDER.value: OUTPUT_FOLDER,
        PathNames.FAO_DIR.value: FAO_DIR,
        PathNames.FAOSTAT_URL.value: FAOSTAT_URL,
        PathNames.FAOSTAT_DATA.value: FAOSTAT_DATA,
        PathNames.FRA_URL.value: FRA_URL,
        PathNames.FRA_DATA.value: FRA_DATA,
        PathNames.CMODULE_ZIP_URL.value: CMODULE_ZIP_URL,
        PathNames.ADD_INFO_DIR.value: ADD_INFO_DIR,
        PathNames.ADD_INFO_FOLDER.value: ADD_INFO_FOLDER,
        PathNames.ADD_INFO_CARBON_PATH.value: ADD_INFO_CARBON_PATH,
        PathNames.PKL_ADD_INFO_CARBON_PATH.value: PKL_ADD_INFO_CARBON_PATH,
        PathNames.ADD_INFO_COUNTRY.value: ADD_INFO_COUNTRY,
        PathNames.PKL_ADD_INFO_START_YEAR.value: PKL_ADD_INFO_START_YEAR,
        PathNames.DEFAULT_PROJECTION_DIR.value: DEFAULT_PROJECTION_DIR,
        PathNames.LOGGING_OUTPUT_FOLDER.value: LOGGING_OUTPUT_FOLDER
    }
    return path_dict

