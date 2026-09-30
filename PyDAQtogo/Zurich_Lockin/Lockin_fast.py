# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 18:19:46 2026
@author: Zhu Zhang
"""

from zhinst.toolkit import Session
import numpy as np



class Zurichlockin:
    def __init__(self, ip, sn, demod_index=0):
        self.session = Session(ip)
        self.device = self.session.connect_device(sn)
        self.demod = self.device.demods[demod_index]
        # Enable demodulator
        self.demod.enable(True)
        # IMPORTANT: set demodulator rate (adjust if needed)
        self.demod.rate(30000)
        # Optional but recommended: set time constant
        # Example: 10 ms
        self.demod.timeconstant(0.01)
        self.node = self.demod.sample
        self.clockbase = self.device.clockbase()

    # -------------------------------------------------
    # Start streaming (call once before scan)
    # -------------------------------------------------
    def start_stream(self):
        self.node.subscribe()
    # -------------------------------------------------
    # Stop streaming (call after scan)
    # -------------------------------------------------
    def stop_stream(self):
        self.node.unsubscribe()
    # -------------------------------------------------
    # Measure one point (core function)
    # -------------------------------------------------
    def measure_point(self, duration=0.2):
        """
        Acquire data for 'duration' seconds and return averaged value.
        """
        data = self.session.poll(duration)
        if self.node not in data:
            return None
    
        sample = data[self.node]
    
        x = sample['x']
        y = sample['y']
    
        if len(x) == 0:
            return None
        r = np.sqrt(x**2 + y**2)
        # Ignore transient
        half = int(len(r) * 0.8)
        #value = np.mean(r[half:])*np.sign(np.mean(y[half:]))
        value = np.mean(y[half:])
    
        return value


