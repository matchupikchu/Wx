module Wx_sequential_wrapper(in_clock, axis_s_tvalid, axis_m_tready, axis_s_tdata, axis_m_tdata, axis_m_tvalid, axis_s_tready);

output      reg    in_clock;
input             axis_s_tvalid;
input 			  axis_m_tready;
input   signed    [15:0] axis_s_tdata;
output 	signed    [47:0] axis_m_tdata;
output 			  axis_m_tvalid;
output 			  axis_s_tready;	
  Wx_sequential dut(
	  .in_clock(in_clock),
	  .axis_s_tvalid(axis_s_tvalid),
	  .axis_m_tready(axis_m_tready),
	  .axis_s_tdata(axis_s_tdata),
	  .axis_m_tdata(axis_m_tdata),
	  .axis_m_tvalid(axis_m_tvalid),
	  .axis_s_tready(axis_s_tready)
  );

  initial begin
	  $dumpfile("Wx_sequential.vcd");
	  $dumpvars;
	  in_clock=0;
	  forever begin
		  #5 in_clock=~in_clock;
	  end
  end
  endmodule
