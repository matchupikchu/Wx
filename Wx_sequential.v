// module multiplier_16_bit(in_a, in_b, out_c);

// input 	[15:0] in_a;
// input 	[15:0] in_b;
// output 	[15:0] out_c;

// reg [15:0] c;

// always @(in_a or in_b)
// begin
// 	c <= in_a * in_b;
// end

// assign out_c = c;

// endmodule


module Wx_sequential(in_clock, axis_s_tvalid, axis_m_tready, axis_s_tdata, axis_m_tdata, axis_m_tvalid, axis_s_tready);

input             in_clock;
input             axis_s_tvalid;
input 			  axis_m_tready;
input      [15:0] axis_s_tdata;
output 	   [47:0] axis_m_tdata;
output 			  axis_m_tvalid;
output 			  axis_s_tready;	

reg [48:0] r_a = 16'd0;
reg [48:0] r_b = 16'd0;
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
		
		if (counter == 3'd1) begin
			r_a <= x;
			r_b <= x;
			x2 <= x * x;

		end else if (counter == 3'd2) begin
			r_a <= x2;
			r_b <= 48'd2;
			x2_mult_2 <= 2 * x2;

		end else if (counter == 3'd3) begin
			r_a <= x2;
			r_b <= x;
			x3 <= x2 * x;

		end else if (counter == 3'd4) begin
			data_valid <= 1'b1;
		end else if (counter == 3'd5) begin
			r_a <= 16'd0;
			r_b <= 16'd0;
			x2 <= 16'd0;
			x2_mult_2 <= 16'd0;
			x3 <= 16'd0;
			counter <= 3'd0;
			data_valid <= 1'b0;
		end
		
end

// multiplier_16_bit mult
//     (
// 		  .in_a(r_a),
// 		  .in_b(r_b),
// 	      .out_c(ab)
//     );

assign axis_m_tdata = x3 + x2_mult_2 + x + 16'd1;
assign axis_m_tvalid = ((data_valid == 1'b1) && (axis_m_tready == 1'b1)) ? 1'b1 :
						  1'b0;
assign axis_s_tready = (counter == 3'd0) ? 1'b1 :
					1'b0;
						 
endmodule