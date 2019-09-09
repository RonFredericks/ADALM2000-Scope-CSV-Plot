# -*- coding: utf-8 -*-
"""
File: M2KScopePlotFncs.py
Math for plotting
v 1.01, August 13, 2019

Author: Ron Fredericks, Ron@BiophysicsLab.com
License: MIT
Copyright 2019 Ron Fredericks, BiophysicsLab.com
See included license file (license.txt) or read it online: https://opensource.org/licenses/MIT
# --------------------------------------------------------------------------------------------

Functions:
    calculate_scale(df, step=10)
    adjust_time_heading(power)
    cube_root(x)
    rescale_dataframe(df, scale)
    compute_ticks(x, step=10)
"""
import numpy as np


# ----------------------------------------------------
def calculate_scale(df, step=10):
    """
    Return maximum engineering scale (power of 10 in multiples of 3)
    :param df: pandas dataframe holding a scope axis such as "Time(S)"
    :param step: number of ticks to separate the plot (i.e. 10 represents "plot shall have 10 scope-like divisions"
    :return: engineering exponent best suited to scale units such that values range stays under +- 10
    """
    xmin = min(df)
    xmax = max(df)
    xstep = (xmax - xmin) / step
    xround = int(abs(np.log10(xstep))) + 1
    engr_lst = [1, 3, 6, 9]
    engr_index = -1
    while True:
        engr_index += 1
        test = abs(xround / engr_lst[engr_index])
        if test < 1:
            engr_index -= 1
            break
    engr_index = max(0, min(3, engr_index))
    return engr_lst[engr_index]
# ----------------------------------------------------


def adjust_time_heading(power):
    """
    Adjust the time heading for plot display
    :param power:
    :return: Str
        return the correct time units for plot display
    """
    power_lst = ['Time (S)', 'Time (mS)', 'Time (uS)', 'Time (nS)']
    return power_lst[cube_root(power)]
# ----------------------------------------------------


def cube_root(x):
    """
    Calculate the cube root of x
    Designed to work with adjust_time_heading function
    :param x: Integer or float value, positive or negative
    :return: Return closest Integer value to the cube root
    """
    x = abs(x)
    return int(round(x ** (1. / 3)))
# ----------------------------------------------------


def rescale_dataframe(df, scale):
    """
    Rescale the data for a selected dataframe column
    One example: convert Time(S) to Time(uS)
    :param df: One column in the pandas dataframe such as time df_data[headings[1]]
    :param scale: A scale factor to multiple original data such as 1E6
    :return: The rescaled dataframe column
    """
    for i in df.index:
        df.at[i] = df.at[i]*scale
    return df
# ----------------------------------------------------


def compute_ticks(x, step=10):
    """
    Create a range of values defining grid ticks on a plot axis
    :param x: The dataframe to be plotted
    :param step: The number of major ticks for the dataframe's axis
    :return: A numpy array of equally spaced values to be displayed on a plot axis
    """

    xmin = min(x)
    xmax = max(x)
    xstep = (xmax - xmin) / step
    xround = int(abs(np.log10(xstep))) + 1
    xstepr = round(xstep, xround + 1)
    return np.arange(round(xmin, xround), round(xmax, xround), xstepr)
