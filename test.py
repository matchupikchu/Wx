import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer

from utilities import InputDriver, IO_Monitor, Wx
   

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




        

