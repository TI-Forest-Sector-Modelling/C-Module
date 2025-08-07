![C-Module_Logo](C-Module_Logo_transparent_v1.png)

------
<!-- TOC -->

- [Cite C-Module](#cite-c-module)
- [Install C-Module](#install-the-c-module)
  - [Double check installation](#doublecheck-installation)
  - [Test suite and coverage](#test-suite-and-coverage-report)
- [Use the C-Module](#use-the-c-module)
  - [Module settings](#model-settings)
    - [Settings as parameters](#settings-as-parameters)
    - [Advanced settings](#advanced-settings)
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

The Carbon Module tracks global carbon stocks and flows across pools in the forestry sector. In the current version, the module 
quantifies carbon stocks and flows in forest biomass (above and belowground), in harvested wood products (HWP), in forest soils,
in dead wood and litter for 180 countries. Substitution effects related to the use of HWP are quantified additionaly.
The quantification of carbon in forest biomass, forest soils, and dead wood and litter is based on the publications of 
Johnston et al. (2019) and Johnston and Radeloff (2019). Carbon in HWP is quantified based on the IPCC Tier1-approach (IPCC 2019).
Additional mathematical information are provided in the [joined publication](#todo).

## Cite C-Module

We are happy that you use the C-Module for your research. When publishing your work in articles, working paper, presentations
or elsewhere, please cite the module as 

[Honkomp (2025) C-Module v1](CITATION.cff)

## Install the C-Module

The package is developed and tested with Python 3 (python 3.12.6) version on Windows.
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
It is recommended to set up a virtual environment for the C-Module to manage dependencies. The package is tested using Python >3.9 (3.8.10 and 3.9.7). With a newer Python version, we can not guarantee the full functionality of the package.
Select the correct Python interpreter.   
Show installed versions: 
   >py -0  
   >
   - If you have installed multiple versions of Python, activate the correct version using the py-Launcher.
   >py -3.12 -m venv venv 
   > 
   - If you are using only a single version of Python on your computer:
   >python -m venv venv
   >
7. Activate the virtual environment  
Enable the virtual environment to isolate the C-Module dependencies. 
   >venv\Scripts\activate
   > 
8. Install C-Module requirements  
Install all required C-Module dependencies listed in the requirements.txt file.
   >pip install -r requirements.txt
   >
9. Install the C-Module in the editable mode  
   >pip install -e .

(If the following error occurs: "ERROR: File "setup.py" or "setup.cfg" not found."
you might need to update the pip version you use with: 
>python.exe -m pip install --upgrade pip
   

### Doublecheck Installation
Doublecheck if installation was successful by running following command from terminal:  
   >run_cmodule --help

The help provides you information about the basic model settings which changed to adapt model runs to your needs (see section [Model settings](#model-settings) for further details).

Test if the C-Module is running by executing the model only for the first period:

  >run_cmodule -MP=1

### Test suite and coverage report
The C-Module comes with a test suite to ensure its functionality.
Run the test suite to check the functionality of the package and validate the produced results with those provided by the TI-FSM:

  > coverage run

or 
 > $python -m unittest discover -s test


To reduce the test suite running time, only the first period will be computed and compared. The test suite results will not be saved.
The computed results and provided validation results are compared with a relative tolerance of 5%.  

The coverage report of the TiMBA model can be accessed using:
 > coverage report


## Use the C-Module
The module comes with a built-in CLI to quantify global carbon stocks and flows of the forestry sector for various
inputs. The module can be used in two ways: 
- As a stand-alone module quantifying key figures related to carbon based on historical data for production, forest area,
and forest stock changes. 
- As an add-on module to the Timber market Model for policy-Based Analysis ([TiMBA](https://github.com/TI-Forest-Sector-Modelling/TiMBA))
allowing to quantify key figures related to carbon based on forest products market, area, and stock projections.

While the parametric input can be seen in cmd output calling `run_timba --help` from the terminal, an important part to 
mention is user input data that need to be imported from a selected folder. You shall not change the following structure within the data folder:
```bash
.
`- data
  `-- input
    `-- additional_information
      |--additional_information_carbon.pkl
      |--additional_information_carbon.xlsx
    |-- 20250703_faostat_data.csv
    |-- 20250703_fra_data.csv
    |--default_Sc_forest.csv
    |--default_Sc_results.csv
    |--default_Sc_results.pkl
    
```
Following data from external sources ([FAOSTAT](https://www.fao.org/faostat/en/#data/FO) and [FRA](https://fra-data.fao.org/assessments/fra/2020)) are used:
- The input data `20250703_faostat_data.csv` is a renamed copy of the file `Forestry_E_All_Data_NOFLAG.csv` provided by the [FAOSTAT bulk data
download](https://bulks-faostat.fao.org/production/Forestry_E_All_Data.zip).
- The input data `20250703_fra_data.csv` is a renamed copy of the file `FRA_Years_YYYY_MM_DD.csv` provided by the [FRA bulk data
download](https://fra-data.fao.org/api/file/bulk-download?assessmentName=fra&cycleName=2020&countryIso=WO).

The original FAOSTAT and FRA files are manually saved as an CSV UTF-8 file. The last copy of the FAOSTAT and FRA data was
downloaded on the 2025-07-03 and contains data until the year 2023 for FAOSTAT and 2020 for FRA. FAOSTAT and FRA data will
be updated regularly. However, when using the C-Module, check if new FAOSTAT and FRA data are available.

The package will generate a results directory called `output` which is located inside the data folder. The final directory after one run will look something like this:
```bash
.
`- data
  `-- output
      |-- ....log  # contains the logged process of the simulation
      |-- DataContainer_....pkl  # contains all output information as pkl file
      |-- results....csv  # contains main results as csv file
      |-- worldprices....csv  # contains world price results as csv file
      |-- forest....csv  # contains forest area and stock results as csv file
      |-- manufacture....csv #contain results for manufacturing as csv 
      |-- results_aggregated....csv #contain aggregated results on continent level as csv file

```
**Important Output Information**  
No output file will ever be overwritten by the application itself. New results-files will be generated in the format `results_D<yyyymmdd>T<hh-mm-ss>.csv` and will be saved to the output folder as well. The logfile itself won't be overwritten as well but also no new file created on additional runs. Log information simply gets appended to the existing logfile. Removing the logfile ahead of executing the model won't result in errors.

### Model settings
Multiple settings are integrated in the C-Module to allow users to interact with the model and adapt the modelling parameters to their research interests.
Following chapter provides an brief overview of the model settings. A detailed description of the settings is provided in the documentation. 

Basic module settings include:

[comment]: <to be complemented>

The C-Module is delivered with a set of default settings, which were tested and validated. The default settings can be changed when excuting the package in the CMD or in `default_parameters.py` (changes in settings by the CLI will overwrite parameters in `default_parameters.py`).
  
#### Settings as parameters
The CLI allows to access basic model settings and their default values.

[comment]: <to be complemented>


#### Advanced settings
In addition to the settings accessible via the CLI, users can control advanced settings through changes in `Defines.py` 
[comment]: <to be complemented>

## Extended module description
To quantify and track carbon sequestration in the forest sector, TiMBA has been extended with a carbon module based on IPCC guidelines. TiMBA is enabled to quantify and price the climate mitigation potential of forests globally and on national level.

[comment]: <to be complemented>

## Roadmap and project status

The development of the C-Module is ongoing and we are already working on future releases. 
Several research projects are currently extending different components of the C-Module:
- CarbonLeak
- 
Frequently check [the GitHub repository](https://github.com/TI-Forest-Sector-Modelling/C-Module) for new releases.
[comment]: <to be complemented>

## Contributing to the project
We welcome contributions, additions and suggestion to further develop or improve the code and the model. To check, discuss and include them into this project, we would like you to share your ideas with us so that we can agree on the requirements needed for accepting your contribution. 
You can contact us directly via GitHub by creating issues, or by writing an Email to:

tomke.honkomp@thuenen.de

A detailed open access documentation will follow and be linked here soon. So far, this README serves as a comprehensive introduction and guidance on how to get started. 



## Authors
The C-Module was developped by [Tomke Honkomp](https://www.thuenen.de/de/fachinstitute/waldwirtschaft/personal/wissenschaftliches-personal/tomke-honkomp-msc) [(ORCID 0000-0002-6719-0190)](https://orcid.org/0000-0002-6719-0190).


## Contribution statement

| Author            | Conceptualization and theoretical framework | Methodology | Data Curation and Management | Formal Analysis | Programming | Writing and Documentation | Visualization | Review and Editing |
|:------------------|:-------------------------------------------:|:-----------:|:----------------------------:|:---------------:|:-----------:|:-------------------------:|:-------------:|:------------------:|
| Tomke Honkomp     |                      X                      |      X      |              X               |        X        |      X      |             X             |       X       |         X          |

## License and Copyright Note

Licensed under the GNU AGPL, Version 3.0. 

Copyright ©, 2025, Thuenen Institute, TI-FSM, Tomke Honkomp

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
-	The forest sector modelling team of the Thünen Institute of Forestry
-	Holger Weimar and Matthias Dieter for the trustful and cooperative working environment, rational support and critical discussion and the opportunity to keep on going
-	The Thünen Institute of Forestry and its Head Matthias Dieter for providing financial resources over the years 
- [makeareadme.com](https://www.makeareadme.com/) for providing the template this README is leaned on.

## References
