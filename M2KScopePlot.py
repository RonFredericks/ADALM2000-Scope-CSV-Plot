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
Version 1: Initial code created July 25, 2019
License: MIT
Copyright 2019 Ron Fredericks, BiophysicsLab.com
See included license file (license.txt) or read it online: https://opensource.org/licenses/MIT
# --------------------------------------------------------------------------------------------
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as tck

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
from CustomScripts.M2KCustomPlotNULL import custom_script
# from CustomScripts.M2KCustomPlotFFT import custom_script
# from CustomScripts.M2KCustomPlotButter import custom_script


m2kintro()

# get two pandas dataframes from a csv file
# - df_info is row data at top of csv file containing information about the df_data
# - df_data holds oscilloscope, column data with headings like this: Sample, Time(S), CH1(V), CH2(V), MAT1(V)
data_file, df_info = read_pandas_info()

# load the info_dict dictionary from df_info pandas dataframe
info_dict = load_info_dict(df_info)
custom_script.set_info_dict(info_dict)

# push csv file creation date onto message que
csv_file_date(info_dict['export'][1])

# push Scopy software version onto the message que
version_test(info_dict['scopy'][1])

# generate plot title from info_dict values
plt_title = generate_plot_title(info_dict)

# Read data from M2K CSV file based on user input
df_data = read_pandas_data(data_file)
headings = list(df_data.columns.values)

# print(headings)
# typical print results: Sample, Time(S), CH1(V), CH2(V)

iplot_colors = ['orange', 'magenta', 'green', 'blue', 'cyan', 'red', 'yellow', 'purple']

# Load useful data into CustomPlotScript class
custom_script.set_df_data(df_data)
custom_script.set_headings(headings)
custom_script.set_iplot_colors(iplot_colors)
# See if a custom script should be executed
custom_script.test_custom_plot()

# produce a subset of headings to plot such as: Time(S), CH1(V), CH2(V), M1(V)
headings2Plot = select_channels_to_plot(headings)
iplots = len(headings2Plot) - 1
if custom_script.get_is_custom_script():
    # add one extra subplot developed in custom script
    iplots += 1
    # labque.push_message_que("Custom plot using: " + custom_script.get_headings_to_use())
    labque.push_message_que(custom_script.get_headings_to_use())

# adjust size of plot based on user input
fwidth, fheight = set_plot_figure()

plt.figure(num="M2KScopePlot", figsize=(fwidth, fheight))

# scale time line for best engineering units: S, mS, uS, nS
engr_power = calculate_scale(df_data[headings[1]])
df_data[headings[1]] = rescale_dataframe(df_data[headings[1]], 10 ** engr_power)

# loop through all plots based on headings found in the csv file
iplot_current = 0
while iplots - iplot_current:
    # stack all plots in this figure vertically
    plt.subplot(iplots, 1, iplot_current + 1)

    if (iplots - iplot_current) == 1 and custom_script.get_is_custom_script():
        custom_script.plot_custom_script()
    else:
        # generate an X Y plot with a unique color
        plt.plot(df_data[headings2Plot[0]], df_data[headings2Plot[iplot_current + 1]],
                 color=iplot_colors[iplot_current])

        # Initialize x-axis time scale variables used to calculate 10 major ticks: like an oscilloscope
        myrange = compute_ticks(df_data[headings[1]], 10)
        # Append one delta step to myrange to get 10 oscilloscope-like divisions (not just 10 ticks)
        if len(myrange) > 1:
            myrange = np.append(myrange, [myrange[len(myrange) - 1] + (myrange[1] - myrange[0])])

        plt.xticks(myrange)
        plt.gca().set_xlim(myrange[0], myrange[len(myrange) - 1])
        plt.xticks(rotation=45)

        plt.xlabel(adjust_time_heading(engr_power))
        plt.ylabel(headings2Plot[iplot_current + 1], color=iplot_colors[iplot_current])

        if iplot_current == 0:
            # display title only once at the top of the figure
            plt.title(plt_title, color='black', fontstyle='italic')

    # adjust number of x-axis minor ticks to 10
    plt.gca().xaxis.set_minor_locator(tck.AutoMinorLocator(n=10))
    # adjust number of y-axis minor ticks based on how many plots will be stacked in one figure
    if iplots == 1:
        plt.gca().yaxis.set_minor_locator(tck.AutoMinorLocator(n=10))
    else:
        plt.gca().yaxis.set_minor_locator(tck.AutoMinorLocator(n=5))
    plt.grid(True)
    iplot_current += 1

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

if text_file:
    labque.push_message_que("Message queue saved in file: " + text_file + "\n")
    file = open(text_file, "w")
    file.write("Recap of plot selections:")
    file.close()
print("Recap of plot selections:")

labque.print_message_que("\t", txt_file=text_file)

print("\nProgram exiting normally now...")
