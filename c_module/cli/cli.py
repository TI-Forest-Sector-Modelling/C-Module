import click
from c_module.logic.main import C_Module
from c_module.user_io.default_parameters import user_input
from c_module.parameters.defines import ParamNames


@click.command()
@click.option('-ADD_ON', '--add_on_activated', "add_on_activated",
              default=user_input[ParamNames.add_on_activated.value], show_default=True, required=True, type=bool,
              help="Flag to use the carbon module as a standalone module or as a TiMBA add-on.")
@click.option('-SY', '--start_year', 'start_year', default=user_input[ParamNames.start_year.value],
              show_default=True, required=True, type=int,
              help="Start year of carbon calculations.")
@click.option('-EY', '--end_year', 'end_year', default=user_input[ParamNames.end_year.value],
              show_default=True, required=True, type=int,
              help="End year of carbon calculations.")
@click.option('-CF_AGB', '--calc_c_forest_agb', "calc_c_forest_agb",
              default=user_input[ParamNames.calc_c_forest_agb.value], show_default=True, required=True, type=bool,
              help="Flag to activate carbon calculation for aboveground forest biomass.")
@click.option('-CF_BGB', '--calc_c_forest_bgb', "calc_c_forest_bgb",
              default=user_input[ParamNames.calc_c_forest_bgb.value], show_default=True, required=True, type=bool,
              help="Flag to activate carbon calculation for belowground forest biomass.")
@click.option('-CF_S', '--calc_c_forest_soil', "calc_c_forest_soil",
              default=user_input[ParamNames.calc_c_forest_soil.value], show_default=True, required=True, type=bool,
              help="Flag to activate carbon calculation for forest soil.")
@click.option('-CF_DWL', '--calc_c_forest_dwl', "calc_c_forest_dwl",
              default=user_input[ParamNames.calc_c_forest_dwl.value], show_default=True, required=True, type=bool,
              help="Flag to activate carbon calculation for dead wood and litter.")
@click.option('-C_HWP', '--calc_c_hwp', "calc_c_hwp",
              default=user_input[ParamNames.calc_c_hwp.value], show_default=True, required=True, type=bool,
              help="Flag to activate carbon calculation for harvested wood products.")
@click.option('-C_HWP_A', '--c_hwp_accounting_approach', "c_hwp_accounting_approach",
              default=user_input[ParamNames.c_hwp_accounting_approach.value], show_default=True, required=True,
              type=str, help="Flag to select the accounting approach for carbon in harvested wood products.")
@click.option('-R', '--read_in_pkl', "read_in_pkl",
              default=user_input[ParamNames.read_in_pkl.value], show_default=True, required=True, type=bool,
              help="Flag to control if pkl- or csv-files are read; reads in if True.")
@click.option('-SD', '--show_carbon_dashboard', 'show_carbon_dashboard',
              default=user_input[ParamNames.show_carbon_dashboard.value], show_default=True, required=False, type=bool,
              help="Flag to launch carbon dashboard.")
def cli(add_on_activated, start_year, end_year, calc_c_forest_agb, calc_c_forest_bgb, calc_c_forest_soil,
        calc_c_forest_dwl, calc_c_hwp, c_hwp_accounting_approach, read_in_pkl, show_carbon_dashboard):

    user_input_cli = {
        ParamNames.add_on_activated.value: add_on_activated,
        ParamNames.start_year.value: start_year,
        ParamNames.end_year.value: end_year,
        ParamNames.read_in_pkl.value: read_in_pkl,
        ParamNames.calc_c_forest_agb.value: calc_c_forest_agb,
        ParamNames.calc_c_forest_bgb.value: calc_c_forest_bgb,
        ParamNames.calc_c_forest_soil.value: calc_c_forest_soil,
        ParamNames.calc_c_forest_dwl.value: calc_c_forest_dwl,
        ParamNames.calc_c_hwp.value: calc_c_hwp,
        ParamNames.c_hwp_accounting_approach.value: c_hwp_accounting_approach,
        ParamNames.show_carbon_dashboard.value: show_carbon_dashboard,
        # Adavanced settings not available via CLI
        ParamNames.historical_c_hwp.value: user_input[ParamNames.historical_c_hwp.value],
        ParamNames.hist_hwp_start_year.value: user_input[ParamNames.hist_hwp_start_year.value],
        ParamNames.hist_hwp_start_year_default.value: user_input[ParamNames.hist_hwp_start_year_default.value],
    }

    c_module = C_Module(UserInput=user_input_cli)
    c_module.run()


if __name__ == '__main__':
    cli()
