SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += Wx_sequential.v
VERILOG_SOURCES += Wx_sequential_wrapper.v


Wx:
	rm -rf sim_build
	$(MAKE) sim MODULE=test TOPLEVEL=Wx_sequential_wrapper

include $(shell cocotb-config --makefiles)/Makefile.sim
