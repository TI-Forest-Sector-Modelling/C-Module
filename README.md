![C-Module_Logo](https://github.com/TI-Forest-Sector-Modelling/C-Module/blob/main/assets/C-Module_Logo_transparent_v1.png?raw=true)

------
[![CI - Test](https://github.com/TI-Forest-Sector-Modelling/C-Module/actions/workflows/actions.yml/badge.svg)](https://github.com/TI-Forest-Sector-Modelling/C-Module/actions/workflows/actions.yml)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=TI-Forest-Sector-Modelling_C-Module&metric=coverage)](https://sonarcloud.io/summary/new_code?id=TI-Forest-Sector-Modelling_C-Module)
![GitHub Release](https://img.shields.io/github/v/release/TI-Forest-Sector-Modelling/C-Module)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16884230.svg)](https://doi.org/10.5281/zenodo.16884230)
[![License](https://img.shields.io/github/license/TI-Forest-Sector-Modelling/C-Module)](https://github.com/TI-Forest-Sector-Modelling/C-Module/blob/main/COPYING)
------
<!-- TOC -->

- [Cite the C-Module](#cite-the-c-module)
- [Install the C-Module](#install-the-c-module)
  - [Double check installation](#doublecheck-installation)
  - [Test suite and coverage](#test-suite-and-coverage-report)
- [Use the C-Module](#use-the-c-module)
  - [Module settings](#module-settings)
    - [Settings as parameters](#settings-as-parameters)
    - [Advanced settings](#advanced-settings)
  - [Carbon dashboard](#carbon-dashboard)
- [Extended module description](#extended-module-description)
- [Roadmap and project status](#roadmap-and-project-status)
- [Contributing to the project](#contributing-to-the-project)
- [Authors](#authors)
- [Contribution statement](#contribution-statement)
- [License and Copyright Note](#license-and-copyright-note)
- [Acknowledgements](#acknowledgements)
- [References](#references)

<!-- /TOC -->

# C-Module

The Carbon Module (C-Module) monitors global carbon stocks and their changes across the forestry sector’s key carbon pools,
drawing on either forest sector projections or historical statistics. In its current version, the module quantifies carbon
stocks and stock changes in forest biomass (above- and below-ground), harvested wood products (HWP), forest soils, dead wood,
and litter for 180 countries.
Substitution effects associated with the use of harvested wood products (HWP) are also quantified. The estimation of carbon
in forest biomass, forest soils, and dead wood and litter follows the methodologies described in Johnston et al. (2019) and
Johnston & Radeloff (2019). Carbon in HWP is quantified using the IPCC Tier 1 approach (IPCC 2019). Additional mathematical
details are provided in [Honkomp (in prep)](#todo).

The C-Module can be used in two modes: either as an add-on to the Timber market Model for policy-Based Analysis ([TiMBA](#https://github.com/TI-Forest-Sector-Modelling/TiMBA))
or as a standalone module (see [Use the C-Module](#use-the-c-module)).

## Cite the C-Module

We are happy that you use the C-Module for your research. When publishing your work in articles, working paper, presentations
or elsewhere, please cite the module as: 

[Honkomp (2025) C-Module v1](CITATION.cff)

## Install the C-Module

The package is developed and tested with Python 3 (Python 3.12.6) version on Windows. Further, the module's functionality
is tested using GitHub Actions for Python 3.9, 3.10, 3.11 with the latest Windows, Ubuntu, and macOS operating systems. 
Using the C-Module with other Python versions or OS might alter the functionality and the results of the module.   
If the C-Module is used as an add-on module of TiMBA, the C-Module will be installed automatically via the requirements of TiMBA.

The following steps apply if the C-Module is used as a standalone module.
Before proceeding, please ensure that Python is installed on your system. It can be downloaded and installed 
from [Python.org](https://www.python.org/downloads/release/python-389/).

1. Clone the repository   
Begin by cloning the repository to your local machine using the following command: 
    >git clone https://github.com/TI-Forest-Sector-Modelling/C-Module
   > 
2. Switch to the C-Module directory  
Navigate into the C-Module project folder on your local machine.
   >cd C-Module
   > 
3. Fetch the latest updates  
Ensue your local copy is up to date by fetching the recent changes from the remote repository.
   >git fetch --all
   >
4. List all branches  
Display all available branches in the C-Module repository.
   >git branch -a
   >
5. Checkout the desired branch  
Switch to the main branch of the C-Module.
   >git checkout main
   > 
6. Create a virtual environment  
It is recommended to set up a virtual environment for the C-Module to manage dependencies. The package is tested using Python 3.12.6.
With a newer Python version, we can not guarantee the full functionality of the package.
Select the correct Python interpreter.   
Show installed versions: 
   >py -0  

   - If you have installed multiple versions of Python, activate the correct version using the py-Launcher.
   >py -3.12 -m venv venv 
 
   - If you are using only a single version of Python on your computer:
   >python -m venv venv

7. Activate the virtual environment  
Enable the virtual environment to isolate the C-Module dependencies. 
   > venv\Scripts\activate

8. Install C-Module requirements  
Install all required C-Module dependencies listed in the requirements.txt file.
   > pip install -r requirements.txt

9. Install the C-Module in the editable mode (i.) or with the testing stack (dash[testing], pytest, coverage, 
webdriver_manager) necessary for running the unittests.
   1. > pip install -e . 
   2. > pip install -e .[dev]

(If the following error occurs: "ERROR: File "setup.py" or "setup.cfg" not found."
you might need to update the pip version you use with: 
>python.exe -m pip install --upgrade pip
   

### Doublecheck Installation
Doublecheck if installation was successful by running following command from terminal:  
   >run_cmodule --help

The help provides you information about the basic model settings which changed to adapt model runs to your needs (see [Module settings](#module-settings) for further details).

Test if the C-Module is running by executing the module only for a selection of carbon pools:

  >run_cmodule -CF_AGB=True -CF_BGB=True -CF_S=False -CF_DWL=False -C_HWP=True

By running the provided example, the C-Module will calculate carbon stocks and stock changes in forest aboveground biomass (-CF_AGB),
in forest belowground biomass (-CF_BGB), and in HWP (-C_HWP). Carbon stocks and stock changes in forest soil (-CF_S) and dead wood and
litter (-CF_DWL) will not be calculated.

### Test suite and coverage report
The C-Module comes with a test suite to ensure its functionality and allow for continuous and safe development. The 
test suite is triggered automatically in GitHub Actions when pushing or pulling into the main branch. 
Run the test suite to check the logic-related functionality of the package:

  > coverage run

or 
 > $python -m unittest discover -s test

The coverage report of the C-Module can be accessed using:
 > coverage report

While the functionality of the dashboard is tested separately from the main logic of the module, these tests are not 
included in the coverage report. However, these dashboard-related unittests are executed automatically in GitHub 
Actions.


## Use the C-Module
The module comes with a built-in CLI to quantify global carbon stocks and stock changes of the forestry sector for various
inputs. The module can be used in two ways: 
- As a standalone module quantifying key figures related to carbon based on historical data for production and trade, as
well as forest area and stock data. 

- As an add-on module to [TiMBA](https://github.com/TI-Forest-Sector-Modelling/TiMBA) allowing to quantify key figures
related to carbon based on forest products market, area, and stock projections.

While the parametric input can be seen in cmd output calling `run_cmodule --help` from the terminal, an important part to 
mention is user input data that need to be imported from a selected folder. You shall not change the following structure within the data folder:
```bash
.
`- data
  `-- input
    `-- additional_information
      |--additional_information_carbon.pkl
      |--additional_information_carbon.xlsx
    `-- historical_data
      |-- 20250703_faostat_data.csv
      |-- 20250703_fra_data.csv 
    `-- projection_data
      |--default_Sc_forest.csv
      |--default_Sc_results.csv
      |--default_Sc_results.pkl
    
```
When running the C-Module as a standalone application all scenario inputs contained in the folder projection_data are processed
automatically. If the C-Module is run as an add-on to TiMBA, the application retrieves automatically generated scenario inputs by TiMBA
while running.

Following data from external sources ([FAOSTAT](https://www.fao.org/faostat/en/#data/FO) and [FRA](https://fra-data.fao.org/assessments/fra/2020)) are used:
- The input data `20250703_faostat_data.csv` is a renamed copy of the file `Forestry_E_All_Data_NOFLAG.csv` provided by the [FAOSTAT bulk data
download](https://bulks-faostat.fao.org/production/Forestry_E_All_Data.zip).
- The input data `20250703_fra_data.csv` is a renamed copy of the file `FRA_Years_YYYY_MM_DD.csv` provided by the [FRA bulk data
download](https://fra-data.fao.org/api/file/bulk-download?assessmentName=fra&cycleName=2020&countryIso=WO).

The original FAOSTAT and FRA files are manually saved as CSV UTF-8 files. The most recent copy of the FAOSTAT and FRA datasets
was downloaded on 2025-07-03 and contains data up to 2023 for FAOSTAT and up to 2020 for FRA. For production and trade, the module
includes data from 1961 onwards. For forest area and stock, data are available from 1990 onwards. FAOSTAT and FRA data will be
updated regularly; however, users of the C-Module should verify whether more recent FAOSTAT or FRA data are available before use.

The package will generate a results directory called `output` which is located inside the data folder. The final directory after one run will look something like this:
```bash
.
`- data
  `-- output
      |-- ....log  # contains the logged process of the simulation
      |-- c_module_output_D<YYYYMMDD>Y<HH-MM-SS>_<scenario_name>.pkl  # contains all carbon outputs in a dict as pkl file
      |-- CarbonDWL_D<YYYYMMDD>Y<HH-MM-SS>_<scenario_name>.csv  # contains carbon outputs for deadwood and litter as csv file
      |-- CarbonForestBiomass_D<YYYYMMDD>Y<HH-MM-SS>_<scenario_name>.csv  # contains carbon outputs for forest biomass as csv file
      |-- CarbonWHP_D<YYYYMMDD>Y<HH-MM-SS>_<scenario_name>.csv  # contains carbon outputs for HWP as csv file
      |-- CarbonSoil_D<YYYYMMDD>Y<HH-MM-SS>_<scenario_name>.csv # contains carbon outputs for forest soils as csv file 
      |-- CarbonSubstitution_D<YYYYMMDD>Y<HH-MM-SS>_<scenario_name>.csv # contains carbon outputs for substitution as csv file
      |-- CarbonTotal_D<YYYYMMDD>Y<HH-MM-SS>_<scenario_name>.csv  # contains carbon outputs for all carbon pools as csv file

```
**Important Output Information**  
No output file will ever be overwritten by the application itself. New results-files will be generated in the format `results_D<yyyymmdd>T<hh-mm-ss>.csv` and will be saved to the output folder as well. The logfile itself won't be overwritten as well but also no new file created on additional runs. Log information simply gets appended to the existing logfile. Removing the logfile ahead of executing the model won't result in errors.

### Module settings
Multiple settings are integrated in the C-Module to allow users to interact with the model and adapt the modelling parameters to their research interests.
The following chapter provides a brief overview of the model settings.

Basic module settings include:

|            Setting            |                                                           Description                                                            |                                                                                                Options                                                                                                |  Default setting  |
|:-----------------------------:|:--------------------------------------------------------------------------------------------------------------------------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:-----------------:|
|      `add_on_activated`       |                                  Flag to activate if the C-Module is used as an add-on to TiMBA                                  |                                                                                                 Bool                                                                                                  |       True        |
|         `start_year`          |        Year from which calculations of the C-Module are started. The value should be aligned with the provided input data        |                                                                                                  int                                                                                                  |       2020        |
|          `end_year`           |       Year until which calculations of the C-Module are running. The value should be aligned with the provided input data        |                                                                                                  int                                                                                                  |       2050        |
|         `read_in_pkl`         |                                  Flag to control which input files are used for projection data                                  |                                                                                                 Bool                                                                                                  |       True        |
|      `calc_c_forest_agb`      |                              Flag to control if carbon in aboveground forest biomass is quantified                               |                                                                                                 Bool                                                                                                  |       True        |
|      `calc_c_forest_bgb`      |                              Flag to control if carbon in belowground forest biomass is quantified                               |                                                                                                 Bool                                                                                                  |       True        |
|     `calc_c_forest_soil`      |                                      Flag to control if carbon in forest soil is quantified                                      |                                                                                                 Bool                                                                                                  |       True        |
|       `calc_forest_dwl`       |                                  Flag to control if carbon in deadwood and litter is quantified                                  |                                                                                                 Bool                                                                                                  |       True        |
|         `calc_c_hwp`          |                                          Flag to control if carbon in HWP is quantified                                          |                                                                                                 Bool                                                                                                  |       True        |
|  `c_hwp_accounting_approach`  |                          Setting to control the accounting approach to quantify carbon in the HWP pool                           |                                                                                    "stock-change" or "production"                                                                                     |  "stock-change"   |
|      `historical_c_hwp`       |                          Setting to control the approach to quantify carbon in the historical HWP pool.                          |                                              "average": uses an 5-year average based on a selected year<br/> or<br/> "historical": uses historical data                                               |     "average"     |
|     `hist_hwp_start_year`     |                           Setting to control the year from which the historical HWP pool is calculated                           | "default": uses a uniform default reference year for all countries and products<br/> or<br/> "country-specific": uses country-specific reference year based on the data availability for each country |     "default"     |
| `hist_hwp_start_year_default` | Setting to control the reference year for the historical HWP pool. <br/>Used in combination with `hist_hwp_start_year`="default" |                                                                                                  int                                                                                                  | 2020 (start year) |
|    `show_carbon_dashboard`    |                        Setting to control if the dashboard for explorative result exploration is launched                        |                                                                                                 Bool                                                                                                  |       True        |


If the C-Module is used as an add-on to TiMBA, the start and end year parameters are automatically adjusted to match TiMBA's start and end years.
The C-Module is delivered with a set of default settings, which were tested and validated. The default settings can be changed when executing the
package in the CMD or in `default_parameters.py` (changes in settings by the CLI will overwrite parameters in `default_parameters.py`).
Gaps in historical FAOSTAT and FRA data exist. The C-Module relies on gap-filling procedures to curate the original data:
- For FRA data, the C-Module fills data gaps assuming that countries in the same regions have similar biogeographical characteristics.
Regional averages are used in case data is missing for the country.
- For FAOSTAT data, no data gap-filling procedure is implemented. However, if `historical_c_hwp`="average" is only applied
for years with data. If `hist_hwp_start_year`="country-specific", the C-Module searches automatically for the 5 years for which data is available for each country.
  
#### Settings as parameters
The CLI allows to access basic model settings and their default values. Run following code to get details:
 >run_cmodule --help

#### Advanced settings
In addition to the settings accessible via the CLI, users can control advanced settings through changes in `default_parameter.py`.
Further, users can enhance additional input data related to carbon factors with country-specific data to conduct analyses 
focused on specific countries.

### Carbon Dashboard
The C-Module comes with an integrated dashboard allowing for an interactive and intuitive exploration of modelling results.
The dashboard is composed of two main figures:
- A stacked bar chart depicting carbon stocks or stock changes over a predefined time period and geographical scope for a selection of scenarios. 
This figure allows for rapid identification of global, regional, or national trends in carbon stocks and 
stock changes in each selected pool. These trends can then be compared across selected scenarios. Carbon stocks and stock changes are summed up for each geographical selection.
- A world map depicting averaged carbon stocks, or stock changes over a predefined time period and geographical scope.
The figure allows for capturing geographical patterns while comparing results at the country-level within one scenario.

In default mode, both figures are generated for all carbon pools over the entire time period covered by the scenario results
on a global level (see figure 1).

In both figures, carbon stocks can either be displayed in absolute or relative terms. The dashboard integrates multiple dropdown 
fields and interactive options to tailor the figures to the user's needs. Filtered data and generated figures can be exported 
from the dashboard for external use with adequate citation.

Carbon in HWP can be displayed separately in the dashboard for sawnwood, wood-based panels, and paper and paper products.

![Carbon-Dashboard](https://github.com/TI-Forest-Sector-Modelling/C-Module/blob/main/assets/C-Module_dashboard_v1.png?raw=true)

**Figure 1:** Illustrative screenshot of the carbon dashboard.

## Extended module description
Forest ecosystems and related forest products constitute important natural carbon sinks. Owing to their cost-effectiveness,
flexibility, and availability, these sinks may play a vital role in achieving climate neutrality. To inform policy-making,
numerical estimates and projections of these sinks are essential for benchmarking current trends against established targets
and for exploring their potential when setting new ones. The C-Module quantifies and tracks carbon stocks in the forest sector
of 180 countries using the latest IPCC guidelines and established scientific methods.
For carbon in forest biomass (above- and below-ground), the C-Module uses forest stock data multiplied by nationally averaged
carbon densities derived from FRA [tC m⁻³]. For carbon in forest deadwood, litter, and soils, the C-Module uses forest area 
data multiplied by nationally averaged carbon densities from FRA [tC ha⁻¹] (Johnston et al., 2019; Johnston and Radeloff, 2019).
Changes in these carbon pools are calculated between individual years or across multi-year periods (as applied in TiMBA).

For quantifying carbon in harvested wood products (HWP), the C-Module offers several accounting approaches (e.g., stock-change
and production), which primarily differ in how trade is integrated. The stock-change approach is based on domestic consumption,
accounting for both exports and imports, whereas the production approach considers only carbon in HWP manufactured from nationally
harvested wood, excluding imports of raw wood (Rüter et al., 2019). The C-Module applies default Tier 1 parameters for HWP
half-lives and carbon content (Pingoud et al., 2006; Rüter et al., 2019).

In addition, substitution effects from the use of HWP are calculated using constant default substitution factors from 
Sathre and O'Connor (2010) and Hurmekoski et al. (2021). Due to the lack of country-specific data, these substitution
factors are applied uniformly across all countries.

All C-Module results are expressed in MtCO₂ per year (1 Mt = 1 million tonnes).

## Roadmap and project status

The development of the C-Module is ongoing and we are already working on future releases.
It is planned to extend the module using alternative datasets for carbon densities, especially remote sensing datasets.
Several research projects have extended and are extending different components of the C-Module:
- [BioSDG](https://www.thuenen.de/en/institutes/forestry/projects-1/the-bioeconomy-and-the-sustainable-development-goals-of-the-united-nations-biosdg)
- [CarbonLeak](https://www.thuenen.de/en/cross-institutional-projects/carbon-leak)

Frequently check [the GitHub repository](https://github.com/TI-Forest-Sector-Modelling/C-Module) for new releases.

## Contributing to the project
We welcome contributions, additions and suggestion to further develop or improve the code and the model. To check, discuss
and include them into this project, we would like you to share your ideas with us so that we can agree on the requirements
needed for accepting your contribution. 
You can contact us directly via GitHub by creating issues, or by writing an Email to:

tomke.honkomp@thuenen.de

A detailed open access documentation will follow and be linked here soon. So far, this README serves as a comprehensive
introduction and guidance on how to get started. 



## Authors
The C-Module was developped by [Tomke Honkomp](https://www.thuenen.de/de/fachinstitute/waldwirtschaft/personal/wissenschaftliches-personal/tomke-honkomp-msc) [(ORCID 0000-0002-6719-0190)](https://orcid.org/0000-0002-6719-0190).


## Contribution statement

| Author            | Conceptualization and theoretical framework | Methodology | Data Curation and Management | Formal Analysis | Programming | Writing and Documentation | Visualization | Review and Editing |
|:------------------|:-------------------------------------------:|:-----------:|:----------------------------:|:---------------:|:-----------:|:-------------------------:|:-------------:|:------------------:|
| Tomke Honkomp     |                      X                      |      X      |              X               |        X        |      X      |             X             |       X       |         X          |

## License and Copyright Note

Licensed under the GNU AGPL, Version 3.0. 

Copyright ©, 2025, Thuenen Institute, Tomke Honkomp

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public
 License along with this program.  If not, see
 <https://www.gnu.org/licenses/agpl-3.0.txt>.


## Acknowledgements

This work is the result of great efforts over two research projects [BioSDG](https://www.thuenen.de/en/institutes/forestry/projects-1/the-bioeconomy-and-the-sustainable-development-goals-of-the-united-nations-biosdg) and [CarbonLeak](https://www.thuenen.de/en/cross-institutional-projects/carbon-leak) at the Thünen Institute of Forestry.
In the last years, many people made important contributions to this work. Without their support, reflection, and constructive criticism, this undertaking would not have been as successful as it turns out to be now.
My gratitude goes to all of them. In particular, I would like to thank: 
-	The forest sector modelling team of the Thünen Institute of Forestry (Franziska Schier, Christian Morland, and Julia Tandetzki)
-	Holger Weimar and Matthias Dieter for the trustful and cooperative working environment, rational support and critical discussion and the opportunity to keep on going
-	The Thünen Institute of Forestry and its Head Matthias Dieter for providing financial resources over the years 
- [makeareadme.com](https://www.makeareadme.com/) for providing the template this README is leaned on.

## References

- Johnston, C.; Buongiorno, J.; Nepal, P.; Prestemon, J. (2019): From Source to Sink: Past Changes and Model Projections of Carbon Sequestration in the Global Forest Sector. In: J Forest Econ 34 (1-2), P. 47–72. DOI: 10.1561/112.00000442.
- Johnston, Craig M. T.; Radeloff, Volker C. (2019): Global mitigation potential of carbon stored in harvested wood products. In: Proceedings of the National Academy of Sciences of the United States of America 116 (29), P. 14526–14531. DOI: 10.1073/pnas.1904231116.
- Pingoud, K.; Skog, K. E.; Martino, D. L.; Tonosaki, M.; Xiaoquan, Z. (2006): Chapter 12: Harvested Wood Products. In: IPCC (Hg.): 2006 IPCC Guidelines for National Greenhouse Gas Inventories. Under the collaboration of H. S. Eggleston, L. Buendia, K. Miwa, T. Ngara und K. Tanabe. Japan: IGES.
- Rüter, S.; Matthews, R. W.; Lundblad, M.; Sato, A.; Hassan, R. A. (2019): Chapter 12: Harvested Wood Products. In: IPCC (Hg.): Refinement of the 2006 IPCC Guidelines for National Greenhouse Gas Inventories. Under the collaboration of E. Calvo Buendia, K. Tanabe, A. Kranjc, J. Baasansuren, M. Fukuda, S. Ngarize et al. Switzerland.
- Sathre, Roger; O’Connor, Jennifer (2010): Meta-analysis of greenhouse gas displacement factors of wood product substitution. In: Environmental Science & Policy 13 (2), P. 104–114. DOI: 10.1016/j.envsci.2009.12.005.
- Hurmekoski, Elias; Smyth, Carolyn E.; Stern, Tobias; Verkerk, Pieter Johannes; Asada, Raphael (2021): Substitution impacts of wood use at the market level: a systematic review. In: Environ. Res. Lett. 16 (12), P. 123004. DOI: 10.1088/1748-9326/ac386f.