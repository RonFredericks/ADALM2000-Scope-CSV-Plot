# -*- coding: utf-8 -*-
"""
File: M2KCustomPlotNULL.py
v 1.01, August 13, 2019
    Initial release
v 1.10, October 12, 2019
	Update method parameters to match new requirements in current main program

A custom plot script
This script demonstrates how to bypass custom script

Author: Ron Fredericks, Ron@BiophysicsLab.com
License: MIT
Copyright 2019 Ron Fredericks, BiophysicsLab.com
See included license file (license.txt) or read it online: https://opensource.org/licenses/MIT
# --------------------------------------------------------------------------------------------

This script is completely contained within a class: CustomPlotScript(object):

    Constructor:
        __init__(self)

    Attributes:
        # flag used by main program to ignore references to custom script
        self.is_custom_script = False

    Methods referenced in main program but ignored within this script:
        get_headings_to_use(self)
        get_is_custom_script(self)
        set_iplot_colors(self, iplot_colors)
        set_df_data(self, df_data)
        set_info_dict(self, info_dict)
        set_headings(self, headings)
        test_custom_plot(self)
        plot_custom_script(self)

Initiate the script by creating an object at the end of this file:
custom_script = CustomPlotScript()
"""


class CustomPlotScript(object):
    """
    A class used to skip custom plotting by main program: M2KScopePlot.py
    """

    def __init__(self):

        # Flag used to control custom script in main program
        self.is_custom_script = False

        # Return a null string when needed by getters
        self.val = ""

    def get_headings_to_use(self):
        return self.val

    def get_is_custom_script(self):
        """
        Flag used within main program to ignore custom plot
        :return: is_custom_script -> bool
            False indicates no custom plot will be used
        """
        return self.is_custom_script

    def set_iplot_colors(self, iplot_colors):
        pass

    def set_df_data(self, df_data):
        pass

    def set_info_dict(self, info_dict):
        pass

    def set_headings(self, headings):
        pass

    def test_custom_plot(self):
        pass

    def plot_custom_script(self, gs, iplot_current):
        pass


# Create custom_script that does nothing

