# -*- coding: utf-8 -*-
"""
File: M2KCustomPlotFFT.py
v 1.01, August 13, 2019

This custom script uses ADALM2000 exported CSV data to plot FFT results:
    create the FFT from a given CSV data channel
    prepare a plot of the results
    add the plot to the end of the plots produced by the main program

Author: Ron Fredericks, Ron@BiophysicsLab.com
License: MIT
Copyright 2019 Ron Fredericks, BiophysicsLab.com
See included license file (license.txt) or read it online: https://opensource.org/licenses/MIT
# --------------------------------------------------------------------------------------------

Main program refers to: M2KScopePlot.py

This script is completely contained within a class: CustomPlotScript(object):

    Attributes:
        values defined using __init__ constructor to customize the FFT plot
            self.plot_title_1
            self.headings_to_use
            self.plot_title_2
            self.n

        flag used to control whether custom script should be used or not
            self.is_custom_script

        data collected from CSV data file during execution of main program
            self.iplot_colors
            self.df_data
            self.info_dict
            self.headings

        Additional data copied from main program
            self.iplot_colors

    Methods:
        get_headings_to_use(self)
        get_is_custom_script(self)
        set_iplot_colors(self, iplot_colors)
        set_df_data(self, df_data)
        set_info_dict(self, info_dict)
        set_headings(self, headings)
        test_custom_plot(self)
        reduce_sample_array(signal_data, n)
        plot_custom_script(self)

Initiate the script by creating an object at the end of this file:

    custom_script = CustomPlotScript("Custom Plot using: ", ('', 'CH1(V)'),
                                    ", with dataset reduced by a factor of: ", 200)
"""
from scipy.fftpack import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from M2KScope.M2KScopePlotFncs import compute_ticks


