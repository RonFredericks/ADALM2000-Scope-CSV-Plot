# ADALM2000-Scope-CSV-Plot
Plot oscilloscope trace results generated from Analog Devices ADALM2000 Advanced Learning Module CSV export files

Setup:
1) Insure the following libraries are available: matplotlib, numpy, pandas, sys, os, time, re, glob, and
                                                scipy (when using M2KCustomPlotFFT or M2KCustomePlotButter)
2) To generate CSV files you will need ADALM2000 hardware and Scopy multi-functional software toolset for signal analysis. 

Usage:
1) Save a csv export file from Scopy Oscilliscope tool, the open-source program used with the ADALM2000 hardware.
2) Review custom scripts available if desired (FFT or Buttworth Filters), default is to ignore these.
3) Generate a CSV file from Scopy software tool, or use the ones supplied with this distribution under TestData folder.
4) Launch main script M2KScopePlot.py to run program: 
4-a) From terminal (such as Anaconda Prompt or IDLE): "python M2KScopePlot.py"
4-b) From IDE (such as PyCharm or Spyder): execute M2KScopePlot.py

Platforms Tested:
1) Python 3.6 on Microsoft Windows 10
2) Python 3.7 on Ubuntu Linux 18.10 (cosmic)

References:
1) ADALM2000 https://www.analog.com/en/design-center/evaluation-hardware-and-software/evaluation-boards-kits/ADALM2000.html
2) Scopy https://wiki.analog.com/university/tools/m2k/scopy
3) Sample usage: http://www.biophysicslab.com/2019/09/09/experimentation-with-analog-devices-adalm2000/
