# -*- coding: utf-8 -*-
"""
File: M2KScopePlotFncs.py
Math functions used to support plotting

v 1.01, August 13, 2019
    initial version
v 1.10, October 12, 2019
    Add new function, rescale_frequency() to determine which units are best for FFT display
    Add new function, adjust_volt_heading() to display FFT voltage scale
    Add new function, round_sig(), to simplify compute_tick() function
    Update compute_tick() function to correct optimized x and y scale calculations for each tick on plot grid
    Change name of rescale_dataframe() to rescale_data() to emphasise rescale supports many data types including:
        NumPy ndarrays, pandas dataframes, ints, and floats

Author: Ron Fredericks, Ron@BiophysicsLab.com
License: MIT
Copyright 2019 Ron Fredericks, BiophysicsLab.com
See included license file (license.txt) or read it online: https://opensource.org/licenses/MIT
# --------------------------------------------------------------------------------------------

Functions:
    calculate_scale(df, step=10)
    adjust_time_heading(power)
    adjust_voltage_heading(power)
    cube_root(x)
    rescale_data(df, scale)
    round_sig(x, sig=2)
    compute_ticks(x, step=10)
    rescale_frequency(x_array)
    get_fft_peaks(heading_to_use, df_data, info_dict, peak_cnt=-1, min_peak_height=0.0, n=1, scaling=False)
    generate_plt_label(flabel)
"""
import numpy as np
from scipy.fftpack import *
from scipy import signal


# ----------------------------------------------------
def calculate_scale(df, step=10):
    """
    Return maximum engineering scale (power of 10 in multiples of 3)
    :param df: pandas dataframe holding a scope axis such as "Time(S)"
    :param step: number of ticks to separate the plot (i.e. 10 represents "10 scope-like divisions"
    :return: engineering exponent best suited to scale units such that values range stays under +- 10
    """
    xmin = min(df)
    xmax = max(df)
    xstep = (xmax - xmin) / step
    xround = int(abs(np.log10(xstep))) + 1
    engr_lst = [0, 3, 6, 9, 12]
    if xround > 10:
        engr_index = 4
    if xround > 7:
        engr_index = 3
    elif xround > 5:
        engr_index = 2
    elif xround > 1:
        engr_index = 1
    else:
        engr_index = 0
    return engr_lst[engr_index]
# ----------------------------------------------------


def adjust_time_heading(power):
    """
    Adjust the time heading for plot display
    :param power:
    :return: Str
        return the correct time units for plot display
    """
    power_lst = ['Time (S)', 'Time (mS)', 'Time (uS)', 'Time (nS)', 'Time (pS)']
    return power_lst[cube_root(power)]
# ----------------------------------------------------


def adjust_voltage_heading(base_heading, power):
    """
    Adjust the volt heading for plot display
    :param power:
    :param base_heading: Str
        base heading for label such as V, CH1(V), CH2(V), M1(V), etc...
    :return: Str
        return the correct voltage heading with units for plot display
    """
    power_lst = ['V', 'mV', 'uV', 'nV', 'pV']
    str_ptr1 = base_heading.find("(")
    if str_ptr1 < 0:
        # Adjust heading when there are new parentheses used
        new_heading = power_lst[cube_root(power)]
    else:
        new_heading = base_heading[0:str_ptr1+1] + power_lst[cube_root(power)] + ")"
    return new_heading
# ----------------------------------------------------


def cube_root(x):
    """
    Calculate the cube root of x
    Designed to work with:
        adjust_time_heading function
        adjust_volt_heading function
    :param x: Integer or float value, positive or negative
    :return: Return closest Integer value to the cube root
    """
    x = abs(x)
    return int(round(x ** (1. / 3)))
# ----------------------------------------------------


def rescale_data(ds, scale):
    """
    Rescale the data for a selected dataframe column
    One example: convert Time(S) to Time(uS)
    :param ds: One column in the pandas dataframe such as time df_data[headings[1]], int or float
    :param scale: A scale factor to multiple original data such as 1E6
    :return: The rescaled dataframe column
    """
    df = ds * scale
    return df
# ----------------------------------------------------


def round_sig(x, sig=2):
    """
    Round a float to sig significant figures, where sig is based on exponent (via log10) of float
    Ref: https://stackoverflow.com/questions/3410976/how-to-round-a-number-to-significant-figures-in-python
    :param x: float
            Number to be rounded
    :param sig: integer
            Number of significant digits to round floating point number
    :return: float
            Floating point number rounded to sig significant figures
    """
    x_tmp = abs(x)
    epsilon = 1e-20
    if x_tmp < epsilon:
        # avoid log10 of zero error
        return 0.0
    x_tmp = np.log10(x_tmp)
    x_tmp = np.floor(x_tmp)
    x_tmp = int(x_tmp)
    x_tmp = round(x, sig - x_tmp - 1)
    return x_tmp
# ----------------------------------------------------


def compute_ticks(x, step=10):
    """
    Create a range of values defining grid ticks on a plot axis
    :param x: The dataframe to be plotted
    :param step: The number of major ticks for the dataframe's axis
    :return: A numpy array of equally spaced values to be displayed on a plot axis
    """
    xmin = round_sig(x.min())
    xmax = round_sig(x.max())
    xstep = round_sig((xmax - xmin) / step)
    return np.arange(xmin, xmax, xstep)
