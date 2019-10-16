File: Preferences_ReadMe.txt
Purpose: Describe preferences.ini for control of main program: M2KScopePlot.py
Author: Ron at BiophysicsLab.com
Initial Date: 10/14/2019

Preferences.ini is very useful for control entry of custom scripts for FFT and Butterworth Filters.
The entries define the names of each custom script and as such allows new custom scripts to be created following the basic pattern shown in this file.

For FFT and Butterworth Filter data entry:

Each entry for these scripts includes a data value and a prompt value.
The data value will be remembered with each use of the script so reuse will not require tedious repetitive data entry. The data values are further explained within each custom script itself. While the prompt entry associated with each data point will display during data entry while running the main program. Some custom prompt modifications take place such as for: x and y headings to display valid entries, and butterworth filter sample rate as this value is tied to the same rate of the oscilloscope csv export.

For new custom scripts:

For new scripts follow the same pattern presented in the ini file to define a new script and new data/prompt pairs to text. No changes within python code main program or existing library files are required to add a new custom script: Just a new custom script python file and the needed data / prompt values within this file.

Review the empty custom script M2KCustomPlotNULL.py to see what methods are used in every custom script.
For some data entry the prompts may need to be customized. The function select_custom_script(config, headings2Plot, sample_rate) in the M2KScope library file M2KScopePlotTxtUI.py is where tweaks to the prompt display are made currently.