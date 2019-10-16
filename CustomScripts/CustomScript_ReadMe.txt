File: CustomScript_ReadMe.txt
Purpose: Describe the struction of custom scripts for creation of new signal processing assets
Author: Ron at BiophysicsLab.com
Initial Date: 10/14/2019

The basic structure is outlined in the bare bones custom script M2KCustomPlotNULL.py.
Fill out the various methods and add the main processing for the new asset to plot_custom_script(self, gs, iplot_current) where gs represents a gridspec.GridSpec option to tile plots, and iplot_current is the row for the custom script plot's gridspec entry.

The class name for a new custom script should remain the same as the current scripts: CustomPlotScript.

The custom scripts follow this code structure to support new scripts as they are developed as seen in the main program: M2KScopePlot.py

# Select, import, and instantiate a custom script, use the null script as a place holder for no custom script
script, param_lst = select_custom_script(config, headings2Plot, info_dict['rate'][1])
script_name = config.get('CustomScript Names', script)
# Ref: https://stackoverflow.com/questions/547829/how-to-dynamically-load-a-python-class
module = importlib.import_module('CustomScripts.'+script_name)
my_class = getattr(module, 'CustomPlotScript')
custom_script = my_class(*param_lst)
