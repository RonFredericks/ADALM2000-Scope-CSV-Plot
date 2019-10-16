# -*- coding: utf-8 -*-
"""
File: M2KCustomPlotButter.py

This custom script uses ADALM2000 exported CSV data to plot Butterworth filter results.

v 1.01, August 13, 2019
    Initial release
v 1.10, October 12, 2019
    Eliminate labque titles from constructor, hard code them instead as:
        self.plot_title_1
        self.plot_title_2
    Add intelligent display of frequency range for x-axis label in plot_custom_script()
    Add intelligent display of voltage range for y-axis label in plot_custom_script()
    Place plots into 3 Column grid using matplotlib GridSpec so Butterworth plot can have 2 plots side by side
        Plot 1: Original filter results plot now takes 2 of 3 columns
        Plot 2: Add new filter response plot for the remaining 1 column
    Replace heading tuple with individual x,y headings in class constructor

Algorithm:
    Create a phase corrected Butterworth digital IIR filter on a given CSV data channel with respect to time.
    Prepare a two plots of the results: Filtered Data, and Frequency Response.
    Add the two plots side-by-side to the end of the plots produced by the main program.

Note:
    The filter plot uses scipy's filtfilt() to align with CSV data displayed above the filter results.
        filtfilt() applies a linear digital filter twice, once forward and once backwards.
        The combined filter has zero phase and a filter order twice that of the original.

Author: Ron Fredericks, Ron@BiophysicsLab.com
License: MIT
Copyright 2019 Ron Fredericks, BiophysicsLab.com
See included license file (license.txt) or read it online: https://opensource.org/licenses/MIT

References:
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html
    https://stackoverflow.com/questions/12093594/how-to-implement-band-pass-butterworth-filter-with-scipy-signal-butter
    https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units
    https://matplotlib.org/3.1.1/gallery/subplots_axes_and_figures/align_labels_demo.html
    https://jakevdp.github.io/PythonDataScienceHandbook/04.08-multiple-subplots.html
# --------------------------------------------------------------------------------------------

Main program refers to: M2KScopePlot.py

This script is contained within a class: CustomPlotScript(object):

    Attributes:
        values defined using __init__ constructor to customize the Bandpass filter plot
            self.x_heading
            self.y_heading
            self.filtertype
            self.order
            self.lowcut
            self.highcut
            self.srate

        flag used to control whether custom script should be used or not
            self.is_custom_script

        data collected from CSV data file during execution of main program
            self.df_data
            self.info_dict
            self.headings

        Additional data copied from main program
            self.iplot_colors

        Additional strings used for Butterworth Filter display in final lab report
            self.plot_title_1
            self.plot_title_2

    Methods:
        get_headings_to_use(self)
        get_is_custom_script(self)
        set_iplot_colors(self, iplot_colors)
        set_df_data(self, df_data)
        set_info_dict(self, info_dict)
        set_headings(self, headings)
        test_custom_plot(self)
        butter_filter_create(lowcut, highcut, filtertype, fs, order=5)
        butter_filter(self, data, lowcut, highcut, filtertype, fs, order=5)
        plot_custom_script(self)

Initiate the Butterworth Filter script by creating custom_script in main program (example):

    custom_script = CustomPlotScript('Time(S)', 'CH1(V)', "bandpass", 3, 500, 1100, 1e+06)

    Where:
        'Time(S)', 'CH1(V)' are the x y data headings from csv file to use for filter and plot
        "bandpass" is the type of filter to create and use
        3 is the filter order (doubled because of forward and reverse filter creation)
        500, 1100 are the low and high cutoff frequencies used to create the filter
        1e+06 is the filter's sample rate (same as the sample rate as found in the csv file)
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as tck
import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt, freqz

from M2KScope.M2KScopePlotFncs import *


class CustomPlotScript(object):
    """
    A class used to add a custom plot after the subplots generated within the main program
    """

    def __init__(self, x_heading, y_heading, filtertype, order, lowcut, highcut, srate):
        """
        :param x_heading: str
                x-axis heading as found in csv data file
        :param y_heading: str
                y-axis heading as found in csv data file
        :param filtertype: str
                type of filter
                ["lowpass", "highpass", "bandpass", "bandstop"]
        :param order: int
                order of the filter
                Note: filters with order > 5 tend to fail using scipy's butter() 'ba' output coefficient vector method,
                        'sos' output would be more stable at higher filter orders, but sosfiltfilt() seems unstable.
                Note: filtfilt() as used in butter_filter() method,
                        doubles the order of the filter during its forward and backward process.
        :param lowcut: float
                frequency for low cutoff in filter types: ‘bandpass’, ‘bandstop’
                frequency for ‘lowpass’ filter type
                ignored for ‘highpass’ filter type
        :param highcut: float
                frequency for high cutoff in filter types: ‘bandpass’, ‘bandstop’
                frequency for ‘highpass’ filter type
                ignored for ‘lowpass’ filter type
        :param srate: float
                sample rate for filter in Hz (use the same sample rate as found in CSV data file)
        """
        # x-axis and y-axis panda dataframe headings must match str values associated with
        #   CSV file imported by main program.
        #   x-axis and y-axis headings are both required
        self.x_heading = x_heading.strip()
        self.y_heading = y_heading.strip()

        filtertype = filtertype.strip()
        self.filtertype = filtertype.lower()
        self.order = int(order)
        self.lowcut = float(lowcut)
        self.highcut = float(highcut)
        self.srate = float(srate)

        # Titles packaged for labque display using headings_to_use() method
        # Text title introducing x-axis and y-axis
        self.plot_title_1 = "Custom Phase Corrected Butterworth Filter Plot using "
        # Text title introducing Butterworth IIR digital filter parameters
        self.plot_title_2 = ": "

        # Flag used to control use of custom script in main program
        self.is_custom_script = False

        # CSV data useful for custom scripting
        # ------------------------------------

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
        Prepare a string for use by class LabQue() defined in M2MScopePlotTxtUI.py
            LabQue is used to print all useful data during the creation of plots
            Results are displayed on the screen and in text file next to plot images when saved

        Example results from labque.print_message_que():

            Recap of plot selections:
                Program: M2KScopePlot: v1.01, August 2 2019
                Plot CSV text file data generated by ADALM2000 Active Learning Module
                Today's date: Wednesday, August 21 2019
                File selected: ./TestData/Lab2.csv
                CSV data file generated on: Wednesday, July 24 2019
                Scopy Version (48fb6a9): v1.06, May 24 2019
                Plot title: M2K Oscilloscope [Nr of samples: 8000, Sample rate: 1e+06]
                List of 'Y-axis' data channels selected to plot: CH1(V), CH2(V), M1(V)
                Custom Phase Corrected Butterworth Filter Plot using Time(S), M1(V):
                    (filter=bandpass, order=3, lowcut=5.0, highcut=300.0, sample rate=10000.0)
                Plot size selected: (8.0, 8.0) in inches
                Plot data saved to file: ./TestData/Lab2.png
                Message queue saved in file: ./TestData/Lab2.txt

        :return: formatted string containing plot_title_1 + headings_to_use + plot_title_2 + filter parameters
        """
        temp_str = self.plot_title_1

        # include CSV data headings used in filter plot
        temp_str += self.x_heading + ", " + self.y_heading

        # include filter info
        temp_str = temp_str + self.plot_title_2
        temp_str = temp_str + "\n\t\t(Filter: " + str(self.filtertype)
        # filter order is doubled because signal.filtfilt() was used
        temp_str = temp_str + ", Order: " + str(2 * self.order)
        if self.filtertype == "highpass":
            temp_str = temp_str + ", Cutoff: " + str(self.highcut) + " Hz"
        elif self.filtertype == "lowpass":
            temp_str = temp_str + ", Cutoff: " + str(self.lowcut) + " Hz"
        else:
            temp_str = temp_str + ", Lowcut: " + str(self.lowcut) + " Hz"
            temp_str = temp_str + ", Highcut: " + str(self.highcut) + " Hz"

        freq_units, freq_value = rescale_frequency(self.srate)
        temp_str = temp_str + ", Sample rate: " + \
                   str(rescale_data(self.srate, 10**freq_value)) + " " + freq_units + ")"

        return temp_str

    def get_is_custom_script(self):
        """
        Flag used within main program to include this custom plot when True

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
            plot_custom_script()

        :param iplot_colors -> list of strings
        :return: None
        """
        self.iplot_colors = iplot_colors

    def set_df_data(self, df_data):
        """
        Make a deep copy of the same data extracted from ADALM2000 Scopy CSV data file used in the main program plots

        :param df_data: pandas dataframe
        :return: None
        """
        self.df_data = df_data.copy()

    def set_info_dict(self, info_dict):
        """
        Make a deep copy of the same info extracted from ADALM2000 Scopy CSV data file used in the main program

        :param info_dict: dictionary
        :return: None
        """
        self.info_dict = info_dict.copy()

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

    @staticmethod
    def get_frequencies(lowcut, highcut, filtertype):
        """
        Return a frequency or a 2-item list of frequencies depending on the Butterworth filter type
        :param lowcut: float, the low cutoff frequency
        :param highcut: float, the high cutoff frequency
        :param filtertype:
        :return: one or two frequencies for use as cutoff parameters in desired filter type
        """
        wnfreq = [lowcut, highcut]
        if filtertype == "lowpass":
            wnfreq = lowcut
        elif filtertype == "highpass":
            wnfreq = highcut
        return wnfreq

    def butter_filter_create(self, lowcut, highcut, filtertype, fs, order=5):
        """
        Create an IIR (Infinite impulse response) digital Butterworth filter
        :param lowcut: float
            Low cutoff frequency: the point at which the gain drops to 1/sqrt(2) that of the passband: “-3 dB point”
            Not used for highpass filter
        :param highcut: float
            High cutoff frequency: the point at which the gain drops to 1/sqrt(2) that of the passband: “-3 dB point”
            Not used for lowpass filter
        :param filtertype: str
            Filter type:  one of these strings ["lowpass", "highpass", "bandpass", "bandstop"]
        :param fs: float
            Sample rate: used to calculate the Nyquist frequency
        :param order: int
            The filter's order shapes the slope of the frequency response:
            higher order value improves frequency response using a steeper slope
        :return: b, a
            Numerator (b) and denominator (a) polynomials of the IIR filter.
        """
        # Nyquist Frequency: the minimum rate at which a signal can be sampled without introducing errors,
        #                   which is twice the highest frequency present in the signal.
        wnfreq = self.get_frequencies(lowcut, highcut, filtertype)
        b, a = butter(order, wnfreq, btype=filtertype, output='ba', fs=fs)
        return b, a

    def butter_filter(self, data, lowcut, highcut, filtertype, fs, order=5):
        """
        Create a butterworth filter using helper function butter_filter_create()
        Apply the filter on data
        Use signal.filtfilt() to apply filter twice for zero phase and double the original filter order
        Return filtered data as y
        :param data: is an ndarray-like pandas Series with float64 dtype elements
            data represents one channel of ADALM2000 scope data imported from CSV data file using pandas data structure
            Example: self.df_data[y_heading]
        :param lowcut: float
            see butter_filter_create() for details
        :param highcut: float
            see butter_filter_create() for details
        :param filtertype: str
            see butter_filter_create() for details
        :param fs: float
            see butter_filter_create() for details
        :param order: int
            see butter_filter_create() for details
        :return y: the filtered results with same shape as data
        """
        b, a = self.butter_filter_create(lowcut, highcut, filtertype, fs, order=order)
        # use filtfilt() instead of lfilter() to align phase with data plotted in main program
        y = filtfilt(b, a, data, method="gust")
        return y

    def test_custom_plot(self):
        """
        Test for valid headings to be used in custom plot script
        Test for valid parameters to be used in butterworth filter
        Set is_custom_script to True if tests are valid, False otherwise
        Report errors found to help user understand nature of the class instantiation problem
        """
        is_custom_script = True

        # avoid displaying common error headings more than once
        headings_displayed_flg = False

        if self.y_heading not in self.headings:
            print("\nCustom Butterworth Plot Script")
            print("\tHeadings with data available to filter: " + str([item for item in self.headings]))
            print("\tERROR: Y-axis heading not found: " + self.y_heading)
            headings_displayed_flg = True
            is_custom_script = False

        if self.x_heading not in self.headings:
            if not headings_displayed_flg:
                print("\nCustom Butterworth Plot Script")
                print("\tHeadings with data available to filter: " + str([item for item in self.headings]))
                headings_displayed_flg = True
            print("\tERROR: X-axis heading not found: " + self.x_heading)
            is_custom_script = False

        filter_lst = ["lowpass", "highpass", "bandpass", "bandstop"]
        if self.filtertype not in filter_lst:
            if not headings_displayed_flg:
                print("\nCustom Butterworth Plot Script")
                print("\tFilter types available to use: " + str([item for item in filter_lst]))
                headings_displayed_flg = True
            print("\tERROR: filtertype (" + self.filtertype + ") not valid")
            is_custom_script = False

        if self.order < 1:
            if not headings_displayed_flg:
                print("\nCustom Butterworth Plot Script")
                headings_displayed_flg = True
            print("\tERROR: Filter order must be an integer greater than 0")
            is_custom_script = False

        sample_rate_min_freq = 0.
        if self.filtertype == "bandpass" or self.filtertype == "bandstop":
            sample_rate_min_freq = self.highcut
            if self.highcut < self.lowcut:
                if not headings_displayed_flg:
                    print("\nCustom Butterworth Plot Script")
                    headings_displayed_flg = True
                print("\tERROR: Bandpass filter highcut must be greater than or equal to lowcut frequency "
                      "and non-zero")
                is_custom_script = False

        if self.filtertype == "lowpass":
            sample_rate_min_freq = self.lowcut
            if self.lowcut <= 0.:
                if not headings_displayed_flg:
                    print("\nCustom Butterworth Plot Script")
                    headings_displayed_flg = True
                print("\tERROR: Lowpass filter lowcut frequency must be greater than 0.")
                is_custom_script = False

        if self.filtertype == "highpass":
            sample_rate_min_freq = self.highcut
            if self.highcut <= 0.:
                if not headings_displayed_flg:
                    print("\nCustom Butterworth Plot Script")
                    headings_displayed_flg = True
                print("\tERROR: Highpass filter highcut frequency must be greater than 0.")
                is_custom_script = False

        if (self.srate <= 2 * sample_rate_min_freq) and (sample_rate_min_freq > 0.):
            # use this test only if self.filtertype has a valid value
            if not headings_displayed_flg:
                print("\nCustom Butterworth Plot Script")
            print("\tERROR: Filter sample frequency must be greater than "
                  "twice the highest frequency in data set (i.e. Nyquist frequency)")
            print("\tNote: Cutoff frequencies should be lower than", (self.srate/2))
            is_custom_script = False

        if not is_custom_script:
            input("\tPress any key to skip custom plot script...")

        self.is_custom_script = is_custom_script

    def plot_custom_script(self, grid_stack, grid_row):
        """
        Create a Magnitude vs Time plot using a butterworth filter
        Use the following functions during plot preparation:
            M2KScope.M2KScopePlotFncs ->
                                    compute_ticks() create a range of values defining grid ticks on a plot axis
                                    calculate_scale() Return maximum engineering scale (power of 10 in multiples of 3)
                                    rescale_dataframe() Rescale the data for a selected dataframe column
                                    adjust_time_heading() Change time display units for Y vs Time plot
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

        if not self.is_custom_script:
            # don't use this function if flag is false
            return

        # Apply a Butterworth Filter to a Data Channel then Plot: Voltage vs Time
        # -----------------------------------------------------------------------

        # stack Butterworth plot in this figure horizontally using 2 of 3 tiles
        plt.subplot(grid_stack[grid_row, :2])

        x_heading = self.x_heading
        y_heading = self.y_heading

        # Scale time line for best engineering units: S, mS, uS, nS
        engr_power = calculate_scale(self.df_data[x_heading])
        self.df_data[x_heading] = rescale_data(self.df_data[x_heading], 10 ** engr_power)

        # Type of filter
        filtertype = self.filtertype
        # Filter parameters: Sample rate and desired cutoff frequencies (in Hz) and filter order.
        fs = self.srate
        lowcut = self.lowcut
        highcut = self.highcut
        order = self.order  # Warning, filter unstable above order=5

        # Scale y-axis (Volts)
        # dfd = self.df_data[y_heading]
        # engr_power_v = calculate_scale(dfd)
        # dfd = rescale_data(dfd, 10 ** engr_power_v)

        # create filter values and plot
        filtered = self.butter_filter(self.df_data[y_heading], lowcut, highcut, filtertype, fs, order=order)
        engr_power_v = calculate_scale(filtered)
        filtered = rescale_data(filtered, 10 ** engr_power_v)
        plt.plot(self.df_data[x_heading], filtered, color=self.iplot_colors[-1])

        # Initialize x-axis time scale variables used to calculate 10 major ticks: like an oscilloscope
        myrange = compute_ticks(self.df_data[x_heading], 10)

        # Append one delta step to myrange to get 10 oscilloscope-like divisions (not just 10 ticks)
        if len(myrange) > 1:
            myrange = np.append(myrange, [myrange[len(myrange)-1]+(myrange[1]-myrange[0])])

        # Complete the display of x-axis
        plt.xticks(myrange)
        plt.gca().set_xlim(myrange[0], myrange[len(myrange)-1])
        plt.xticks(rotation=45)
        plt.xlabel(adjust_time_heading(engr_power))

        # Complete display of y-axis
        plt.ylabel(adjust_voltage_heading(y_heading, engr_power_v), color=self.iplot_colors[-1])

        # Prepare custom plot title
        temp_str = filtertype.capitalize() + " Filter ["
        # filter order is doubled because signal.filtfilt() was used
        temp_str = temp_str + "Order: " + str(2 * order)
        if self.filtertype == "highpass":
            temp_str = temp_str + ", Cutoff: " + str(highcut)
        elif self.filtertype == "lowpass":
            temp_str = temp_str + ", Cutoff=" + str(lowcut)
        else:
            temp_str = temp_str + ", Lo: " + str(lowcut)
            temp_str = temp_str + ", Hi: " + str(highcut)
        # temp_str = temp_str + ", srate=" + str(np.format_float_scientific(fs)) + "]"
        temp_str += "]"
        plt.title(temp_str)

        # Add plot control here because main program only applies to second plot
        # when two plots are stacked horizontally
        plt.grid(True)

        # Adjust number of x-axis minor ticks to 10 for linear scale only (errors on log scale)
        if plt.gca().get_xaxis().get_scale() == "linear":
            plt.gca().xaxis.set_minor_locator(tck.AutoMinorLocator(n=10))

        # digital filter frequency response plot, showing the critical points
        # -------------------------------------------------------------------

        # stack Butterworth plot in this figure horizontally using 1 of 3 tiles
        plt.subplot(grid_stack[grid_row, 2])

        if filtertype == 'lowpass':
            fs_temp = lowcut
        else:
            fs_temp = highcut
        fs_temp = fs_temp * 5.0
        b, a = self.butter_filter_create(lowcut, highcut, filtertype, fs_temp, order=(2*order))
        w, h = freqz(b, a, fs=fs_temp)

        freq_units, freq_multiplier = rescale_frequency(w)
        w = rescale_data(w, 10 ** freq_multiplier)

        plt.plot(w, np.abs(h), linewidth=2, color="royalblue")
        # plt.semilogx(w, 20 * np.log10(abs(h)))
        # left, right = plt.xlim()
        # bottom, top = plt.ylim()
        plt.title('Frequency Response')
        plt.xlabel('Frequency (' + freq_units + ')')
        plt.ylabel('Gain (Vo / Vi)', color="royalblue")
        plt.margins(0, 0.1)
        # plt.grid(which='both', axis='both')

        wnfreq = self.get_frequencies(lowcut, highcut, filtertype)
        if type(wnfreq) is list:
            for i in range(len(wnfreq)):
                plt.axvline(rescale_data(wnfreq[i], 10 ** freq_multiplier), linewidth=1, color='green')  # cutoff frequency
                plt.plot(rescale_data(wnfreq[i], 10 ** freq_multiplier), 0.5 * np.sqrt(2), 'ko', linewidth=1)
        else:
            plt.axvline(rescale_data(wnfreq, 10 ** freq_multiplier), linewidth=1, color='green')  # cutoff frequency
            plt.plot(rescale_data(wnfreq, 10 ** freq_multiplier), 0.5 * np.sqrt(2), 'ko')

        # Initialize x-axis scale variables used to calculate n major ticks
        myrange = compute_ticks(w, 5)
        # Append one delta step to myrange to get 10 oscilloscope-like divisions (not just 10 ticks)
        if len(myrange) > 1:
            myrange = np.append(myrange, [myrange[len(myrange)-1]+(myrange[1]-myrange[0])])
        # Complete the display of x-axis
        # https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.xticks.html
        plt.xticks(myrange)
        plt.gca().set_xlim(myrange[0], myrange[len(myrange)-1])
        plt.xticks(rotation=45)
