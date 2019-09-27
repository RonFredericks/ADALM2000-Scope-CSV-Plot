# -*- coding: utf-8 -*-
"""
File: M2KScopePlotUI.py
Text-based User Interface Module for M2KScopePlot
v 1.01, August 13, 2019
	first version
v 1.0.2, September 25, 2019
	m2kintro() and version_test() updated for Scopy version 1.1.0

Author: Ron Fredericks, Ron@BiophysicsLab.com
License: MIT
Copyright 2019 Ron Fredericks, BiophysicsLab.com
See included license file (license.txt) or read it online: https://opensource.org/licenses/MIT
# --------------------------------------------------------------------------------------------

Classes:
    LabQue(object)
Functions:
    m2kintro()
    system_in_ide()
    split_file(file)
    combine_file(file_path, file_base_name, file_extent)
    list_files(directory, extension)
    get_file_info()
    get_datafile()
    read_pandas_info(nr=7, head=None, er_bad_lines=False)
    read_pandas_data(dat_file, skiprw=7, er_bad_lines=False)
    set_plot_figure()
    load_info_dict(df)
    csv_file_date(csv_date)
    version_test(ver)
    generate_plot_title(info_dict)
    get_plot_file(data_file)
    select_channels_to_plot(headings)
"""


import sys
from os import path, name, environ
from time import localtime, strftime
import re
from glob import glob
import pandas as pd


# message que list property and methods
# ----------------------------------------------------
class LabQue(object):
    def __init__(self):
        """
        Create a message list to be used as a queue
        The queue will hold string messages representing lab notes captured while executing this program
        """
        self.message_list = []
        # list_reversed flag tracks whether list is in reversed order
        self.list_reversed = False

    def print_message_list(self):
        print("message list:\n", self.message_list)

    def _reverse_message_list(self):
        """
        The list is created following FILO logic, this function will change logic to FIFO
        This function is called once when message_list ready to be dequed or printed using pop
        State of list_reversed flag is reversed each time this method is called
        :return: No return
        """
        self.message_list.reverse()
        if not self.list_reversed:
            self.list_reversed = True
        else:
            self.list_reversed = False

    def push_message_que(self, new_message):
        self.message_list.append(new_message)

    def pop_message_que(self):
        """
        Retrieve messages from the list, one "pop" at a time
        Messages will be taken off the list in FIFO order as a result of using the _reverse_message_list() function
        :return: Most recent message from message_list or "None"
        """
        if not self.list_reversed:
            # Use self.list_reversed flag to insure message_list is in reverse order for dequeing
            self._reverse_message_list()
        if len(self.message_list):
            message = self.message_list.pop()
        else:
            message = None
            # Clear the "list has been reversed" flag when message_list queue is empty
            self.list_reversed = False
        return message

    def print_message_que(self, pre, not_last_post="", last_post="", txt_file=""):
        """
        Print all messages in que, until message_que list is empty
        :param pre: A control string to be used before printing each line, such as "\t"
        :param not_last_post: A control string to be used after printing all but last line, such as "" or ","
        :param last_post: A control string to be used after printing last line, such as "" or "."
        :param txt_file: if not None, the name of a text file to save results
        :return: No return
        """
        fileflag = False
        while True:
            temp_str = self.pop_message_que()
            if temp_str is not None:
                if not fileflag and txt_file:
                    fileflag = True
                    file = open(txt_file, "a")
                    file.write("\n")
                if len(self.message_list):
                    if fileflag:
                        file.write(pre + temp_str + not_last_post + "\n")
                    print(pre + temp_str + not_last_post)
                else:
                    if fileflag:
                        file.write(pre + temp_str + last_post + "\n")
                    print(pre + temp_str + last_post)
            else:
                break
        if fileflag:
            file.close()


labque = LabQue()
# ----------------------------------------------------


