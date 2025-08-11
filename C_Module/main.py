from c_module.logic.main import C_Module
from c_module.user_io.default_parameters import user_input


if __name__ == "__main__":
    c_module = C_Module(UserInput=user_input)
    c_module.run()

