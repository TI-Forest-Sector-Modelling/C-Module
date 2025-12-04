import datetime as dt
from pathlib import Path
from c_module.user_io.default_parameters import user_input
from c_module.parameters.defines import ParamNames, PathNames

current_dt = dt.datetime.now().strftime("%Y%m%dT%H-%M-%S")


def extract_scenarios(input_folder, output_folder, sc_num):
    """
    Extract scenario names from Excel files in a folder and merge them with 'DataContainer_Sc_' prefix.
    :param input_folder: Path to the folder containing scenario files.
    :param output_folder: Path to the folder where the output files will be stored.
    :param sc_num: Number of scenarios to extract.
    :return: List of merged scenario names.
    """
    folder_path = Path(output_folder)
    files = list(folder_path.glob("*.pkl"))
    files.sort(key=lambda f: f.stat().st_mtime)
    if sc_num is None:
        folder_path = Path(input_folder)
        try:
            sc_num = len(list(folder_path.glob("*.xlsx")))
        except FileNotFoundError:
            sc_num = 1
        files = files[-sc_num:]
    else:
        files = files[-user_input[ParamNames.sc_num.value]:]

    scenarios = files

    return scenarios


def cmodule_is_standalone(debug: bool = False) -> bool:
    """
    Check if cmodule is standalone or not, covering if the code is run as the main program, covering CLI, script, IDE,
     and entry point runs.
    :param debug: Flag to enable debug mode.
    :return: Bool if cmodule is standalone or not.
    """
    import sys
    import inspect
    import __main__

    reasons = []

    # Running under a typical test runner => treat as imported
    if "pytest" in sys.modules:
        reasons.append("pytest detected in sys.modules")
        if debug:
            print("DEBUG: pytest present -> treated as imported")
        return True
    if any("unittest" in mod for mod in sys.modules):
        reasons.append("unittest detected in sys.modules")
        if debug:
            print("DEBUG: unittest present -> treated as imported")
        return True

    # Simple and reliable check for most cases
    if __name__ == "__main__":
        reasons.append("__name__ == '__main__'")
        if debug:
            print("DEBUG: __name__ == '__main__' -> standalone")
        return True

    # Inspect stack: some IDEs or runners execute a wrapper that sets __name__ == '__main__'
    # in a different frame. If any frame was executed as __main__, assume standalone entry.
    for frame_info in inspect.stack():
        g = frame_info.frame.f_globals
        frame_name = g.get("__name__")
        frame_file = g.get("__file__", None)
        if frame_name == "__main__":
            reasons.append(f"found frame with __name__ == '__main__' (file={frame_file})")
            if debug:
                print("DEBUG: stack frame with __name__ == '__main__' -> standalone")
                print(f"DEBUG: frame file: {frame_file}")
            return True

    # Compare the top-level script path with this package path:
    # if the top-level entry script is outside this package, it likely invoked/imported the package.
    main_file = getattr(__main__, "__file__", None)
    if main_file:
        try:
            main_path = Path(main_file).resolve()
            package_root = Path(__file__).resolve().parents[1]
            # If the top-level script is the module file itself -> standalone
            if main_path == Path(__file__).resolve():
                reasons.append("main_file equals this module file")
                if debug:
                    print("DEBUG: main_file equals this module file -> standalone")
                return True
            # If the top-level script is *inside* the package: often still a standalone run (python -m)
            if package_root in main_path.parents:
                reasons.append("main_file is located inside package root (likely -m or IDE module run)")
                if debug:
                    print("DEBUG: main_file inside package root -> standalone")
                    print(f"DEBUG: main_file={main_path}, package_root={package_root}")
                return True
            # Otherwise treat as imported
            reasons.append("main_file exists but is outside package -> treated as imported")
            if debug:
                print("DEBUG: main_file outside package -> treated as imported")
                print(f"DEBUG: main_file={main_path}, package_root={package_root}")
            return False
        except Exception as e:
            # fallback
            if debug:
                print("DEBUG: error resolving main_file or package_root:", e)
            pass

    # If none of the above matched, assume imported
    if debug:
        print("DEBUG: no indication of standalone execution; reasons:", reasons)
    return False


def set_paths(user_input: dict) -> dict:
    PACKAGEDIR = Path(__file__).parent.parent.absolute()

    if cmodule_is_standalone(debug=False):
        if user_input[ParamNames.add_on_activated.value]:
            import sys
            print("Inconsistent settings:")
            print(f"C-Module is executed as standalone: {cmodule_is_standalone(debug=False)}")
            print(f"But parameter add_on_activated: {user_input[ParamNames.add_on_activated.value]}")
            print(f"Harmonize settings to proceed")
            sys.exit("Stopping execution.")

    if user_input[ParamNames.add_on_activated.value] or not cmodule_is_standalone(debug=False):
        # input and output paths for add-on c-module
        if user_input[ParamNames.folderpath.value] is None:
            # If user-defined path does not exists, use default path
            # For compatibility with other modules, paths must be adapted
            TIMBADIR = Path(__file__).parent.parent.parent.parent.parent.parent.absolute()
            TARGETDIR = TIMBADIR
        else:
            # If user-defined path exist
            USER_PATH = Path(user_input[ParamNames.folderpath.value]).absolute()
            TARGETDIR = USER_PATH

        TIMBADIR_INPUT = TARGETDIR / Path("TiMBA") / Path("data") / Path("input") / Path("01_Input_Files")
        TIMBADIR_OUTPUT = TARGETDIR / Path("TiMBA") / Path("data") / Path("output") / Path("data")

        INPUT_FOLDER = PACKAGEDIR / Path("data") / Path("input")
        OUTPUT_FOLDER = TIMBADIR_OUTPUT

    else:
        # input and output paths for standalone c-module
        if user_input[ParamNames.folderpath.value] is None:
            TARGETDIR = PACKAGEDIR
        else:
            USER_PATH = Path(user_input[ParamNames.folderpath.value]).absolute()
            TARGETDIR = USER_PATH

        TIMBADIR_INPUT = None
        TIMBADIR_OUTPUT = None

        INPUT_FOLDER = TARGETDIR / Path("data") / Path("input")
        OUTPUT_FOLDER = TARGETDIR / Path("data") / Path("output")

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
        PathNames.TIMBADIR_INPUT.value: TIMBADIR_INPUT,
        PathNames.TIMBADIR_OUTPUT.value: TIMBADIR_OUTPUT,
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