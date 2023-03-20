module Wx_sequential(in_clock, axis_s_tvalid, axis_m_tready, axis_s_tdata, axis_m_tdata, axis_m_tvalid, axis_s_tready);

input             in_clock;

output 			  axis_m_tvalid;
output 	   [47:0] axis_m_tdata;
input 			  axis_m_tready;

input             axis_s_tvalid;
input      [15:0] axis_s_tdata;
output 			  axis_s_tready;	

localparam X2 = 1;
localparam X22 = 2;
localparam X3 = 3;
localparam VALID = 4;
localparam RESTART = 5;


wire [48:0] r_a;
wire [48:0] r_b;

wire [47 : 0] result;


assign r_a = (counter == 3'd1) ? x :
			 ((counter == 3'd2) || (counter == 3'd3)) ? x2 :
			 48'd0;

assign r_b = ((counter == 3'd1) || (counter == 3'd3)) ? x :
			 ((counter == 3'd2)) ? 48'd2 :
			 48'd0;

assign result = r_a * r_b;


wire [47:0] ab;
wire [47:0] data;

reg [15:0] x = 16'd0;
reg [31:0] x2 = 32'd0;
reg [32:0] x2_mult_2 = 33'd0;
reg [47:0] x3 = 48'd0;

reg [2:0] counter = 3'd0;
reg data_valid = 1'b0;

always @(posedge in_clock)
begin

		if((counter > 16'd0) & (counter < 16'd4)) begin
			counter <= counter + 3'd1;
		end

		if((axis_s_tvalid == 1'b1) & (counter == 3'd0)) 
			x <= axis_s_tdata;
			counter <= counter + 3'd1;
		
		if (counter == X2) begin
			x2 <= result;

		end else if (counter == X22) begin
			x2_mult_2 <= result;

		end else if (counter == X3) begin
			x3 <= result;

		end else if (counter == VALID) begin
			data_valid <= 1'b1;
		end else if (counter == RESTART) begin
			x2 <= 16'd0;
			x2_mult_2 <= 16'd0;
			x3 <= 16'd0;
			counter <= 3'd0;
			data_valid <= 1'b0;
		end
		
end

assign axis_m_tdata = x3 + x2_mult_2 + x + 16'd1;
assign axis_m_tvalid = ((data_valid == 1'b1) && (axis_m_tready == 1'b1)) ? 1'b1 :
						  1'b0;
assign axis_s_tready = (counter == 3'd0) ? 1'b1 :
					1'b0;
						 
endmodule