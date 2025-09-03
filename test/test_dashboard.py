import unittest
from unittest.mock import patch
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dash.testing.application_runners import ThreadedRunner


from c_module.logic.visualisation import Carbon_DashboardPlotter
from c_module.parameters.defines import VarNames

# Sample dummy data for testing
data = pd.DataFrame({
    VarNames.year_name.value: [2020, 2025, 2020, 2025, 2020, 2025],
    VarNames.ISO3.value: ["DEU", "DEU", "FRA", "FRA", "POL", "POL"],
    VarNames.output_variable.value: ["CarbonForestBiomass", "CarbonForestBiomass", "CarbonForestBiomass",
                                     "CarbonForestBiomass", "CarbonForestBiomass", "CarbonForestBiomass"],
    VarNames.scenario.value: ["A", "A", "A", "A", "A", "A"],
    VarNames.carbon_stock.value: [100, 240, 400, 230, 30, 48],
    VarNames.carbon_stock_chg.value: [0, 140, 0, -170, 0, 18],
    VarNames.carbon_region.value: ["Central Europe", "Central Europe", "Western Europe", "Western Europe",
                                   "Central Europe", "Central Europe",],
    VarNames.continent.value: ["Europe", "Europe", "Europe", "Europe", "Europe", "Europe"],
})


class TestCallbacks(unittest.TestCase):
    def setUp(self):
        self.dashboard = Carbon_DashboardPlotter(data=data)
        self.pool_colors = self.dashboard.get_colors()

    def test_update_plot_carbon(self):
        stacked_fig, world_map = self.dashboard.update_plot_carbon(continent=["Europe"],
                                                                   region=["Central Europe", "Western Europe"],
                                                                   country=["DEU", "FRA"],
                                                                   variable=["CarbonForestBiomass"],
                                                                   scenario=["A", "B"],
                                                                   value_type_1="absolute",
                                                                   stock_type_1="carbon stock",
                                                                   value_type_2="absolute",
                                                                   stock_type_2="carbon stock",
                                                                   year_range=[2020, 2025],
                                                                   pool_colors=self.pool_colors)
        self.assertIn("data", world_map.to_dict())
        self.assertGreater(len(world_map.data), 0)
        self.assertIn("layout", stacked_fig.to_dict())
        self.assertEqual(stacked_fig.layout.barmode, "relative")


class TestLayout(unittest.TestCase):
    def setUp(self):
        self.dashboard = Carbon_DashboardPlotter(data=data)
        self.app = self.dashboard.app

    def test_layout_contains_graphs(self):
        layout_str = str(self.app.layout)
        self.assertIn("carbon-world-map", layout_str)
        self.assertIn("carbon-stacked-area-chart", layout_str)

    def test_layout_contains_dropdowns(self):
        layout_str = str(self.app.layout)
        self.assertIn("continent-dropdown", layout_str)
        self.assertIn("region-dropdown", layout_str)
        self.assertIn("country-dropdown", layout_str)
        self.assertIn("scenario-dropdown", layout_str)
        self.assertIn("btn_csv", layout_str)
        self.assertIn("year-range-slider", layout_str)
        self.assertIn("value-type-dropdown-1", layout_str)
        self.assertIn("stock-type-dropdown-1", layout_str)
        self.assertIn("value-type-dropdown-2", layout_str)
        self.assertIn("stock-type-dropdown-2", layout_str)


class DashboardIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Configure headless Chrome with webdriver-manager."""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--remote-debugging-port=9222")

        # Use webdriver-manager to auto-install chromedriver
        cls.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.patcher = patch("webbrowser.open_new", lambda url: None)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        # Import the dashboard app dynamically
        self.dashboard = Carbon_DashboardPlotter(data=data)
        self.app = self.dashboard.app

        self.runner = ThreadedRunner()
        self.runner.start(self.app)

        self.base_url = self.runner.url
        assert self.base_url is not None

    def test_app_launches(self):
        """Verify the dashboard starts and title is correct."""
        self.driver.get(self.base_url)
        dropdown = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "value-type-dropdown-2"))
        )
        self.assertIsNotNone(dropdown)

    def test_dropdowns_exist(self):
        """Verify dropdowns are rendered."""
        self.driver.get(self.base_url)

        # Wait for dropdowns
        value_type_dropdown = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "value-type-dropdown-2"))
        )
        stock_type_dropdown = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "stock-type-dropdown-2"))
        )

        self.assertIsNotNone(value_type_dropdown)
        self.assertIsNotNone(stock_type_dropdown)

    def test_dropdown_interaction_updates_graph(self):
        """Select 'shares' in value-type dropdown and verify map updates."""
        self.driver.get(self.base_url)

        # Wait for the dropdown
        value_type_dropdown = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.ID, "value-type-dropdown-2"))
        )
        value_type_dropdown.click()

        # Wait for the option with text 'shares' to appear anywhere in DOM
        option_shares = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[contains(@class,'VirtualizedSelectOption') and text()='shares']"))
        )
        option_shares.click()

        # Wait for the map graph to update
        map_graph = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "carbon-world-map"))
        )

        self.assertIsNotNone(map_graph)


if __name__ == "__main__":
    unittest.main()