def m2kintro():
    """
    Generate a short introduction to this program
    Print introduction in the run environment
    Push the introduction onto the message queue for display at end of program
    :return: None
    """
    intro_str1 = "Program: M2KScopePlot: v1.02, September 25 2019"
    intro_str2 = "Plot CSV text file data generated by ADALM-2000 Active Learning Module"
    intro_str3 = "Today's date: " + strftime("%A, %B %d %Y", localtime())
    labque.push_message_que(intro_str1)
    labque.push_message_que(intro_str2)
    labque.push_message_que(intro_str3)
    print("\n"+intro_str1 + "\n" + intro_str2)
# ----------------------------------------------------


def system_in_ide():
    """
    Determine if program is running within an IDE
    Used to issue help message related to plt.show()
    Tested IDE's pycharm and Spyder
    :return: inside_ide flag: True if programming running within IDE
    """
    inside_ide = False
    # print(environ)
    if "PYCHARM_HOSTED" in environ:
        # print("\nProgram running within PyCharm IDE")
        inside_ide = True
    elif "SPYDER_ARGS" in environ:
        # print("\nProgram running within Spyder IDE")
        inside_ide = True
    else:
        # This code block tested for python running in Windows CMD prompt, Linux terminal, or python IDLE shell
        pass
    return inside_ide


# Some basic file management utilities -------------------------
def split_file(file):
    """
    Split a data file into its basic three components
    OS agnostic
    :param file: a data file name with a path, base file name, and file extent (such as txt or png)
    :return: file_path, file_base_name, file_extent
    """
    file_path, file_name = path.split(file)
    file_base_name, file_extent = path.splitext(file_name)
    return file_path, file_base_name, file_extent


def combine_file(file_path, file_base_name, file_extent):
    """
    Combine a data file's components into a full data file
    OS agnostic
    :param file_path: path name
    :param file_base_name: base file name
    :param file_extent: file extent (such as txt or png)
    :return: a fully qualified data file
    """
    return path.join(file_path, file_base_name + "." + file_extent)


def list_files(directory, extension):
    return glob(combine_file(directory, '*', extension))
# ----------------------------------------------------


def get_file_info():
    """
    Get valid directory and data file extension where CSV files are located
    Include support for use of ~ (tilde) to reference user's home directory in Windows, Linux, and MacOS
    Example: if ADALM2000 data files are located here ./*.csv, then
            return directory name of ./ and file extension of csv
    :return: a tuple (directory name (str), file extension (str))
    """
    while True:
        e = ''
        # assign path conversion from ~ for Linux, MacOS and Windows operating systems
        # assign user note during directory entry showing support for ~ conversion
        path_str = ""
        note_str = ""
        if name == 'nt':
            note_str = "\n\t" + r"(Note: ~ can be used as C:\Users\<usr> shortcut)"
            path_str = path.expanduser('~')
        elif name == 'posix':
            note_str = "\n\t(Note: ~ can be used as /home/<usr> shortcut)"
            path_str = path.expanduser('~')

        d = input("Enter a directory for ADALM2000 datafile " + note_str + "? ")
        if not d:
            print("Directory cannot be empty. \nTry again...")
            continue
        # unpack special directory token
        if d[0] == "~":
            if not path_str:
                print("~ shortcut not available for: " + name + "\nTry again...")
                continue
            else:
                d = path_str + d[1:]
        if not path.isdir(d):
            print("Directory not found: " + d + "\nTry again...")
            continue

        e = input("Enter file extension (usually CSV or csv) for ADALM2000 datafile? ")
        if list_files(d, e):
            break
        else:
            print("No files found with: " + combine_file(d, '*', e) + " \nTry again...")
            continue
    return d, e
# ----------------------------------------------------


