import random

import cocotb
from cocotb import coroutine
from cocotb.clock import Clock
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import BusMonitor, Monitor
from cocotb.triggers import RisingEdge, FallingEdge, Timer, ReadOnly, NextTimeStep

def a_prot_cover(txn):
    pass

def Wx(x):
    return x**3 + (2*(x**2)) + x + 1

# def sb_fn(actual_value):
#     global expected_value
#     assert actual_value == expected_value.pop(0), "Dupa, nie dziala"

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

        




   

@cocotb.test()
async def test_case_classes(dut):

    clock = Clock(dut.in_clock, 10, units="ns")
    await cocotb.start(clock.start())

    global expected_value
    expected_value = []

    dut.axis_s_tvalid.value = 0
    dut.axis_m_tready.value = 1
    dut.axis_s_tdata.value = 0

    await Timer(5, "ns")
    


    in_driver = InputDriver(dut, "axis_s", dut.in_clock)
    slave_monitor = IO_Monitor(dut, name = "axis_s", clock = dut.in_clock)
    master_monitor = IO_Monitor(dut, name = "axis_m", clock = dut.in_clock, callback=Wx)

    for i in range(10):

        x = random.randint(0, 200)
        
        if i == 0:
            x = 0

        expected_value.append(Wx(x))
        
        await in_driver._driver_send(x)




        

