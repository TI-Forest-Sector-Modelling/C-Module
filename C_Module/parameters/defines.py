from enum import Enum

class CarbonConstants(Enum):
    """
    Class to hold constants
    """
    MIO_FACTOR = 1000
    CO2_FACTOR = round(44 / 12, 3)
    CARBON_MIO_FACTOR = 1000000
    CARBON_TSD_FACTOR = 1000

class CountryConstants(Enum):
    """

    """
    FAO_REGION_CODE = 5000

class VarNames(Enum):
    """
    Class to hold names of variables
    """
    # TiMBA data
    timba_data_forest = "Forest"
    timba_data_all = "data_periods"
    region_code = "RegionCode"
    commodity_code = "CommodityCode"
    commodity_name = "CommodityName"
    dummy_region = "zy"
    year_name = "Year"
    data_aligned = "data_aligned"

    # Additonal data
    timba_country_name = "TiMBA Area"
    timba_country_code = "TiMBA Area Code"
    ISO3 = "ISO3 Code"
    fao_country_name = "Area Name"
    fao_country_code = "Area Code"
    continent = "ContinentNew"
    carbon_region = "Carbon Region"

    country_data = "country_data"
    commodity_dict = "commodity"
    commodity_data = "commodity_data"
    commodity_num = "commodity_num"

    # Additional carbon data
    carbon_forest_biomass = "CarbonForestBiomass"
    carbon_forest_biomass_chg = "CarbonChangeForestBiomass"
    carbon_hwp = "CarbonHWP"
    carbon_agb = "CarbonAboveGround"
    carbon_bgb = "CarbonBelowGround"
    carbon_dw = "CarbonDeadWood"
    carbon_dwl = "CarbonDWL"
    carbon_dwl_chg = "CarbonChangeDWL"
    carbon_litter = "CarbonLitter"
    carbon_soil = "CarbonSoil"
    carbon_soil_chg = "CarbonChangeSoil"
    carbon_subsitution = "CarbonSubstitution"
    carbon_total = "CarbonTotal"
    carbon_density_avg = "carbon_average"
    carbon_density_avg_rand = "rand_carbon_average"


    # FAOSTAT data
    faostat_item_code = "Item Code"
    faostat_item_name = "Item"
    faostat_element_name = "Element"
    faostat_element_code = "Element Code"





