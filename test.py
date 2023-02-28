import random

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import Timer
from cocotb.scoreboard import Scoreboard
from cocotb.regression import TestFactory
from utilities import InputDriver, IO_Monitor, Polynomial, Wx

   

@cocotb.test()
async def test_case_classes(dut):

    clock = Clock(dut.in_clock, 10, units="ns")
    cocotb.start(clock.start())

    # global expected_value
    # expected_value = []

    dut.axis_s_tvalid.value = 0
    dut.axis_m_tready.value = 1
    dut.axis_s_tdata.value = 0


    in_driver = InputDriver(dut, "axis_s", dut.in_clock)
    slave_monitor = IO_Monitor(dut, name = "axis_s", clock = dut.in_clock)
    master_monitor = IO_Monitor(dut, name = "axis_m", clock = dut.in_clock, callback=Wx)

    await in_driver._driver_send(0)

    for _ in range(10):

        x = random.randint(0, 2*16)

        # expected_value.append(Wx(x))
        
        await in_driver._driver_send(x)


async def test(dut):
    
    tb = Polynomial(dut)
    dut.axis_m_tready.value = 1


    tb.start_clock()

    for _ in range(10):
        x = random.randint(0, 2**16)

        await tb.axis_s_driver._driver_send(x)




factory = TestFactory(test) 
factory.generate_tests()

