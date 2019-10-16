#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create graphs from exported ADALM2000 Oscilloscope CSV data files
Ref: https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/ADALM2000.html

Main Program:
    M2KScopePlot.py

M2KScope:
    M2KScopePlotUI.py: A text-based User Interface for control parameter input
    M2KScopePlotFncs.py: Support functions for plots

CustomScripts:
    M2KCustomPlotNULL.py: A user modifiable python script designed to ignore the custom script
    M2KCustomPlotFFT.py: A user modifiable python script designed to generate an extra plot using FFT
    M2KCustomPlotButter.py: A user modifiable python script designed to generate an extra plot using Butterworth filter

Author: Ron Fredericks, Ron@BiophysicsLab.com
Version 1.01: July 25, 2019
    Initial code created
Version 1.02: September 25 2019
    Update module M2KScopePlotUI function verify_test() to support Scopy version 1.1.0
    Update M2KScopePlot.py remove 'yellow' from iplot_colors list
Version 1.10: October 12 2019
    Pass current release version text to m2kinfo() function, track current and past version details as comments
    Place plots into n Row x 3 Column grid using matplotlib GridSpec so Butterworth plot can have 2 plots side by side
    Add preferences.ini settings file
        - Remove need to make changes to any python code while using custom scripts
        - Controls all custom script parameters including store/recall of last changes made
        - Adds control for display of frequency as a legend for each plot

License: MIT
Copyright 2019 Ron Fredericks, BiophysicsLab.com
See included license file (license.txt) or read it online: https://opensource.org/licenses/MIT
# --------------------------------------------------------------------------------------------
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import matplotlib.gridspec as gridspec
import configparser
import importlib

from M2KScope.M2KScopePlotTxtUI import *
from M2KScope.M2KScopePlotFncs import *

# -----------------------------------------------------------------------------------------------------------
# Custom Scripts
#
#   Select (uncomment only) one of the scripts below or add one of your own
#       M2KCustomPlotNULL	    Ignores the custom script feature
#       M2KCustomPlotFFT	    Append one FFT plot, follow guidance at end of this file: M2KCustomPlotFFT.py
#       M2KCustomPlotButter	    Append one Butterworth filter plot, follow guidance at end of this file:
#                               M2KCustomPlotButter.py
# -----------------------------------------------------------------------------------------------------------

# Release Dates:
# "v1.01, July 25 2019"
# "v1.02, September 25 2019"
# "v1.10, October 12 2019"
m2kintro("v1.10, October 12 2019")

config = configparser.RawConfigParser()
config.optionxform = str
config.read(combine_file('.\Preferences', 'preferences', 'ini'))
# DisplayFrequency: Yes in preferences.ini will include a frequency value in each plot
displayFrequency = config['ScopeChannelPlots'].getboolean('DisplayFrequency')

# get two pandas dataframes from a csv file
# - df_info is row data at top of csv file containing information about the df_data
# - df_data holds oscilloscope, column data with headings like this: Sample, Time(S), CH1(V), CH2(V), MAT1(V)
data_file, df_info = read_pandas_info(config)

# load the info_dict dictionary from df_info pandas dataframe
info_dict = load_info_dict(df_info)

# push csv file creation date onto message que
csv_file_date(info_dict['export'][1])

# push Scopy software version onto the message que
version_test(info_dict['scopy'][1])

# Read data from M2K CSV file based on user input
df_data = read_pandas_data(data_file)

# typical headings: Sample, Time(S), CH1(V), CH2(V)
headings = list(df_data.columns.values)

iplot_colors = ['orange', 'magenta', 'green', 'blue', 'cyan', 'red', 'purple']

# produce a subset of headings to plot such as: Time(S), CH1(V), CH2(V), M1(V)
headings2Plot = select_channels_to_plot(headings)
iplots = len(headings2Plot) - 1

# Select, import, and instantiate a custom script, use the null script as a place holder for no custom script
script, param_lst = select_custom_script(config, headings2Plot, info_dict['rate'][1])
script_name = config.get('CustomScript Names', script)
# Ref: https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
module = importlib.import_module('CustomScripts.'+script_name)
my_class = getattr(module, 'CustomPlotScript')
custom_script = my_class(*param_lst)

# Load useful data into CustomPlotScript class
custom_script.set_info_dict(info_dict)
custom_script.set_df_data(df_data)
custom_script.set_headings(headings)
custom_script.set_iplot_colors(iplot_colors)

# See if a custom script should be executed
custom_script.test_custom_plot()

# adjust size of plot based on user input
fwidth, fheight = select_plot_size()
plt.figure(num="M2KScopePlot", figsize=(fwidth, fheight))

# Use three tiles per row in plots so Butterworth custom script can display two plots side by side
# Determine the total number of rows needed with the help  of the get_is_custom)script() function
gs = gridspec.GridSpec((iplots+1) if custom_script.get_is_custom_script() else iplots, 3)

# Scale time line for best engineering units: S, mS, uS, nS
engr_power_t = calculate_scale(df_data[headings[1]])
df_data[headings[1]] = rescale_data(df_data[headings[1]], 10 ** engr_power_t)

