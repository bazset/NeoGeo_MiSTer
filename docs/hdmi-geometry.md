# Optional HDMI geometry adjustment

## Credits and provenance

This change builds upon the **existing Neo Geo MiSTer core**; it is not a new
Neo Geo FPGA implementation.

- **Original Neo Geo FPGA core:** [Furrtek](https://www.patreon.com/furrtek/posts),
  as credited in the upstream [README](../README.md).
- **MiSTer Neo Geo maintenance and existing HDL/infrastructure:**
  [MiSTer-devel/NeoGeo_MiSTer contributors](https://github.com/MiSTer-devel/NeoGeo_MiSTer/graphs/contributors).
  All existing notices and credits are retained.
- **Existing MiSTer scaler and video framework:** original authors/contributors.
  The existing sys/video_freak.sv copyright notices include Grabulosaure
  and Alexey Melnikov; these notices are preserved.
- **CRT geometry feature inspiration and special thanks: Meathax.**
  [SIMPLE156 OSMAN source](https://github.com/meathax/meatsauce/blob/main/cores/simple156/OSMAN.sv)
  and [meatsauce repository](https://github.com/meathax/meatsauce)
  demonstrate user-adjustable CRT geometry controls and motivated the HDMI
  size/position OSD experience here.
- **Neo Geo HDMI integration/PR preparation:** BAZSET (@bazset).
  This change wires new OSD options into the existing scaler and supplies
  an HDMI destination-window calculation and optional overscan crop.
  **It does not claim authorship of the original core or Meathax work.**

**Code provenance:** This PR implements the HDMI adjustment behavior independently.
It is **not a direct HDL port** of the Meathax SIMPLE156 CRT module,
which uses different video timing. No Meathax HDL was copied in this change.
Credit is given explicitly for feature inspiration.

## Controls

Enable **HDMI Geometry** in Audio & Video, then adjust:

| Option | Action |
| --- | --- |
| HDMI H-Size | Increase/decrease HDMI picture width |
| HDMI V-Size | Increase/decrease HDMI picture height |
| HDMI H-Position | Move the HDMI picture left/right |
| HDMI V-Position | Move the HDMI picture up/down |

All offsets default to zero and the feature defaults **Off**, preserving
upstream scaler sizing. Adjustments operate on HDMI scaler output, not
native Neo Geo timing or analog VGA/direct-video.

Size steps change the destination size by approximately 1/64 (1.56%) per
increment; position uses 1/128 of HDMI canvas size. Signed OSD values
span -16 to +15. Bounds clamp to the HDMI canvas, so movement is limited
when the picture fills that axis. Optional scaler source crop allows
overscan when scaling reaches the canvas edge.

## Changed files

- neogeo.sv: optional OSD controls and expanded status field.
- sys/emu_ports.vh: core-platform geometry wires.
- sys/hdmi_crt_window.sv: destination geometry and overscan flags.
- sys/sys_top.v: HDMI scaler integration and direct-video bypass.
- sys/ascal.vhd: conditional auto-input overscan cropping.
- sys/sys.qip: include the new module.
- tests/test_hdmi_crt.py: model-based checks and RTL wiring assertions.

## Validation and limitations

- **Hardware:** contributor reports the B01 RBF works on MiSTer FPGA.
  Broader mode-by-mode regression testing is still recommended.
- **Quartus:** Prime Lite 17.0.2 full compile, 0 errors, 95 warnings.
  This is not timing closure.
- **TimeQuest:** worst setup slack -4.286 ns on the Neo Geo 48.35 MHz PLL
  clock domain; the HDMI PLL clock setup slack is +0.425 ns. Incomplete
  setup/hold constraints (20 unconstrained input ports and 88 output
  ports). Baseline upstream timing was not measured under same conditions,
  so the cause of the setup failure is not established.
- **Automated checks:** 12,000 Python reference geometry cases and static
  wiring checks passed. These are not HDL simulation or hardware testing.
- **Not included:** screenshots/videos, binaries, Quartus reports/logs
  or unrelated BAZSET modifications.

## Suggested reviewer focus

Check signed OSD value encoding, default scaler behavior, overscan cadence,
HDMI mode transitions, and whether these controls would be better as
shared MiSTer framework functionality.