class CustomPlotScript(object):
    """
    A class used to add a custom plot to the end of the subplots created in the main program
    """

    def __init__(self, plot_title_1, headings_to_use, plot_title_2="", n=1):
        """
        :param plot_title_1: str
                general title packaged for labque display using headings_to_use() method
        :param headings_to_use: a tuple holding x-axis and y-axis panda dataframe
                headings must match str values associated with CSV file imported by main program, or None
                y-axis required to activate this custom plot script
                x-axis optional
        :param plot_title_2: str
                FFT title packaged for labque display using headings_to_use() method
        :param n: positive integer
                Number of data samples to step over for each axis
                Larger n generates narrower frequency range for plotted fft
                When n=1 no data will be removed
        """

        self.plot_title_1 = plot_title_1
        self.headings_to_use = (headings_to_use[0].strip(), headings_to_use[1].strip())
        self.plot_title_2 = plot_title_2
        self.n = int(n)

        # Flag used to control custom script in main program
        self.is_custom_script = False

        # CSV data useful for custom scripting
        # ------------------------------------

        # List of colors to use for plotting
        #   example: iplot_colors = ['orange', 'magenta', 'green', 'blue', 'cyan', 'red', 'yellow', 'purple']
        self.iplot_colors = []

        # Pandas dataframe to hold imported csv column data, one row for each heading
        #
        #         Example using print(df_data)
        #
        #                 Sample     Time(S)     CH1(V)    CH2(V)     M1(V)
        #                 0          0 -0.004000 -0.003607 -0.009240  0.004883
        #                 1          1 -0.003999  0.001272 -0.004327  0.004883
        #                 2          2 -0.003998  0.004524  0.000585  0.003906
        #                 3          3 -0.003997  0.011029  0.007136  0.003906
        #                 ...      ...       ...       ...       ...       ...
        #                 7997    7997 0.003997  -0.023123 -0.028891  0.004883
        #                 7998    7998  0.003998 -0.021497 -0.022341  0.000000
        #                 7999    7999  0.003999 -0.010112 -0.014153  0.003906
        self.df_data = pd.DataFrame()

        # Dictionary of CSV info
        # Example:
        # info_dict = {
        #     'scopy': (';Scopy version', '48fb6a9')
        #     'export': (';Exported on', 'Wednesday July 24/07/2019')
        #     'device': (';Device', 'M2K')
        #     'samples': (';Nr of samples', '8000')
        #     'rate': (';Sample rate', '1.00E+06')
        #     'tool': (';Tool', 'Oscilloscope')
        # }
        self.info_dict = {}

        # List of df_data headings extracted from CSV file as strings
        # Example: Sample, Time(S), CH1(V), CH2(V)
        self.headings = []

        # plot data useful for custom scripting
        # ------------------------------------

        # List of colors to use for plotting
        #   Example:
        #       iplot_colors = ['orange', 'magenta', 'green', 'blue', 'cyan', 'red', 'yellow', 'purple']
        self.iplot_colors = []

    def get_headings_to_use(self):
        """
        Prepare a string for use by class LabQue() defined in M2MScopPlotTxtUI.py
            LabQue is used to print all useful data during the creation of plots
            Results are displayed on the screen and in text file next to plot images when saved

            Example:

                Recap of plot selections:
                    Program: M2KScopePlot: v1.01, August 2 2019
                    Plot CSV text file data generated by ADALM2000 Active Learning Module
                    Today's date: Thursday, August 22 2019
                    File selected: ./TestData/Lab2.csv
                    CSV data file generated on: Wednesday, July 24 2019
                    Scopy Version (48fb6a9): v1.06, May 24 2019
                    Plot title: M2K Oscilloscope [Nr of samples: 8000, Sample rate: 1e+06]
                    List of 'Y-axis' data channels selected to plot: CH1(V), CH2(V), M1(V)
                    Custom FFT Plot using: M1(V), with dataset reduced by a factor of: 200
                    Plot size selected: (8.0, 8.0) in inches
                    Plot data saved to file: ./TestData/Lab2.png
                    Message queue saved in file: ./TestData/Lab2.txt

        :return: formatted string containing plot_title_1 + headings_to_use + plot_title_2 + n
        """
        temp_str = self.plot_title_1
        for istr in self.headings_to_use:
            if istr:
                temp_str += istr + ","
        if temp_str:
            temp_str = temp_str[:-1]

        if self.n > 1:
            # include slice information if slicing actually occurs
            temp_str = temp_str + self.plot_title_2
            temp_str = temp_str + str(self.n)
        return temp_str

    def get_is_custom_script(self):
        """
        Flag used within main program to include a custom plot when True

        Methods used that involve is_custom_scipt flag
            test_custom_plot() -> sets or clears flag
            plot_custom_script() -> generates custom plot when flag is True

        :return: is_custom_script -> bool
            True indicates that all data is ready for custom plot
            False indicates no custom plot will be used
        """
        return self.is_custom_script

    def set_iplot_colors(self, iplot_colors):
        """
        Make a copy of the same custom plot color list as in the main program
        Select one of these list items to add color to custom script plot

        Used by method:
            plot_custom_script

        :param iplot_colors -> list of strings
        :return: None
        """
        self.iplot_colors = iplot_colors

    def set_df_data(self, df_data):
        """
        Make a copy of the same data extracted from ADALM2000 Scopy CSV data file used in the main program plots

        :param df_data -> pandas dataframe
        :return: None
        """
        self.df_data = df_data

    def set_info_dict(self, info_dict):
        """
        Make a copy of the same info extracted from ADALM2000 Scopy CSV data file used in the main program
        Used to get sample rate in method custom_plot_script

        :param info_dict -> dictionary
        :return: None
        """
        self.info_dict = info_dict

    def set_headings(self, headings):
        """
        Make a copy of the headings found in CSV export file during execution of the main plot program
        Used by method:
            test_custom_plot()

        Example:
            ['Sample', 'Time(S)', 'CH1(V)', 'CH2(V)', 'M1(V)']

        :param headings -> list of strings
        :return:
        """
        self.headings = headings

    def test_custom_plot(self):
        """
        Test for valid headings to be used in custom plot script
        Set is_custom_script to True if headings_to_use is found within headings
        Otherwise is_custom_script remains False
        """
        if self.headings_to_use[1]:
            # custom script will not be used if y-axis heading is empty

            is_custom_script = True
            # avoid displaying headings available more than once
            headings_displayed_flg = False
            if self.headings_to_use[1] not in self.headings:
                print("\nCustom Plot Script")
                print("\tHeadings available to use: " + str([item for item in self.headings]))
                print("\tERROR: Y-axis heading not found: " + self.headings_to_use[1])
                headings_displayed_flg = True
                is_custom_script = False
            if self.headings_to_use[0] and (self.headings_to_use[0] not in self.headings):
                if not headings_displayed_flg:
                    print("\nCustom Plot Script")
                    print("\tHeadings available to use: " + str([item for item in self.headings]))
                # x-axis heading is optional, but should be a valid heading if defined
                print("\tERROR: X-axis not empty or not found: " + self.headings_to_use[0])
                is_custom_script = False
            if not is_custom_script:
                input("\tPress any key to skip custom plot script...")

            self.is_custom_script = is_custom_script

    @staticmethod
    def reduce_sample_array(signal_data, n):
        # n must be between 1 and signal_data size
        # signal_data size includes the number of samples * number of channels
        signal_data = signal_data[::n]
        return signal_data

    def plot_custom_script(self):
        """
        Create a Magnitude vs Frequency plot for one of the columns of data captured in CSV data file
        Build logic to generate an FFT display using the following functions:
            self.reduce_sample_array() for frequency range
            scipy.fftpack -> fft() for y-axis
            scipy.fftpack -> fftfreq() for x-axis
            M2KScope.M2KScopePlotFncs ->
                                    compute_ticks() create a range of values defining grid ticks on a plot axis
        Main program plot loop sets up the plot using the following methods:
            plt.figure()
            plt.subplot()
        Prepare and execute the following plot parameters within this method:
            plt.plot()
            plt.xticks()
            plt.gca().set_xlim()
            plt.xticks()
            plt.title()
            plt.xlabel()
            plt.ylabel()
        Main program finally completes the custom plot using the following:
            plt.gca().xaxis.set_minor_locator()
            plt.gca().yaxis.set_minor_locator()
            plt.grid()
            plt.tight_layout()
            plt.savefig()
            plt.show()

        :return: None
        """
        # ref: https://stackoverflow.com/questions/48298724/fast-fourier-transform-on-motor-vibration-signal-in-python

        if not self.is_custom_script:
            # don't use this function if flag is false
            return

        yheading = self.headings_to_use[1]

        # Reduce signal_data array size by a factor of n (used to reduce the frequency range)
        n = self.n
        updated_df_data = self.reduce_sample_array(self.df_data, n)

        # update sample rate and array size
        sample_rate = float(self.info_dict['rate'][1])/n
        array_size = updated_df_data[yheading].size

        # Calculate y-axis magnitude scaled to same units as y-axis in heading2Use data (ie volts)
        yf = 2/array_size * fft(updated_df_data[yheading].values)
        # Calculate x axis as frequency in Hz
        x = fftfreq(array_size, 1 / float(sample_rate))
        x_half = x[:x.size//2]

        # Change x-axis frequency from Hz, to kHz to MHz for best display
        freq_units = [('Hz', 1), ('kHz', -3), ('MHz', -6)]
        log_max = int(np.log10(np.amax(x_half)))
        if log_max >= 5:
            # MHz
            freq_unit_index = 2
        elif log_max >= 2:
            # kHz
            freq_unit_index = 1
        else:
            # Hz
            freq_unit_index = 0
        for i in range(0, x_half.size):
            x_half[i] = x_half[i] * 10**freq_units[freq_unit_index][1]

        plt.plot(x_half, abs(yf)[:array_size//2], color=self.iplot_colors[-1])

        # Initialize x-axis time scale variables used to calculate 10 major ticks: like an oscilloscope
        myrange = compute_ticks(x_half, 10)
        # Append one delta step to myrange to get 10 oscilloscope-like divisions (not just 10 ticks)
        if len(myrange) > 1:
            myrange = np.append(myrange, [myrange[len(myrange)-1]+(myrange[1]-myrange[0])])

        # Complete the display of x-axis
        plt.xticks(myrange)
        plt.gca().set_xlim(myrange[0], myrange[len(myrange)-1])
        plt.xticks(rotation=45)
        plt.xlabel('Frequency (' + freq_units[freq_unit_index][0] + ')')

        # Complete the display of y-axis
        plt.ylabel(self.headings_to_use[1], color=self.iplot_colors[-1])

        # Prepare custom plot title
        plt.title("Magnitude vs Spectrum")


# Create custom_script to plot using the CustomPlotScript class

# Include the following parameters to use the custom script:
#   1) Text tile for x-axis (optional) and y-axis headings to be used within get_headings_to_use()
#   2) String tuple holding the x-axis and y-axis heading names:
#       x-axis heading is optional (not used in this fft custom script)
#       y-axis heading is required to activate the custom script
#   3) Text title for step parameter (optional)
#   4) Integer step value to reduce data as needed to get an ideal frequency range in plot (optional)
custom_script = CustomPlotScript("Custom FFT Plot using: ", ('', 'CH2(V)'),
                                 ", with dataset reduced by a factor of: ", 200)
