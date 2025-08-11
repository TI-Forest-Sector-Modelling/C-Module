from tmp_folder.logic.main import C_Module
from tmp_folder.user_io.default_parameters import user_input


if __name__ == "__main__":
    c_module = C_Module(UserInput=user_input)
    c_module.run()

