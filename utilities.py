
import cocotb
from cocotb_bus.scoreboard import Scoreboard
from cocotb.clock import Clock
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import BusMonitor
from cocotb.triggers import RisingEdge, Timer


def Wx(x):
    return x**3 + (2*(x**2)) + x + 1

class SlaveDriver(BusDriver):
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
        self.bus.tdata.value = data

        while self.bus.tready.value == 0:
            await Timer(10, "ns")

class MasterDriver(BusDriver):
    _signals = ["tvalid", "tready", "tdata"]

    def __init__(self, entity, name, clock, **kwargs):
        BusDriver.__init__(self, entity, name, clock, **kwargs)
        self.bus.tready.value = 0
        self.bus.tvalid.value = 0
        self.bus.tdata.value  = 0
    
    def set_dut_master_ready(self):
        self.bus.tready.value = 1
        self.bus.tvalid.value = 0
        self.bus.tdata.value  = 0


class SlaveMonitor(BusMonitor):
    
    def __init__(self, entity, clock,
                 name = '',
                 bus_separator='_',
                 signals = ['tvalid', 'tdata', 'tready'],
                 callback = Wx):
        
        self.dut = entity
        self._signals = signals
        BusMonitor.__init__(self, entity, name, clock, bus_separator = bus_separator, callback = None)
        self.clock = clock
        self.tvalid = getattr(self.bus,list(filter(lambda x: 'tvalid' in x, self._signals))[0])
        self.tready = getattr(self.bus,list(filter(lambda x: 'tready' in x, self._signals))[0])
        self.tdata  = getattr(self.bus,list(filter(lambda x: 'tdata' in x, self._signals))[0])

        
    @cocotb.coroutine
    def _monitor_recv(self):
        
        while True:
            yield RisingEdge(self.clock)
            if self.tvalid.value == 1:

                self.log.info(f"{self.name} tvalid {int(self.tvalid)}")
                self.log.info(f"{self.name} tready {int(self.tready)}")
                self.log.info(f"{self.name} tdata {int(self.tdata)}")
                
class MasterMonitor(BusMonitor):
    
    def __init__(self, entity, clock,
                 name = '',
                 bus_separator='_',
                 signals = ['tvalid', 'tdata', 'tready'],
                 callback = Wx):
        
        self.dut = entity
        self._signals = signals
        BusMonitor.__init__(self, entity, name, clock, bus_separator = bus_separator, callback = None)
        self.clock = clock
        self.tvalid = getattr(self.bus,list(filter(lambda x: 'tvalid' in x, self._signals))[0])
        self.tready = getattr(self.bus,list(filter(lambda x: 'tready' in x, self._signals))[0])
        self.tdata  = getattr(self.bus,list(filter(lambda x: 'tdata' in x, self._signals))[0])

        
    @cocotb.coroutine
    def _monitor_recv(self):
        
        while True:
            yield RisingEdge(self.clock)
            if self.tvalid.value == 1:
                self.log.info(f"{self.name} tvalid {int(self.tvalid)}")
                self.log.info(f"{self.name} tready {int(self.tready)}")
                self.log.info(f"{self.name} tdata {int(self.tdata)}")
                assert Wx(int(self.entity.axis_s_tdata.value)) == int(self.entity.axis_m_tdata.value), f"{Wx(int(self.entity.axis_s_tdata.value))} {int(self.entity.axis_m_tdata.value)}"
        


class TbPolynomial(object):
    def __init__(self, dut):
        self.dut = dut
    
    def start_clock(self, clk_period = 10):
        self.dut._log.info("Running clock")
        cocotb.start_soon(Clock(self.dut.in_clock, clk_period,units='ns').start())

class SScoreboard(Scoreboard):
    
    def __init__(self, dut, sb_fun):
        self.dut = dut
        self.sb_fun = sb_fun
        

class Polynomial(TbPolynomial):

    def __init__(self, dut):
        super(Polynomial, self).__init__(dut)

        # dut.axis_m_tready.value = 1
        self.expected_output = []

        self.dut.axis_s_tvalid.value = 0
        self.dut.axis_m_tready.value = 1
        self.dut.axis_s_tdata.value = 0

        self.axis_s_driver = SlaveDriver(self.dut, "axis_s", dut.in_clock)
        self.axis_m_driver = MasterDriver(self.dut, "axis_m", dut.in_clock)
        
        self.axis_s_monitor = SlaveMonitor(self.dut, name = "axis_s", clock = dut.in_clock, callback = self.model)
        self.axis_m_monitor = MasterMonitor(self.dut, name = "axis_m", clock = dut.in_clock)
        
        self.scoreboard = Scoreboard(self.dut)
        self.scoreboard.add_interface(self.axis_m_monitor, self.expected_output)

        self.axis_m_driver.set_dut_master_ready()

        self.dut._log.info(self.scoreboard.log)
    
    
    def model(self, y):
        self.expected_output.append(y)
        # assert 
    
    # def comp(self, s_driver, m_driver):

