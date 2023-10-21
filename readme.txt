How to use the GUI to install openmc and prerequisistes under miniconda3
This tutorial is tested for ubuntu 22.04 

Prof. Tarek El Bardouni, University Abdelmalek Essaadi, Tetouan, Morocco

A/ First make an update of your system and install the following packages if don't exist:

	sudo apt update
	sudo apt upgrade

	sudo apt install g++ cmake libhdf5-dev libpng-dev

B/ Before running the GUI: install python3-pyqt5

	sudo apt install python3-pyqt5

or 

	sudo apt install pyqt5-dev pyqt5-dev-tools

C/ install git

	sudo apt install git

D/ run the application from its directory by executing :

	python3 gui.py


1. In the tab "get openmc" install miniconda3 and update its packages

2. close the gui

3. close and reopen the terminal

4. make sure the conda is activated

5. as pyqt5 is not yet installed under conda, if the GUI doesn't work, run it by executing :

	/usr/bin/python3 gui.py

insteade of : python3 gui.py

6. install prerequisites
- Before installing prerequisites it is better to update miniconda on terminal or from the gui.
- If the update frozes in "Solving environment" step an issue is:
	- delete the file : ~/.condarc
	- then set channel priority : conda config --set channel_priority flexible


It's better to close the gui after prequisites installing is finished, then in a terminal activate the created openmc environment, for example: conda activate openmc-py3.7
If you can not run the gui because pyqt5 is not installed under conda, try the command in a terminal : pip install pyqt5

7. install openmc

If compiling openmc crashes repeat its installation. If the compiling still doesn't work properly reinstall cmake under conda by : conda install cmake

8. download neutron data

E/ runing openmc under the GUI

Use the script bellow to lunch the gui to run openmc :

	conda activate openmc-py3.7

	export OPENMC_CROSS_SECTIONS=$HOME/Py-OpenMC-2020/data/endfb71_hdf5/cross_sections.xml

	python3 gui.py

To run the two first commands automaticaly, each time the terminal is opened, add them to the .bashrc file.

Note that the variable OPENMC_CROSS_SECTIONS must point to the correct path of downloaded cross sections data folder

E/ License

This software is free software, you can redistribute it and / or modify it under the
terms of the GNU General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later version. For the complete
text of the license see the GPL-web page.
