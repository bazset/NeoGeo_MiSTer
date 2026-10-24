// SPDX-License-Identifier: GPL-2.0-or-later
// Optional HDMI geometry controls for MiSTer Neo Geo.
// Inspiration: Meathax CRT controls, SIMPLE156 OSMAN:
// https://github.com/meathax/meatsauce/blob/main/cores/simple156/OSMAN.sv
// This HDMI scaler-window implementation is independently written, not a
// direct port or verbatim copy of Meathax CRT HDL.
// Original Neo Geo core: Furrtek and existing MiSTer contributors (retained).
// HDMI integration contributed via BAZSET; native raster/VGA are unchanged.
module hdmi_crt_window (
    input wire [11:0] screen_w, screen_h, base_w, base_h,
    input wire active,
    input wire [4:0] h_size, v_size, h_pos, v_pos,
    output reg [11:0] left, right, top, bottom,
    output reg [3:0] hoverscan, voverscan
);
    integer sw, sh, w, h, x, y, xr, yr;
    always @* begin
        sw = {1'b0,screen_w}; sh = {1'b0,screen_h};
        w = {1'b0,base_w}; h = {1'b0,base_h};
        if(active) begin
            // One size step is 1/64th of the current picture dimension.
            w = w + ((w * $signed(h_size)) >>> 6);
            h = h + ((h * $signed(v_size)) >>> 6);
        end
        // HDMI-only overscan via source cropping in ascal.
        hoverscan = 4'd0; voverscan = 4'd0;
        if(active && sw > 0 && w > sw && !h_size[4]) hoverscan = h_size[3:0];
        if(active && sh > 0 && h > sh && !v_size[4]) voverscan = v_size[3:0];
        if(w < 1) w = 1;
        if(h < 1) h = 1;
        if(w > sw) w = sw;
        if(h > sh) h = sh;
        x = (sw - w) >>> 1; y = (sh - h) >>> 1;
        if(active) begin
            // One position step = 1/128th of HDMI screen dimension.
            x = x + ($signed(h_pos) * (sw >>> 7));
            y = y + ($signed(v_pos) * (sh >>> 7));
        end
        if(x < 0) x = 0;
        if(y < 0) y = 0;
        if(x > sw - w) x = sw - w;
        if(y > sh - h) y = sh - h;
        xr = x + w - 1; yr = y + h - 1;
        left = x[11:0]; right = xr[11:0];
        top = y[11:0]; bottom = yr[11:0];
    end
endmodule
