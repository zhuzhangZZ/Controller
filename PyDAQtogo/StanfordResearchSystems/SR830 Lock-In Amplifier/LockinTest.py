

#%%

import SRSLockinAmplifier_Driver as SRS

# import autoUL
import numpy as np
import time
try:
    lockin = SRS.SR830(COMPort='ASRL8::INSTR', timeout=5000)
except:
    print("The SR830 is alreday opended!")
lockin.CLS()       
# lockin.control(control = 'remote')

lockin.reference_source(ref_source="internal")
lockin.frequency(freq = 10.6)
lockin.reference_phase_shift(ref_phase=0)
lockin.sine_output_amplitude(ref_amp= 0.1)
lockin.reference_trigger(ref_tri = 'TTL_f')

lockin.input_config(input_value= "A")
# lockin.lockin.write("ISRC 1") 
lockin.input_coupling(coupling_value="AC")
lockin.input_shield(shield_value= "float")
lockin.input_filter(filter_value= "0-0")


lockin.time_constant(Tc = "1 ms")
lockin.sensitivity(sen = '200 mV/nA')
lockin.filter_slope(filter_slope= "24")
lockin.reserve_mode(reserve_mode= "normal")
lockin.sync_filter(sync_filter="True")
lockin.CH1_display(display1= "R")
lockin.out_offset_exp(output='R')
lockin.CH2_display(display2= "Theta")

lockin.front_output1(output1="display")
lockin.front_output2(output2="display")



#%%
## Get data from lockin

import PyDAQtogo.config as config

configfile = config.find_configfile("config_Zhu.yml")
param = config.read_config(configfile)

param['Lock-in']['input_config']=lockin.query_input_config()  ## this is an example of reading from a dictionary, fill in the rest as necessary
param['Lock-in']['input_coupling']=lockin.query_input_coupling()
param['Lock-in']['input_shield']=lockin.query_input_shield()
param['Lock-in']['input_filter']=lockin.query_input_filter()

param['Lock-in']['time_constant']=lockin.query_time_constant()
param['Lock-in']['sensitivity']=lockin.query_sensitivity()
param['Lock-in']['filter_slope']=lockin.query_filter_slope()
param['Lock-in']['reserve_mode']=lockin.query_reserve_mode()
param['Lock-in']['sync_filter']=lockin.query_sync_filter()

param['Lock-in']['frequency']=lockin.query_frequency()
param['Lock-in']['reference_source']=lockin.query_reference_source()
param['Lock-in']['reference_trigger']=lockin.query_reference_trigger()
param['Lock-in']['harm']=lockin.query_harm()

savefolder = 'D:\\OneDrive - Universiteit Utrecht\\Gizmo\\config\\config_Zhu_test.yml'
config.save_config( param,savefolder)

lockin.query_sample_rates()

lockin.control(control= 'remote')
lockin.query_control()
lockin.control(control= 'lockloc')
lockin.close()

#%%
lockin.sample_rates(SR = "512 Hz")
#Set (Query) the Data Scan Mode to 1 Shot (0) or Loop (1).
lockin.lockin.write("SEND 1")
#Set (Query) the Trigger Starts Scan modeto No (0) or Yes (1)
lockin.lockin.write("TSTR 0")
#Reset the scan. All stored data is lost.
lockin.lockin.write("REST")
##Start or continue a scan. 
lockin.lockin.write("STRT")
time.sleep(1)
length = lockin.lockin.query("SPTS?")
lockin.lockin.write("PAUS")
start =0
channel =1
R = lockin.lockin.query("OUTP? 1")
time_st = time.time()

X = lockin.lockin.query(('TRCA? {},{},{}'.format(channel, start, length)))
timet = time.time()
print(timet-time_st)
x = np.fromstring(X, sep=',')
Y= lockin.lockin.query(('TRCA? {},{},{}'.format(2, start, length)))
y = np.fromstring(Y, sep=',')


fig, ax = plt.subplots(figsize=(9,5))

ax.plot(x)
ax1 = ax.twinx()
ax1.plot(y)
ax1.set_ylim(-180,180)
buffersize = 16.3E3
samplerate =512
datatime =2
maxtime = buffersize/samplerate
transferrate =19.2e3
datasize = int(length)
transfertime = datasize*154.76/transferrate
#%%

import lantz.drivers.stanford_rs.sr830 as SRS


lockin = SRS.SR830('ASRL3::INSTR', baud_rate = 19200)
lockin.initialize()
lockin.write("FREQ 2000")
lockin.frequency= 200
lockin.write("*CLS?")
lockin.input_coupling
print(lockin.idn)
lockin.read_bytes(1)
"""==============INPUT and FILTER COMMANDS===============
   +++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
lockin.input_configuration="A" #set input channle 
lockin.input_coupling="AC" # sets the  input  coupling 
lockin.input_shield='ground' # sets  input  shield  grounding
lockin.input_filter # sets input  line  notch  filter  status 0: none

"""==============GAIN and TIME CONSTANT COMMANDS==========
   +++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
