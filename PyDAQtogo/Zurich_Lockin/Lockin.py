from zhinst.toolkit import Session
import numpy as np
import time
from TEST import variables

class Zurichlockin:
    def __init__(self, ip, sn):
        self.ip = ip
        self.sn = sn
        self.session = Session(ip)
        self.device = self.session.connect_device(sn)
        self.sum2value = 0
        self.sumnot2value=0

        self.device.demods[0].enable(True)

        self.sample_nodes = [
            #self.device.demods[0].sample.r
            #self.device.demods[0].sample.x
            self.device.demods[0].sample.y
        ]


        self.TOTAL_DURATION = 2 # [s]
        self.SAMPLING_RATE = 250000 # Number of points/second 2500000
        self.BURST_DURATION = 0.1 # Time in seconds for each data burst/segment.

        self.num_cols = int(np.ceil(self.SAMPLING_RATE * self.BURST_DURATION))
        self.num_bursts = int(np.ceil(self.TOTAL_DURATION / self.BURST_DURATION))

        self.daq_module = self.session.modules.daq
        self.daq_module.device(self.device)
        self.daq_module.type(0) # continuous acquisition
        self.daq_module.grid.mode(2)
        self.daq_module.count(self.num_bursts)
        self.daq_module.duration(self.BURST_DURATION)
        self.daq_module.grid.cols(self.num_cols)

        self.daq_module.save.fileformat(1)
        self.daq_module.save.filename('zi_toolkit_acq_example')
        self.daq_module.save.saveonread(1)

        for node in self.sample_nodes:
             self.daq_module.subscribe(node)

        self.clockbase = self.device.clockbase()
        self.ts0 = np.nan
        self.timeout = 2
        self.start_time = time.time()
        self.results = {x: [] for x in self.sample_nodes}
        self.value = np.zeros((1, self.num_cols))
        self.Ready=False


        self.t=0
        self.valueAvg = np.zeros(self.num_bursts)
        self.j=0
        self.ExpPoint = 0
        variables.k = 0
        variables.i = 0



    def read_and_plot_data(self):
        daq_data = self.daq_module.read(raw=False, clk_rate=self.clockbase)
        #progress = self.daq_module.raw_module.progress()[0]

        for node in self.sample_nodes:
            # Check if node data available
            if node in daq_data.keys():
                for sig_burst in daq_data[node]:
                    self.results[node].append(sig_burst)
                    if np.any(np.isnan(self.ts0)):
                      self.ts0 = sig_burst.header['createdtimestamp'][0] / self.clockbase
                    # Convert from device ticks to time in seconds.
                    self.t0_burst = sig_burst.header['createdtimestamp'][0] / self.clockbase
                    self.t = (sig_burst.time + self.t0_burst) - self.ts0
                    self.value = sig_burst.value[0, :]
                    #### FOR TESTING PURPOSES ######
                    i=0

                    while i<self.num_cols:
                        self.valueAvg[self.j] = self.valueAvg[self.j] + self.value[i]
                        i+=1
                    self.valueAvg[self.j] = self.valueAvg[self.j]/self.num_cols

                    self.j+=1

    def read_and_plot_data_real(self): #used for realtimescan, uses the infinite while loops while waiting for the delay stage to be set
        daq_data = self.daq_module.read(raw=False, clk_rate=self.clockbase)
        progress = self.daq_module.raw_module.progress()[0]

        for node in self.sample_nodes:
            # Check if node data available
            if node in daq_data.keys():
                for sig_burst in daq_data[node]:
                    start_time = time.time()
                    while variables.k != variables.i:
                        if time.time()>start_time+2:
                            break
                        continue
                    if variables.k==1000000000:
                        break
                    self.results[node].append(sig_burst)
                    if np.any(np.isnan(self.ts0)):
                        self.ts0 = sig_burst.header['createdtimestamp'][0] / self.clockbase
                    # Convert from device ticks to time in seconds.
                    self.t0_burst = sig_burst.header['createdtimestamp'][0] / self.clockbase
                    self.t = (sig_burst.time + self.t0_burst) - self.ts0
                    self.value = sig_burst.value[0, :]
                    variables.k = variables.k + 1
                    i = 0
                    while i < self.num_cols:
                        self.valueAvg[self.j] = self.valueAvg[self.j] + self.value[i]
                        i += 1
                    self.valueAvg[self.j] = self.valueAvg[self.j] / self.num_cols
                    self.j += 1
    def presentdata(self):
        self.Ready = False
        self.num_cols = int(np.ceil(self.SAMPLING_RATE * self.BURST_DURATION))
        self.num_bursts = int(np.ceil(self.TOTAL_DURATION / self.BURST_DURATION))

        self.daq_module = self.session.modules.daq
        self.daq_module.device(self.device)
        self.daq_module.type(0) # continuous acquisition
        self.daq_module.grid.mode(2)
        self.daq_module.count(self.num_bursts)
        self.daq_module.duration(self.BURST_DURATION)
        self.daq_module.grid.cols(self.num_cols)
        self.clockbase = self.device.clockbase()
        self.ts0 = np.nan
        self.timeout = 10
        #    self.start_time = time.time()
        self.results = {x: [] for x in self.sample_nodes}
        self.value = np.zeros((1, self.num_cols))

        self.t=0
        self.valueAvg = np.zeros(self.num_bursts)
        self.j=0
        self.ExpPoint = 0


        self.start_time = time.time()
        self.ExpPoint=0


        # Start recording data
        self.daq_module.execute()

        self.Ready=True
        while time.time() - self.start_time < self.timeout:
            self.read_and_plot_data()
            if self.daq_module.raw_module.finished():
                 # Once finished, call once more to get the potential remaining data.
                self.read_and_plot_data()
                break


            time.sleep(self.BURST_DURATION)
       # print(self.valueAvg)
        i = 0
        while i<self.num_bursts:
            self.ExpPoint = self.ExpPoint + self.valueAvg[i]
            i+=1

        self.ExpPoint = self.ExpPoint/self.num_bursts
        self.j=0
      #  self.daq_module.save.save.wait_for_state_change(0, timeout=100)
        return self.ExpPoint

    def presentdatareal(self): #used for realtimescan, uses the infinite while loops while waiting for the delay stage to be set
        self.Ready = False
        self.BURST_DURATION=0.1
        self.num_cols = int(np.ceil(self.SAMPLING_RATE * self.BURST_DURATION))
        self.num_bursts = int(np.ceil(self.TOTAL_DURATION / self.BURST_DURATION))

        self.daq_module = self.session.modules.daq
        self.daq_module.device(self.device)
        self.daq_module.type(0) # continuous acquisition
        self.daq_module.grid.mode(2)
        self.daq_module.count(self.num_bursts)
        self.daq_module.duration(self.BURST_DURATION)
        self.daq_module.grid.cols(self.num_cols)
        self.clockbase = self.device.clockbase()
        self.ts0 = np.nan
        self.timeout = 100000
        #    self.start_time = time.time()
        self.results = {x: [] for x in self.sample_nodes}
        self.value = np.zeros((1, self.num_cols))

        self.t=0
        self.valueAvg = np.zeros(self.num_bursts)
        self.j=0
        self.ExpPoint = 0


        self.start_time = time.time()
        self.ExpPoint=0


        # Start recording data
        self.daq_module.execute()

        self.Ready=True
        while time.time() - self.start_time < self.timeout:
            self.read_and_plot_data_real()
            if self.daq_module.raw_module.finished():
                 # Once finished, call once more to get the potential remaining data.
                self.read_and_plot_data_real()
                break


            time.sleep(self.BURST_DURATION)
        i = 0
        while i<self.num_bursts:
            self.ExpPoint = self.ExpPoint + self.valueAvg[i]
            i+=1

        self.ExpPoint = self.ExpPoint/self.num_bursts
        self.j=0
        #self.daq_module.save.save.wait_for_state_change(0, timeout=1)
        return self.ExpPoint

if __name__ == "__main__":
    Experiment = Zurichlockin("192.168.10.10", "dev7344")
    Zurichlockin.presentdata(Experiment)
