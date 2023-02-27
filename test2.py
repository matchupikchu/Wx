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

def sb_fn(actual_value):
    global expected_value
    assert actual_value == expected_value.pop(0), "Dupa, nie dziala"

class InputDriver(BusDriver):
    _signals = ["tvalid", "tready", "tdata"]

    def __init__(self, entity, name, clock, **kwargs):
        BusDriver.__init__(self, entity, name, clock, **kwargs)
        self.bus.tready.value = 0
        self.bus.tvalid.value = 0
        self.bus.tdata.value  = 0
    
    async def _driver_send(self, data, sync=False):

        self.log.info(f"Sending {data}")

        self.bus.tvalid.value = 1
        self.bus.tdata.value = data

        await Timer(10, "ns")
        self.bus.tvalid.value = 0
        self.bus.tdata.value = 0

        while self.bus.tready.value == 0:
            await Timer(10, "ns")


class IO_Monitor(BusMonitor):
    
    def __init__(self, entity, name, clock, callback=Wx):
        self.entity = entity
        self.name = name
        self.clock = clock
        self.callback = callback
        

    async def _monitor_recv(self):


        while self.bus.tvalid.value != 1:
            await RisingEdge(self.clock)
        
        output = self.bus.tdata.value
            
        self._recv(output)
        self.log.info(f"Received {output}")
        




class OutputDriver(BusDriver):
    _signals = ["tvalid", "tready", "tdata"]

    def __init__(self, dut, name, clk, sb_callback):
        BusDriver.__init__(self, dut, name, clk)
        self.bus.tready.value = 1
        self.clk = clk
        self.callback = sb_callback
        self.append(0)

    async def _driver_send(self, value, sync=True):
        while True:
            # for i in range(5):
            #     await RisingEdge(self.clk)
            # if self.bus.tvalid.value != 1:
            #     await RisingEdge(self.bus.tvalid)

            while self.bus.tvalid.value != 1:
                await RisingEdge(self.clk)
            
            # await ReadOnly()
            self.callback(self.bus.tdata.value)
            await RisingEdge(self.clk)
            # await NextTimeStep
            self.bus.tvalid.value = 0


   

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
    IO_Monitor(dut, "axis_m", dut.in_clock, callback=Wx)
    OutputDriver(dut, "axis_m", dut.in_clock, sb_fn)

    for i in range(10):

        x = random.randint(0, 200)
        
        if i == 0:
            x = 0

        expected_value.append(Wx(x))
        
        await in_driver._driver_send(x)

    # while len(expected_value) > 0:
    #     await Timer(20, "ns")


        