# ----------------------------------------------------


def rescale_frequency(x_array):
    """
    Change x-axis frequency from Hz, to kHz to MHz for best FFT display
    :param x_array: ndarray of x values, or a regular list of float values
    :return: (string, integer) Tuple
            frequency units: 'Hz', 'kHz', or 'MHz'
            frequency scale: 0, -3, or -6
    """
    freq_units = [('Hz', 0), ('kHz', -3), ('MHz', -6)]
    if not isinstance(x_array, np.ndarray):
        x_array = np.array([x_array])
    fmax = np.amax(x_array)
    flog = np.log10(fmax)
    log_max = int(flog)
    if log_max > 5:
        # MHz
        freq_unit_index = 2
    elif log_max > 2:
        # kHz
        freq_unit_index = 1
    else:
        # Hz
        freq_unit_index = 0
    return freq_units[freq_unit_index][0], freq_units[freq_unit_index][1]
# ----------------------------------------------------


def get_fft_peaks(heading_to_use, df_data, info_dict, peak_cnt=-1, min_peak_height=0.0, n=1, scaling=False):
    """
    Take the fft of a data set and return the peaks found (freq and voltage) from largest to smallest
    :param heading_to_use:  a tuple holding x-axis and y-axis panda dataframe
                headings must match str values associated with CSV file imported by main program
    :param df_data: pandas dataframe
    :param info_dict: dictionary
    :param peak_cnt: integer
                Maximum number of peaks to highlight (shown as vertical lines plus frequency, magnitude list in legend)
                Peaks are found using the scipy.signal.find_peak() function
                Number of peaks displayed will be the maximum of peaks found up to the number of of peaks requested
                Note: -1 indicates all peaks should be displayed that meet min_peak_height limitation
    :param min_peak_height: float
                Use this parameter to skip peaks that are too small to be of interest
                The value corresponds to the FFT magnitude (in Volts). A value of .05 (Volts) for example
    :param n: positive integer
                Number of times to reduce FFT sampling frequency
                Larger n generates narrower frequency range for plotted fft
                When n=1 no sampling data will be removed
    :param scaling: bool
                Flag to activate scaling of results
                    - True requests scaling of frequency and voltage to optimized engineering units
                    - False requests no scaling so frequency remains in Hz and voltage remains in Volts
    :return: (string, string list) tuple
            peak_title string, A title for use in a plot legend
            flabel string list, A list of formatted peak values: frequency, voltage (sorted by voltage)
    """

    yheading = heading_to_use

    # Reduce signal_data array size by a factor of n (used to reduce the frequency range)
    updated_df_data = df_data[::n]

    # update sample rate and array size
    sample_rate = float(info_dict['rate'][1]) / n
    array_size = updated_df_data[yheading].size

    # Calculate y-axis magnitude scaled to same units as y-axis in heading2Use data (ie volts)
    yf = 2 / array_size * fft(updated_df_data[yheading].values)
    # Calculate x axis as frequency in Hz
    x = fftfreq(array_size, 1 / float(sample_rate))
    x_half = x[:x.size // 2]

    if not scaling:
        freq_units = "Hz"
        freq_multiplier = 0
    else:
        freq_units, freq_multiplier = rescale_frequency(x_half)
        x_half = rescale_data(x_half, 10 ** freq_multiplier)

    y_half = abs(yf)[:array_size // 2]
    if not scaling:
        # amplitude remains in Volts
        engr_power_v = 0
    else:
        engr_power_v = calculate_scale(y_half)
        y_half = rescale_data(y_half, 10 ** engr_power_v)

    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html#scipy.signal.find_peaks
    peaks = signal.find_peaks(y_half, height=rescale_data(min_peak_height, 10 ** engr_power_v))[0]
    flabel = []
    peak_title = ""
    if peaks.size > 0:
        xhp = x_half[peaks]
        ayf = y_half[peaks]
        # Get indices that would sort voltage (magnitude) array.
        ayf_as = np.argsort(ayf)
        max_peaks = xhp.size
        # Determine how many FFT peaks to display (all or limited from class constructor input)
        if peak_cnt < 0:
            peak_cnt = max_peaks
        else:
            peak_cnt = min(max_peaks, peak_cnt)
        if peak_cnt == 1:
            peak_title = 'FFT Peak Value'
        else:
            peak_title = 'Largest FFT Peak Values'

        for i in range(peak_cnt):
            i_ptr = ayf_as[len(ayf_as) - i - 1]
            flabel.append("{:.2f} {}, {:.2f} {}".format(xhp[i_ptr], freq_units, ayf[i_ptr],
                                                        adjust_voltage_heading('V', engr_power_v)))

    return peak_title, flabel
# ----------------------------------------------------


def generate_plt_label(flabel):
    """
    Convert formatted string designed for fft peak list legend to a simple single frequency legend
    :param flabel: String
        A list of fft frequency/votage pairs generated from function get_fft_peaks()
    :return:
        The most dominant frequency scaled and formatted as a string with units
    """
    fl_values = flabel[0].split()
    freq = float(fl_values[0])
    freq_units, freq_scale = rescale_frequency(freq)
    return "{0:.2f} {1:}".format(rescale_data(freq, 10**freq_scale), freq_units)
