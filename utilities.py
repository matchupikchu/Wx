import random

import cocotb
from cocotb.regression import TestFactory
from cocotb.clock import Clock
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import BusMonitor, Monitor
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ReadOnly, NextTimeStep

def Wx(x):
    return x**3 + (2*(x**2)) + x + 1

class InputDriver(BusDriver):
    _signals = ["tvalid", "tready", "tdata"]

    def __init__(self, entity, name, clock, **kwargs):
        BusDriver.__init__(self, entity, name, clock, **kwargs)
        self.bus.tready.value = 0
        self.bus.tvalid.value = 0
        self.bus.tdata.value  = 0
    
    async def _driver_send(self, data, sync=False):

        self.log.info(f"Sending x = {data}")
        self.log.info(f"Expected value of W(x) {Wx(data)}")
        

        self.bus.tvalid.value = 1
        self.bus.tdata.value = data

        await Timer(10, "ns")
        self.bus.tvalid.value = 0
        self.bus.tdata.value = 0

        while self.bus.tready.value == 0:
            await Timer(10, "ns")


class IO_Monitor(BusMonitor):
    
    def __init__(self, entity, clock,
                 name = '',
                 bus_separator='_',
                 signals = ['tvalid', 'tdata', 'tready'],
                 callback = Wx):
        
        self._signals = signals
        BusMonitor.__init__(self, entity, name, clock, bus_separator = bus_separator, callback = None)
        self.clock = clock
        self.axis_m_tvalid = getattr(self.bus,list(filter(lambda x: 'tvalid' in x, self._signals))[0])
        self.axis_m_tready = getattr(self.bus,list(filter(lambda x: 'tready' in x, self._signals))[0])
        self.axis_m_tdata  = getattr(self.bus,list(filter(lambda x: 'tdata' in x, self._signals))[0])

        
    @cocotb.coroutine
    def _monitor_recv(self):
        while True:
            yield RisingEdge(self.clock)

            if self.axis_m_tvalid.value:
                self.log.info(f"Received W(x) = {int(self.axis_m_tdata)}")