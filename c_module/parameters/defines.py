from enum import Enum


class CarbonConstants(Enum):
    """
    Class to hold constants
    """
    MIO_FACTOR = 1000
    CO2_FACTOR = round(44 / 12, 3)
    CARBON_MIO_FACTOR = 1000000
    CARBON_TSD_FACTOR = 1000
    NON_ZERO_PARAMETER = 0.0000000001


class CountryConstants(Enum):
    """

    """
    FAO_REGION_CODE = 5000


class ParamNames(Enum):
    """
    Class to hold names of parameters set by users
    """
    add_on_activated = "activate_add_on_cmodule"
    start_year = "start_year"
    end_year = "end_year"
    read_in_pkl = "read_in_pkl"
    save_data_as = "save_data_as"
    calc_c_forest_agb = "calc_c_forest_agb"
    calc_c_forest_bgb = "calc_c_forest_bgb"
    calc_c_forest_soil = "calc_c_forest_soil"
    calc_c_forest_dwl = "calc_c_forest_dwl"
    calc_c_hwp = "calc_c_hwp"
    c_hwp_accounting_approach = "c_hwp_accounting_approach"
    historical_c_hwp = "historical_c_hwp"
    hist_hwp_start_year = "hist_hwp_start_year"
    hist_hwp_start_year_default = "hist_hwp_start_year_default"
    show_carbon_dashboard = "show_carbon_dashboard"


class VarNames(Enum):
    """
    Class to hold names of variables
    """
    # TiMBA data
    timba_data_forest = "Forest"
    timba_data_all = "data_periods"
    timba_data_carbon = "Carbon"
    timba_data_carbon_flat = "Carbon_flat"
    region_code = "RegionCode"
    commodity_code = "CommodityCode"
    commodity_name = "CommodityName"
    domain_name = "domain"
    quantity_col = "quantity"
    dummy_region = "zy"
    year_name = "year"
    period_var = "Period"
    data_aligned = "data_aligned"
    data = "data"
    supply_var = "Supply"
    import_var = "TransportationImport"
    export_var = "TransportationExport"
    production_var = "ManufactureCost"
    forest_stock_var = "ForStock"
    forest_area_var = "ForArea"

    # Additonal data
    timba_country_name = "TiMBA Area"
    timba_country_code = "RegionCode"
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
    carbon_hwp_chg = "CarbonChangeHWP"
    carbon_hwp_inflow = "CarbonInflowHWP"
    carbon_sawnwood = "Carbon_sawnwood"
    carbon_wood_based_panels = "Carbon_wood-based panels"
    carbon_paper_and_paperboard = "Carbon_paper and paperboard"
    carbon_agb = "CarbonAboveGround"
    carbon_bgb = "CarbonBelowGround"
    carbon_dw = "CarbonDeadWood"
    carbon_dwl = "CarbonDWL"
    carbon_dwl_chg = "CarbonChangeDWL"
    carbon_litter = "CarbonLitter"
    carbon_soil = "CarbonSoil"
    carbon_soil_chg = "CarbonChangeSoil"
    carbon_substitution = "CarbonSubstitution"
    material_substitution = "MaterialSubstitution"
    energy_substitution = "EnergySubstitution"
    total_substitution = "TotalSubstitution"
    total_substitution_chg = "TotalChangeSubstitution"
    carbon_total = "CarbonTotal"
    carbon_total_chg = "CarbonChangeTotal"
    carbon_density_avg = "carbon_average"
    carbon_density_avg_rand = "rand_carbon_average"
    carbon_factor = "Carbon_factor"
    half_life = "Half_life"
    displacement_factor = "Displacement_factor"
    share_domestic_feedstock = "share domestic feedstock"
    hwp_category = "hwp_category"
    start_year = "start year"
    production_approach = "production"
    stock_change_approach = "stock-change"
    output_variable = "Variable"
    carbon_stock = "carbon stock"
    carbon_stock_chg = "carbon stock change"
    all_scenarios = "all_sc"
    scenario = "scenario"

    # FAOSTAT data
    faostat_item_code = "Item Code"
    faostat_item_name = "Item"
    faostat_element_name = "Element"
    faostat_element_code = "Element Code"
    faostat_year = "Year"
    faostat_production = "Production"
    faostat_domestic_consumption = "Domestic consumption"
    faostat_production_domestic_feedstock = "Production domestic feedstock"
    faostat_import = "Import quantity"
    faostat_export = "Export quantity"
    faostat_import_value = "Import value"
    faostat_export_value = "Export value"







