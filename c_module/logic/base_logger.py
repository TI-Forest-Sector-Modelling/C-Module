from typing import Union
import os
from pathlib import Path
import datetime as dt
import logging
from c_module.parameters.paths import LOGGING_OUTPUT_FOLDER


def get_logger(user_path: Union[str, Path, None], add_on_activated: bool):
    current_dt = dt.datetime.now().strftime("%Y%m%d")
    if add_on_activated:
        filename = f"{current_dt}_TiMBA.log"
    else:
        filename = rf"{current_dt}_C_Module.log"

    if user_path is None:
        filepath = os.path.join(LOGGING_OUTPUT_FOLDER, filename)
    else:
        filepath = os.path.join(user_path, "output", filename)
    if not os.path.exists(filepath):
        os.makedirs(Path(filepath).parent, exist_ok=True)

    if add_on_activated:
        Logger = logging.getLogger("TiMBA")
    else:
        Logger = logging.getLogger("C-Module")
    if not Logger.hasHandlers():
        Logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(lineno)s: %(message)s',
            '%d.%m.%y %H:%M:%S'
        )
        handler = logging.FileHandler(filepath, 'a+')
        handler.setFormatter(formatter)
        Logger.addHandler(handler)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(name)-10s: %(levelname)-10s %(message)s')
        console.setFormatter(console_formatter)
        Logger.addHandler(console)
    return Logger