def get_datafile():
    """
    Select an ADALM2000 Oscilloscope data file
    :return: a data file with Oscilloscope data (a csv file in this program's directory by default)
    """

    if name == "nt":
        # use back slashes for directory name on Windows platforms
        dir_default = ".\\TestData"
    else:
        # for Linux, Unix, OSX use forward slashes for directory name
        dir_default = './TestData'
    ext_default = "csv"
    file_name = ""
    while True:
        # prepare a list of files found at a selected directory having a selected file extent
        files = list_files(dir_default, ext_default)
        file_list = []
        for file in files:
            file_list.append(file)

        # allow user to:
        # - select one of the found files,
        # - manually enter a new directory and file
        # - abort this program
        if len(file_list) >= 1:
            print('\nList of datafiles available at ' + combine_file(dir_default, '*', ext_default) + ':')
            i = 0
            default_int = 0
            for file in file_list:
                if i == default_int:
                    default_str = "*"
                else:
                    default_str = " "
                print(i, default_str, '\t', path.basename(file))
                i = i+1
            print("Select datafile (or terminate program):")
            print("\tpress integer for file")
            print("\tpress <enter> to select * default file")
            print("\tpress c to change search")
            print("\tpress a to terminate")
            ans = input("\t?")
            if ans == "":
                ans = str(default_int)
            ans = ans.lower()
            if ans.isdigit() and 0 <= int(ans) < i:
                file_name = file_list[int(ans)]
                break
            elif ans == 'a':
                print("Program terminated")
                sys.exit()
            elif ans != 'c':
                print("\nHelp: print one character followed by <enter> key")
                print("Try again...\n")
                continue

        # change default search
        dir_default, ext_default = get_file_info()
        continue

    return path.join(dir_default, path.basename(file_name))
# ----------------------------------------------------


# pandas file management -----------------------------
def read_pandas_info(nr=7, head=None, er_bad_lines=False):
    while True:
        dat_file = str(get_datafile())
        print("File selected: " + dat_file)
        labque.push_message_que("File selected: " + dat_file)
        # Read info from M2K CSV file
        d_info = ''
        try:
            d_info = pd.read_csv(dat_file, header=head, error_bad_lines=er_bad_lines, nrows=nr)
        except Exception as e:
            print('Read error: pd.read_csv(file, ...')
            print(e)
            print('\n')
            input("Press <enter> to make another selection...")
            continue
        break

    return dat_file, d_info


def read_pandas_data(dat_file, skiprw=7, er_bad_lines=False):
    d_data = pd.read_csv(dat_file, error_bad_lines=er_bad_lines, skiprows=skiprw)
    return d_data
# ----------------------------------------------------


def set_plot_figure():
    # initialize plot's figure width and height in inches
    fw = 0.
    fh = 0.
    plot_size_list = [(6.4, 4.8), (8., 6.), (8., 8.)]

    # allow user to:
    # - select one of the suggested entries,
    # - manually enter a new figure size
    while True:
        print('\nList of suggested plot figure sizes (width, height):')
        i = 0
        default_int = 1
        for plot_size in plot_size_list:
            if i == default_int:
                default_str = "*"
            else:
                default_str = " "
            print(i, default_str, '\t', plot_size[0], ',', plot_size[1])
            i = i + 1
        print("Select plot size in inches:")
        print("\tpress integer for figure size")
        print("\tpress <enter> to select * default size")
        print("\tpress c to change search")
        ans = input("\t?")
        if ans == "":
            ans = str(default_int)
        ans = ans.lower()
        if ans.isdigit() and 0 <= int(ans) < i:
            fw, fh = plot_size_list[int(ans)]
            break
        elif ans != 'c':
            print("\nHelp: print one character followed by <enter> key")
            print("Try again...\n")
            continue

        ans = input('Select desired width of plot in inches: ')
        if 1. < float(ans) < 25.:
            fw = float(ans)
        else:
            print("Desired width entry was out of scope")
            print("Please try again...\n")
            continue
        ans = input('Select desired height of plot in inches: ')
        if 1. < float(ans) < 25.:
            fh = float(ans)
            break
        else:
            print("Desired height entry was out of scope")
            print("Please try again...\n")
            continue
    temp_str = "Plot size selected: (" + str(fw) + ", " + str(fh) + ") in inches"
    print(temp_str)
    labque.push_message_que(temp_str)
    return fw, fh
# ----------------------------------------------------