# set time constant
lockin.time_constants="1 s"
lockin.time_constants
# set the sensitivity
lockin.sensitivity="100 mV/nA"
# sets or queries the reserve mode
lockin.reserve_mode = "high"
# set or  queries  the  low  pass  filter  slope
lockin.filter_db_per_oct = 24

# ets  or  queries  the  synchronous  filter  status.
lockin.sync_filter=False

"""==============DISPLAY and OUTPUT COMMANDS=============
   ++++++++++++++++++++++++++++++++++++++++++++++++++++++"""
# selects the CH1 and CH2 what to displays: X, R; Y thata...; 0: raito
lockin.display[1]=  (1, 0)
lockin.display[2] = (1, 0)

#output sources from 0:Display or 1: X, Y 

lockin.front_output[1] = "display"
# lockin.front_output=(channel= 2, value= 0)


lockin.reference_internal=True
lockin.finalize()



#%%
from SRS830Lockin_Driver import SR830
import visa
import math
import matplotlib.pyplot as plt
import time
import csv
import datetime

######################################################################
# Connect to the lock-in amplifier
######################################################################

# connect to the SR830 Lock In Amplifier
sr830 = SR830()
sr830.connect("ASRL3::INSTR")
# Enable debug output so we see the commands that are sent to the instrument
sr830.enable_debug_output()
# Reset the device
#sr830.reset()


######################################################################
# Setup of the SR830 Lock-in Amplifier
######################################################################

sr830.use_internal_reference()

# disable line filters
sr830.disable_line_filters()
#sr830.enable_line_filters()

# set the input to measure 
#sr830.set_input_mode_A_1uA()
sr830.set_input_mode_A()
sr830.set_input_shield_to_floating()
sr830.set_input_coupling_ac()

# set the reserve
#sr830.set_reserve_low_noise()
sr830.set_reserve_normal()


# set the displays to interesting things
sr830.display_ch1_r()
sr830.display_ch2_phi()

######################################################################
# define the parameters for the measurement
######################################################################


amplitude = 0.004
sr830.set_sine_output_level(amplitude)
#sr830.set_reference_frequency(freq)

 # define the sweep parameters
f_start = 1000
f_stop =  100000
f_step = 1000       
delay = 3


# define variables we store the measurement in
data_impedance = []                # impedance
#data_BiasVoltage = []            # Bias voltage we set
data_phi = []                       # phaseshift
#data_1_over_C_squared = []  # to save one over Capacity^2
freq = []                               # frequency

# Creat unique filenames for saving the data
time_for_name = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S")
filename_csv = 'semshort' + time_for_name +'.csv'
filename_pdf = 'semshort' + time_for_name +'.pdf'

# Header for csv
with open(filename_csv, 'a') as csvfile:
        writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
#       writer.writerow(["f / Hz :" , str(freq)])
        writer.writerow(["Ue / V :" , str(amplitude)])
        writer.writerow(["Frequency / Hz" , "Impedance / Ohm", "Phase / Â°"])

# Some parameters for the SR830
sr830.set_time_constant(0.1)
sr830.set_sensitivity(1)
sr830.set_reference_frequency(f_start)
time.sleep(delay)


######################################################################
# step through the frequencies
######################################################################

# positive sweep
steps = int((f_stop - f_start)/f_step)
for nr in range(steps):
    f = f_start + nr * f_step
    sr830.set_reference_frequency(f)
    time.sleep(1)
    # read the data from the SR830
    value_r = sr830.read_r()
    phi = sr830.read_phi()
    #sr830.set_sensitivity(2*value_r)
    # calculate the capacity
    # if clause in case of opern circuit measure with I = 0 A
    if (value_r != 0):
        freq.append(f)
        Z = amplitude/value_r
        data_impedance.append(Z)
        data_phi.append(phi)

        # Write the data in a csv
        with open(filename_csv, 'a') as csvfile:
            writer = csv.writer(csvfile, delimiter=';',  lineterminator='\n')
            writer.writerow([f, Z, phi])


######################################################################
# Plot the Data and save the figure as a .pdf
######################################################################

# plot the data
f, fig = plt.subplots(2, sharex = True)
fig[0].plot(freq, data_impedance,'o-')
fig[1].plot(freq, data_phi,'*')

# set labels and a title
plt.xlabel('Frequency / Hz')
plt.axes(fig[0])
plt.ylabel('Z / Ohm')
plt.axes(fig[1])
plt.ylabel('Phi / Â°')
#plt.title('Characteristic curve of a diode')

plt.savefig(filename_pdf)
plt.show()


######################################################################
# Clean up
######################################################################

# reset and disconnect the SR830
sr830.reset()
sr830.disconnect()




