import unittest

from tmp_folder.logic.main import C_Module
from tmp_folder.user_io.default_parameters import user_input


class TestCModuleClass(unittest.TestCase):

    def test_cmodule_run(self):
        c_module = C_Module(UserInput=user_input)
        c_module.run()


if __name__ == '__main__':
    unittest.main()
