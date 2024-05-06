import pyvisa as visa
import numpy as np
import sys
import time 
# from PyDAQmx import *
from pathlib import Path 

def measure(timestart):
    folder = "LCR-"+time.strftime("%y-%m-%d_%H_%M", time.localtime(timestart)) + "/"
    Path(folder).mkdir(parents=True, exist_ok=True)

    #STANDART LOG RANGE BY LCR meter E4980AL
    freq ='+2.00000E+01,+2.11118E+01,+2.22854E+01,+2.35242E+01,+2.48319E+01,+2.62122E+01,+2.76694E+01,+2.92075E+01,+3.08311E+01,+3.25450E+01,+3.43541E+01,+3.62638E+01,+3.82797E+01,+4.04076E+01,+4.26538E+01,+4.50249E+01,+4.75278E+01,+5.01698E+01,+5.29587E+01,+5.59026E+01,+5.90102E+01,+6.22905E+01,+6.57532E+01,+6.94083E+01,+7.32667E+01,+7.73395E+01,+8.16387E+01,+8.61769E+01,+9.09674E+01,+9.60242E+01,+1.01362E+02,+1.06997E+02,+1.12945E+02,+1.19223E+02,+1.25850E+02,+1.32846E+02,+1.40231E+02,+1.48026E+02,+1.56255E+02,+1.64941E+02,+1.74110E+02,+1.83789E+02,+1.94005E+02,+2.04790E+02,+2.16174E+02,+2.28191E+02,+2.40876E+02,+2.54266E+02,+2.68400E+02,+2.83320E+02,+2.99070E+02,+3.15695E+02,+3.33244E+02,+3.51769E+02,+3.71323E+02,+3.91965E+02,+4.13753E+02,+4.36754E+02,+4.61032E+02,+4.86661E+02,+5.13714E+02,+5.42270E+02,+5.72415E+02,+6.04235E+02,+6.37823E+02,+6.73279E+02,+7.10706E+02,+7.50214E+02,+7.91917E+02,+8.35939E+02,+8.82408E+02,+9.31460E+02,+9.83239E+02,+1.03790E+03,+1.09559E+03,+1.15649E+03,+1.22078E+03,+1.28865E+03,+1.36028E+03,+1.43590E+03,+1.51572E+03,+1.59997E+03,+1.68891E+03,+1.78280E+03,+1.88190E+03,+1.98652E+03,+2.09695E+03,+2.21351E+03,+2.33656E+03,+2.46645E+03,+2.60355E+03,+2.74828E+03,+2.90106E+03,+3.06232E+03,+3.23255E+03,+3.41225E+03,+3.60193E+03,+3.80216E+03,+4.01352E+03,+4.23663E+03,+4.47214E+03,+4.72074E+03,+4.98316E+03,+5.26017E+03,+5.55257E+03,+5.86124E+03,+6.18706E+03,+6.53099E+03,+6.89404E+03,+7.27727E+03,+7.68181E+03,+8.10883E+03,+8.55959E+03,+9.03541E+03,+9.53768E+03,+1.00679E+04,+1.06275E+04,+1.12183E+04,+1.18419E+04,+1.25002E+04,+1.31951E+04,+1.39286E+04,+1.47029E+04,+1.55202E+04,+1.63829E+04,+1.72936E+04,+1.82550E+04,+1.92697E+04,+2.03409E+04,+2.14717E+04,+2.26652E+04,+2.39252E+04,+2.52552E+04,+2.66591E+04,+2.81410E+04,+2.97054E+04,+3.13566E+04,+3.30997E+04,+3.49397E+04,+3.68820E+04,+3.89322E+04,+4.10964E+04,+4.33809E+04,+4.57924E+04,+4.83380E+04,+5.10250E+04,+5.38615E+04,+5.68556E+04,+6.00161E+04,+6.33523E+04,+6.68740E+04,+7.05915E+04,+7.45156E+04,+7.86578E+04,+8.30304E+04,+8.76459E+04,+9.25181E+04,+9.76611E+04,+1.03090E+05,+1.08821E+05,+1.14870E+05,+1.21255E+05,+1.27996E+05,+1.35111E+05,+1.42622E+05,+1.50550E+05,+1.58919E+05,+1.67753E+05,+1.77078E+05,+1.86922E+05,+1.97312E+05,+2.08281E+05,+2.19859E+05,+2.32081E+05,+2.44982E+05,+2.58600E+05,+2.72975E+05,+2.88150E+05,+3.04168E+05,+3.21076E+05,+3.38925E+05,+3.57765E+05,+3.77653E+05,+3.98646E+05,+4.20806E+05,+4.44199E+05,+4.68891E+05,+4.94956E+05,+5.22471E+05,+5.51514E+05,+5.82172E+05,+6.14535E+05,+6.48696E+05,+6.84756E+05,+7.22821E+05,+7.63002E+05,+8.05417E+05,+8.50189E+05,+8.97450E+05,+9.47338E+05,+1.00000E+06'

    #freq = '+1E5, 2E5'

    def query_yes_no(question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = input()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

    t = 2

    LCRoff = np.array([0,0], dtype = np.uint8)
    LCRon = np.array([1,1], dtype = np.uint8)

    # LCRelay = Task()
    # LCRelay.CreateDOChan("/Dev3/port0/line0:1", "", DAQmx_Val_ChanForAllLines)

    # LCRelay.WriteDigitalLines(1, 1, 10.0, DAQmx_Val_GroupByChannel, LCRon, None, None)

    rm = visa.ResourceManager()
    print(rm.list_resources())
    LCR = rm.open_resource('USB0::0x2A8D::0x2F01::MY54408800::0::INSTR')
    LCR.read_termination = '\n'
    LCR.write_termination = '\n'
    LCR.query('*IDN?')
    LCR.timeout = 100000

    print("Connected to: " + LCR.query('*IDN?'))
    LCR.write('*CLS')
    print('*CLS')
    print(LCR.query(':SYSTem:ERRor?'))

    LCR.write(':INITiate:CONTinuous 0')
    print(':INITiate:CONTinuous 0')
    print(LCR.query(':SYSTem:ERRor?'))

    #LCR.write(':TRIG:SOUR INT')

    #LCR.write(':ABOR')
    LCR.write(':AMPL:ALC 1')
    print(':AMPL:ALC 1')
    print(LCR.query(':SYSTem:ERRor?'))
    time.sleep(0.1)

    LCR.write(':APER MED')
    print(':APER SHOR')
    print(LCR.query(':SYSTem:ERRor?'))
    time.sleep(0.1)

    LCR.write(':FUNC:IMP ZTR')
    print(':FUNC:IMP ZTR')
    print(LCR.query(':SYSTem:ERRor?'))
    time.sleep(0.1)

    LCR.write(':LIST:FREQ ' + freq)
    print(':LIST:FREQ ' + freq)
    print(LCR.query(':SYSTem:ERRor?'))
    time.sleep(0.1)
    """
    while not query_yes_no("Please connect the cell that you want to measure. \nIs it connected?", None):
        print()
    """
    print("Script performs sweep of frequencies on a log scale.")

    #vs = [25E-3, 100E-3, 200E-3, 500E-3, 1, 1.5, 2, 10E-3] #To be honest this values were chosen for no real rason

    vs = [0.01, 0.05] #one is enough
    
    print("Preparing the measurement")
    LCR.write(':CORR:LONG')
    time.sleep(0.1)

    LCR.write(':TRIG:SOUR BUS')
    print(':TRIG:SOUR BUS')
    print(LCR.query(':SYSTem:ERRor?'))
    time.sleep(0.1)

    LCR.write(':FORM ASC')
    print(':FORM ASC')
    print(LCR.query(':SYSTem:ERRor?'))
    time.sleep(0.1)

    LCR.write(':FORMat:ASCii:LONG 1')
    print(':FORMat:ASCii:LONG 1')
    print(LCR.query(':SYSTem:ERRor?'))
    time.sleep(0.1)

    LCR.write(':DISP:PAGE LIST')
    print(':DISP:PAGE LIST')
    print(LCR.query(':SYSTem:ERRor?'))
    time.sleep(t)
        
    LCR.write(':LIST:MODE SEQ')
    print(':LIST:MODE SEQ')
    print(LCR.query(':SYSTem:ERRor?'))
    time.sleep(t)



    for v in vs:
        print("Preparing first measurement")
        
        LCR.write(':MEM:CLE DBUF')
        print(':MEM:CLE DBUF')
        #print(LCR.query(':SYSTem:ERRor?'))
        time.sleep(t)
        
        LCR.write(':VOLT ' + str(v))
        print(':VOLT ' + str(v))
        #print(LCR.query(':SYSTem:ERRor?'))
        time.sleep(t)
        
        LCR.write(':MEMory:DIM DBUF,' + str(len(freq)))
        print(':MEMory:DIM DBUF freq')
        #print(LCR.query(':SYSTem:ERRor?'))
        time.sleep(t)
        
        LCR.write(':MEM:FILL DBUF')
        print(':MEM:FILL DBUF')
        #print(LCR.query(':SYSTem:ERRor?'))
        time.sleep(t)
        
        """
        LCR.write(':LIST:CLE:ALL')
        print(':LIST:CLE:ALL')
        print(LCR.query(':SYSTem:ERRor?'))
        time.sleep(t)
        """
        
        #LCR.write(':INITiate:CONTinuous 1')
        #print(':INITiate:CONTinuous 1')
        #print(LCR.query(':SYSTem:ERRor?'))
        #time.sleep(t)
        
        LCR.write(':TRIG')
        print(':TRIG')
        #print(LCR.query(':SYSTem:ERRor?'))
        time.sleep(t)
        
        print("Measuring spectra at "+str(v)+" V")
        
        dataraw= ['+9.90000E+37', '+9.90000E+37', -1, 0]
        i=0
        
        while dataraw[-2] == -1:
            print("at least one try")
            """
            time.sleep(1)
            print("Is it ready?")
            data = LCR.query(':MEM:READ? DBUF').split(',')
            print(':MEM:READ? DBUF')
            print(data)
            print(LCR.query(':SYSTem:ERRor?'))
            i += 1
            """
            try:
                time.sleep(1)
                print("Is it ready?")
                dataraw = LCR.query('FETC?').split(',')
                print(':MEM:READ? DBUF')
                print(data)
                print(LCR.query(':SYSTem:ERRor?'))
                
                print("It is!")
            except:
                pass
      

        time.sleep(0.1)
        
        data = [float(d) for d in dataraw]
        print(data)
        
        np.savetxt(folder + "spectra-"+str(v)+".txt", data)

        time.sleep(0.1)

    LCR.write('TRIG:SOUR INT')
    LCR.write('ABOR')
    LCR.write(':MEM:CLE DBUF')
    LCR.write(':DISP:PAGE MEAS')
    
    LCR.close()


if __name__ == '__main__':
    measure(2021-11-19)