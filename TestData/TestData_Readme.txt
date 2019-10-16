File: TestData_Readme.txt
Date: 10/5/2019
Purpose: Describe scopy oscilloscope exported csv test data


Scopy Oscilloscope CSV Export Files
=======================================================================================================

For Lab1 details see this blog post:
http://www.biophysicslab.com/2019/09/09/experimentation-with-analog-devices-adalm2000/

Lab1_Sine_1kHz.csv		CH1(V) is input, CH2(V) Output, M1(V) is CH2(V)-CH1(V) showing difference 
								between input and output op-amp signals
Lab1_Square_7kHz.csv		CH1(V) is input, CH2(V) Output from op-amp showing slew rate performance


MakeWaves.py Generated CSV Export Files (clean noise free signals simulating scopy oscilloscope export)
=======================================================================================================

The MakeWaves.py python tool is available in the ./Tools/SignalAndTest/ subdirectory

data_1SquareWave.csv		CH1(V) - clean 5 Hz square wave
data_2SineWaves.csv		CH1(V) - clean superposition of two sine waves at 5 and 10 Hz


M2KScopePlot.py Result Files
=======================================================================================================

Lab1_Sine_1kHz.png		CH1(V), CH2(V), M1(mV) plot vs Time(mS)
Lab1_Sine_1kHz.txt		Auto generated lab report showing plot selections and results

Lab1_Square_7kHz.png		CH1(V) and CH2(V) plot vs Time(mS) with CH1(V) FFT plot
Lab1_Square_7kHz.txt		Auto generated lab report showing plot selections and results
   
data_1SquareWave.png		CH1(V) plot vs Time(mS) along with FFT plot
data_1SquareWave.txt		Auto generated lab report showing plot selections and results

data_2SineWaves.png		CH1(V) plot vs Time(mS) along with Butterworth Filter and Response plots
data_2SineWaves.txt		Auto generated lab report showing plot selections and results