# Initialize x-axis time scale variables used to calculate 10 major ticks
myrange = compute_ticks(df_data[headings[1]], 10)
# Append one delta step to myrange to get 10 divisions (not just 10 ticks)
if len(myrange) > 1:
    myrange = np.append(myrange, [myrange[len(myrange) - 1] + (myrange[1] - myrange[0])])
time_per_tick = (myrange[10] - myrange[0]) / 10

# generate plot title from info_dict values
s = adjust_time_heading(engr_power_t)
time_units = s[s.find("(")+1:s.find(")")]
plt_title = generate_plot_title(info_dict, time_per_tick, time_units)

# Loop through all CSV import data plots based on headings found in the csv file
iplot_current = 0
while iplots - iplot_current:

    # Stack all plots in this figure vertically using all three tiles
    plt.subplot(gs[iplot_current, :])

    # Scale voltage y-axis for best engineering units: V, mV, uV, nV, pV
    engr_power_v = calculate_scale(df_data[headings2Plot[iplot_current + 1]])
    df_data[headings2Plot[iplot_current + 1]] = \
        rescale_data(df_data[headings2Plot[iplot_current + 1]], 10**engr_power_v)

    # Generate an X Y plot with a unique color
    plt.plot(df_data[headings2Plot[0]], df_data[headings2Plot[iplot_current + 1]],
             color=iplot_colors[iplot_current])

    # # Initialize x-axis time scale variables used to calculate 10 major ticks
    # myrange = compute_ticks(df_data[headings[1]], 10)
    # # Append one delta step to myrange to get 10 divisions (not just 10 ticks)
    # if len(myrange) > 1:
    #     myrange = np.append(myrange, [myrange[len(myrange) - 1] + (myrange[1] - myrange[0])])

    plt.xticks(myrange)
    plt.gca().set_xlim(myrange[0], myrange[len(myrange) - 1])
    plt.xticks(rotation=45)

    plt.ylabel(adjust_voltage_heading(headings2Plot[iplot_current + 1], engr_power_v),
               color=iplot_colors[iplot_current])

    if displayFrequency:
        peak_title, flabel = get_fft_peaks(headings2Plot[iplot_current + 1], df_data, info_dict, peak_cnt=1)
        if peak_title:
            plt.legend([generate_plt_label(flabel)], loc='upper right', title="Frequency via FFT")

    # Display title only once at the top of the figure
    if iplot_current == 0:
        plt.title(plt_title, color='black', fontstyle='italic')

    if custom_script.get_is_custom_script():
        # display time axis when custom plot will be drawn later
        plt.xlabel(adjust_time_heading(engr_power_t))
        plt.setp(plt.gca().get_xticklabels(), visible=True)
    else:
        # Display time axis only once for stacked subplots
        if (iplots - iplot_current) == 1:
            plt.xlabel(adjust_time_heading(engr_power_t))
            plt.setp(plt.gca().get_xticklabels(), visible=True)
        else:
            plt.setp(plt.gca().get_xticklabels(), visible=False)

    # adjust number of x-axis minor ticks to 10 for linear scale only (errors on log scale)
    if plt.gca().get_xaxis().get_scale() == "linear":
        plt.gca().xaxis.set_minor_locator(tck.AutoMinorLocator(n=10))

    # Adjust number of y-axis minor ticks based on how many plots will be stacked in one figure
    if iplots == 1:
        plt.gca().yaxis.set_minor_locator(tck.AutoMinorLocator(n=10))
    else:
        plt.gca().yaxis.set_minor_locator(tck.AutoMinorLocator(n=5))

    plt.grid(True)

    iplot_current += 1

# Plot up to one custom scripted plot
if custom_script.get_is_custom_script():
    # Final plot may be a custom script, pass along the stack pointer and row in stack
    custom_script.plot_custom_script(gs, iplot_current)
    labque.push_message_que(custom_script.get_headings_to_use())

    # adjust number of x-axis minor ticks to 10 for linear scale only (errors on log scale)
    if plt.gca().get_xaxis().get_scale() == "linear":
        plt.gca().xaxis.set_minor_locator(tck.AutoMinorLocator(n=10))
    # Adjust number of y-axis minor ticks
    plt.gca().yaxis.set_minor_locator(tck.AutoMinorLocator(n=5))

    plt.grid(True)

# use tight_layout() to ensure there is enough space around all plot elements
plt.tight_layout()

# save and display plot
fig_file = get_plot_file(data_file)
text_file = ""
if fig_file:
    text_file = fig_file[:-3] + "txt"
    plt.savefig(fig_file)

if not system_in_ide():
    print("\nPlot launched, quit interactive plot display to close program\n")
else:
    print("\n")
plt.show()

mywrite_str = "Lab Report (recap of plot selections):"
if text_file:
    labque.push_message_que("Message queue saved in file: " + text_file + "\n")
    file = open(text_file, "w")
    file.write(mywrite_str)
    file.close()
print(mywrite_str)

labque.print_message_que("\t", txt_file=text_file)

print("\nProgram exiting normally now...")
