import random

import cocotb
from cocotb.clock import Clock
# from cocotb.triggers import Timer
# from cocotb.scoreboard import Scoreboard
from cocotb.regression import TestFactory
from utilities import SlaveDriver, MasterDriver, SlaveMonitor, MasterMonitor, Polynomial, Wx

   

@cocotb.test()
async def test_primitive(dut):

    clock = Clock(dut.in_clock, 10, units="ns")
    cocotb.start(clock.start())

    # global expected_value
    expected_value = []

    # dut.axis_s_tvalid.value = 0
    # dut.axis_m_tready.value = 1
    # dut.axis_s_tdata.value = 0


    slave_driver = SlaveDriver(dut, "axis_s", dut.in_clock)
    master_driver = MasterDriver(dut, "axis_m", dut.in_clock)


    slave_monitor = SlaveMonitor(dut, name = "axis_s", clock = dut.in_clock)
    master_monitor = MasterMonitor(dut, name = "axis_m", clock = dut.in_clock, callback=Wx)
    
    master_driver.set_dut_master_ready()

    await slave_driver._driver_send(0)

    for _ in range(10):

        x = random.randint(0, 2*16)
        
        await slave_driver._driver_send(x)




async def test(dut):
    
    tb = Polynomial(dut)

    tb.start_clock()

    for _ in range(10):
        x = random.randint(0, 2**16)

        await tb.axis_s_driver._driver_send(x)




factory = TestFactory(test) 
factory.generate_tests()