def load_info_dict(df):
    # info_dict dictionary structure
    # - info_dict[heading](heading title, heading value)
    # - headings:
    #       'scopy' holds scopy software version
    #       'export' holds date when csv data was exported from scopy
    #       'device' holds the abbreviated name of the Analog Devices Active Learning Module ADALM2000
    #       'samples' holds the number of samples for each data channel
    #       'rate' holds the sample rate where sample rate = (Memory depth/time per division) x number of divisions
    #       'tool' holds the tool used during export of the csv file (Only the oscilloscope tool has been tested so far)
    info_dict = {
        'scopy': df.iloc[0],    # example: (';Scopy version', '48fb6a9')
        'export': df.iloc[1],   # example: (';Exported on', 'Wednesday July 24/07/2019')
        'device': df.iloc[2],   # example: (';Device', 'M2K')
        'samples': df.iloc[3],  # example: (';Nr of samples', '8000')
        'rate': df.iloc[4],     # example: (';Sample rate', '1.00E+06')
        'tool': df.iloc[5]      # example: (';Tool', 'Oscilloscope')
    }

    return info_dict
# ----------------------------------------------------


def csv_file_date(csv_date):
    # push CSV Export File date to message que
    words = re.split("[^\\w]", csv_date)
    date_str = "CSV data file generated on: " + words[0] + ", " + words[1] + " " + words[2] + " " + words[-1]
    labque.push_message_que(date_str)
    return date_str
# ----------------------------------------------------


def version_test(ver):
    """
    Test version of Scopy
    When version not found, warn user that behavior of this software has not been tested with the newer version
    Manually check for new version here: https://wiki.analog.com/university/tools/m2k/scopy
    :param ver: Scopy version as reported in ADALM2000 exported csv file
    :return: '' indicates Scopy version has not been tested with this code base
             otherwise return value text built from version key list such as
             'v1.06 May 24, 2019'
    """
    ret_value = ''
    scopy_tested_versions = {'48fb6a9': ['v1.06,', 'May 24 2019'],
                             '6fa2c03': ['v1.1.0', 'Sep 10 2019']}
    if ver not in scopy_tested_versions:
        warning_message = "Warning: this version of Scopy" + \
                          " has not been tested: " + ver
        print("\n" + warning_message)
        labque.push_message_que(warning_message)
        input("Press <enter> to continue...\n")
        labque.push_message_que("Scopy Version (" + ver + "): untested")
    else:
        ret_value = (ret_value+" ").join(scopy_tested_versions[ver])
        labque.push_message_que("Scopy Version (" + ver + "): " + ret_value)
    return ret_value
# ----------------------------------------------------


def generate_plot_title(info_dict):
    plt_title = info_dict['device'][1] + " " + info_dict['tool'][1] + \
                " [" + info_dict['samples'][0] + ": " + str(info_dict['samples'][1]) + \
                ", " + info_dict['rate'][0] + ": " + info_dict['rate'][1] + "]"
    plt_title = plt_title.replace(';', '')
    labque.push_message_que("Plot title: " + plt_title)
    return plt_title
# ----------------------------------------------------


