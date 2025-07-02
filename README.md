![C-Module_Logo](C-Module_Logo_transparent_v1.png)

------
<!-- TOC -->

- [Cite C-Module](#cite-c-module)
- [Install C-Module](#install-timba)
  - [Double check installation and test suite](#doublecheck-installation-and-test-suite)
- [Use C-Module](#use-timba)
  - [Module settings](#model-settings)
    - [Settings as parameters](#settings-as-parameters)
    - [Advanced settings](#advanced-settings)
- [C-Module extended model description](#timba-extended-model-description)
- [Roadmap and project status](#roadmap-and-project-status)
- [Contributing to the project](#contributing-to-the-project)
- [Authors](#authors)
- [Contribution statement](#contribution-statement)
- [License and Copyright Note](#license-and-copyright-note)
- [Acknowledgements](#acknowledgements)
- [References](#references)

<!-- /TOC -->

# C-Module

The Carbon Module tracks global carbon stocks and flows across pools of the forestry sector. In the current version, the module 
quantifies carbon stocks and flows in forest biomass (above and belowground), in harvested wood products (HWP), in forest soils,
in dead wood and litter for 180 countries. Substitution effects related to the use of HWP are quantified additionaly.

## Cite C-Module

We are happy that you use the C-Module for your research. When publishing your work in articles, working paper, presentations
or elsewhere, please cite the module as 

[Honkomp (2025) C-Module v1](CITATION.cff)

## Install TiMBA

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
It is recommended to set up a virtual environment for the C-Module to manage dependencies. The package is tested using Python >3.8.9 (3.8.10 and 3.9.7). With a newer Python version, we can not guarantee the full functionality of the package.
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
The package comes with a built-in CLI to compute the TiMBA for various inputs. While the parametric input can be seen in cmd output calling `run_timba --help` from the terminal, an important part to mention is user input data that need to be imported from a selected folder. You shall not change the following structure within the data folder:
```bash
.
`- data
  `-- input
    `-- 01_Input_Files
      |-- world.xlsx  # contains all input data to the model
    `-- 02_Additional_Informations
      |-- additional_information.xlsx 
      |-- worldprice.xlsx
      |--additional_information_carbon.xlsx
    `-- 03_Serialization
      |-- AddInfoContent.pkl  # contains additional information about the last input data which is processed by the model
      |-- AddInfoCarbonContent.pkl  # contains additional carbon information about the last input data which is processed by the model
      |-- WorldDataContent.pkl  # contains input information about the last input data which is processed by the model
      |-- WorldPriceContent.pkl  # contains world price information about the last input data which is processed by the model
```

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
- ### Todo To be complemented

The C-Module is delivered with a set of default settings, which were tested and validated. The default settings can be changed when excuting the package in the CMD or in `default_parameters.py` (changes in settings by the CLI will overwrite parameters in `default_parameters.py`).
  
#### Settings as parameters
The CLI allows to access basic model settings and their default values. 

### Todo To be complemented

#### Advanced settings
In addition to the settings accessible via the CLI, users can control advanced settings through changes in `Defines.py` 

### Todo To be complemented

## Extended description of the C-Module
To quantify and track carbon sequestration in the forest sector, TiMBA has been extended with a carbon module based on IPCC guidelines. TiMBA is enabled to quantify and price the climate mitigation potential of forests globally and on national level.

## Roadmap and project status

The development of the C-Module is ongoing and we are already working on future releases.

Several projects are currently extending different components of the C-Module:
- 
Frequently check https://github.com/TI-FSM for new releases.

## Contributing to the project
We welcome contributions, additions and suggestion to further develop or improve the code and the model. To check, discuss and include them into this project, we would like you to share your ideas with us so that we can agree on the requirements needed for accepting your contribution. 
You can contact us directly via GitHub by creating issues, or by writing an Email to:

tomke.honkomp@thuenen.de

A detailed open access documentation will follow and be linked here soon. So far, this README serves as a comprehensive introduction and guidance on how to get started. 



## Authors
The C-Module was developped by [Tomke Honkomp](https://www.thuenen.de/de/fachinstitute/waldwirtschaft/personal/wissenschaftliches-personal/tomke-honkomp-msc) [(ORCID 0000-0002-6719-0190)](https://orcid.org/0000-0002-6719-0190).


## Contribution statement

| Author            | Conceptualization and theoretical framework | Methodology | Data Curation and Management | Formal Analysis | Programming | Writing and Documentation | Visualization | Review and Editing | Supervision |
|:------------------|:-------------------------------------------:|:-----------:|:----------------------------:|:---------------:|:-----------:|:-------------------------:|:-------------:|:------------------:|:-----------:|
| Tomke Honkomp     |                      X                      |      X      |              X               |        X        |      X      |             X             |       X       |         X          |             |

## License and Copyright Note

Licensed under the GNU AGPL, Version 3.0. 

Copyright ©, 2025, Thuenen Institute, TI-FSM, tomke.honkomp@thuenen.de

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
