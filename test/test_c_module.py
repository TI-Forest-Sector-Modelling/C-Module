import unittest

from c_module.logic.main import C_Module
from c_module.user_io.default_parameters import user_input
from c_module.parameters.defines import ParamNames


class TestCModuleClass(unittest.TestCase):

    def test_cmodule_run(self):
        c_module = C_Module(UserInput=user_input)
        c_module.UserInput[ParamNames.show_carbon_dashboard.value] = False
        c_module.run()


if __name__ == '__main__':
    unittest.main()