def get_plot_file(data_file):

    # Suggest plot image name based on csv data file name and directory
    fig_path, fig_base_file_name, fig_file_ext = split_file(data_file)
    fig_name_original = combine_file(fig_path, fig_base_file_name, "png")

    # prepare a list of up to 9 suggested file names:
    # - first entry will be the data file name reused as an image file name
    # - additional entries will be crafted as needed to find an unused image file name
    fig_name_list = [fig_name_original]
    fig_note_list = ['']
    i_max = 9
    fig_name = ''
    i_max_note = ''
    replace_file_note = '(Warning: file would be replaced if selected)'
    if path.isfile(fig_name_original):
        fig_note_list[0] = replace_file_note
        i = 0
        while True:
            test_file = path.join(fig_path, fig_base_file_name + "_" + str(i) + "." + "png")
            i += 1
            if i > i_max:
                i_max_note = "Warning: all suggested files already exist"
                break
            elif i <= i_max and path.isfile(test_file):
                fig_name_list.append(test_file)
                fig_note_list.append(replace_file_note)
                continue
            elif i <= 9 and not path.isfile(test_file):
                fig_name_list.append(test_file)
                fig_note_list.append('')
                break

    # allow user to select one of the proposed file names, or allow user to create a new file name manually
    while True:
        print('\nSuggested filenames to save graph results:')
        i = 0
        while i < len(fig_name_list):
            print(i, '\t', fig_name_list[i], '\t', fig_note_list[i])
            i += 1
        if i_max_note:
            print(i_max_note)
        print("Select graph file option:")
        print("\tpress integer for file")
        print("\tpress c to change filename")
        print("\tpress s to skip saving of a graphic file")
        ans = input("\t?")
        ans = ans.lower()
        if ans.isdigit() and int(ans) < len(fig_name_list):
            fig_name = fig_name_list[int(ans)]
            break
        elif ans == 's':
            fig_name = ''
            break
        elif ans != 'c':
            print("\nHelp: print one character followed by <enter> key")
            print("Try again...\n")
            continue

        # change default search
        fig_name = input("Enter full graphic file name with path and extension:")
        tmp_fig_path, tmp_fig_file = path.split(data_file)
        if not path.isdir(tmp_fig_path):
            print("\nError: path does not exist: " + tmp_fig_path)
            input("Press <enter> to try again...")
            continue
        if path.exists(fig_name):
            print("\nWarning: file already exists")
            ans = input("press y to replace file")
            if ans.lower() != 'y':
                break
            else:
                input("Press <enter> to try again...")
                continue
        else:
            break

    if fig_name:
        temp_str = "Plot data saved to file: " + fig_name
    else:
        temp_str = "Plot data not saved to file"
    print(temp_str)
    labque.push_message_que(temp_str)
    return fig_name
# ----------------------------------------------------


def select_channels_to_plot(headings):
    """
    Choose which Y data sets to plot vs time
    :param headings: list of all headings collected from csv file.
                    Example: ['Sample', 'Time(S)', 'CH1(V)', 'CH2(V)', 'M1(V)']
    :return: list of string values to plot.
                    Example: ['Time(S)', 'CH1(V)', 'CH2(V)', 'M1(V)']
    """
    while True:
        iplots_offset = 2
        headings_available_to_plot = []
        selections_available_to_plot = []
        if len(headings) == 3:
            # there is only one channel to plot vs time
            ans = "a"
            headings_available_to_plot = [headings[2]]
        else:
            print("\nList of channels to plot:")

            i = 0
            for title in headings[iplots_offset:]:
                headings_available_to_plot.append(title)
                selections_available_to_plot.append(chr(97 + i))
                print(selections_available_to_plot[i], "=", headings_available_to_plot[i])
                i += 1
            i -= 1
            print("Select channel letters" + " from a to", chr(97 + i), "in desired order followed by <enter>:")
            print("\tor press <enter> to plot all channels in current order ")
            example_str = ""
            default_str = ""
            # prepare example and default entry strings
            for j in range(i + 1):
                example_str += chr(97 + i - j)
                default_str += chr(97 + j)
            print("\texample: " + example_str + "<enter> will plot all channels in reverse order")
            ans = input("\t?")
            # handle default channel section made by just pressing <enter>
            if ans == "":
                ans = default_str
            ans = ans.lower()
        # start headings with time
        headings_to_plot = [headings[1]]
        error_test = False
        for j in range(len(ans)):
            try:
                headings_to_plot.append(headings_available_to_plot[ord(ans[j]) - ord('a')])
            except IndexError:
                input("Invalid heading selection, press <enter> to try again:")
                error_test = True
                break

        if error_test:
            continue
        else:
            break

    temp_str = "List of 'Y-axis' data channels selected to plot:"
    for istr in headings_to_plot[1:]:
        temp_str += " " + istr + ","
    temp_str = temp_str[:-1]
    labque.push_message_que(temp_str)
    return headings_to_plot
