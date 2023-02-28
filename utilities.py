
import cocotb
from cocotb.clock import Clock
from cocotb_bus.drivers import BusDriver
from cocotb_bus.monitors import BusMonitor
from cocotb.triggers import RisingEdge, Timer
from cocotb import Scoreboard

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
        

        self.entity.axis_m_tready.value = 1
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


# class Polynomianl()
class TbPolynomial(object):
    def __init__(self, dut):
        self.dut = dut
        self.scoreboard = Scoreboard(dut)
    
    def start_clock(self, clk_period = 10):
        self.dut._log.info("Running clock")
        cocotb.start_soon(Clock(self.dut.in_clock, clk_period,units='ns').start())
    

class Polynomial(TbPolynomial):
    def __init__(self, dut):
        super(Polynomial, self).__init__(dut)

        dut.axis_m_tready.value = 1

        self.dut.axis_s_tvalid.value = 0
        self.dut.axis_m_tready.value = 1
        self.dut.axis_s_tdata.value = 0

        self.axis_s_driver = InputDriver(dut, "axis_s", dut.in_clock)
        self.axis_s_monitor = IO_Monitor(dut, name = "axis_s", clock = dut.in_clock)
        self.axis_m_monitor = IO_Monitor(dut, name = "axis_m", clock = dut.in_clock, callback=Wx)
