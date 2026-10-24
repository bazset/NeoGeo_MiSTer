"""Checks for BAZSET NeoGeo HDMI CRT geometry."""
from pathlib import Path
from itertools import product
from random import Random
ROOT = Path(__file__).resolve().parents[1]

def window(sw,sh,bw,bh,en,hs,vs,hp,vp):
    w,h=bw,bh
    if en:
        w += (w*hs)//64
        h += (h*vs)//64
    w=max(1,min(sw,w)); h=max(1,min(sh,h))
    x=(sw-w)//2; y=(sh-h)//2
    if en:
        x += hp*(sw>>7); y += vp*(sh>>7)
    x=max(0,min(sw-w,x)); y=max(0,min(sh-h,y))
    return (x,x+w-1,y,y+h-1)

def run():
    cases=0
    random=Random(20261024)
    for sw,sh,bw,bh in [(640,480,640,480),(1280,720,960,720),
                        (1920,1080,1440,1080),(2560,1440,1920,1440),
                        (3840,2160,2880,2160),(1920,1080,1600,900)]:
        default=((sw-bw)//2,(sw-bw)//2+bw-1,(sh-bh)//2,(sh-bh)//2+bh-1)
        assert window(sw,sh,bw,bh,True,0,0,0,0)==default
        for _ in range(2000):
            hs,vs,hp,vp=(random.randint(-16,15) for _ in range(4))
            a,b,c,d=window(sw,sh,bw,bh,True,hs,vs,hp,vp)
            assert 0<=a<=b<sw and 0<=c<=d<sh,(sw,sh,hs,vs,hp,vp,a,b,c,d)
            assert window(sw,sh,bw,bh,False,hs,vs,hp,vp)==default
            cases+=1
        for h in range(-16,15):
            w1=window(sw,sh,bw,bh,True,h,0,0,0)
            w2=window(sw,sh,bw,bh,True,h+1,0,0,0)
            assert w2[1]-w2[0]>=w1[1]-w1[0]
    neo=(ROOT/'neogeo.sv').read_text()
    top=(ROOT/'sys/sys_top.v').read_text()
    ports=(ROOT/'sys/emu_ports.vh').read_text()
    qip=(ROOT/'sys/sys.qip').read_text()
    src=(ROOT/'sys/hdmi_crt_window.sv').read_text()
    for name in ('ENABLE','HSIZE','VSIZE','HPOS','VPOS'):
        assert 'HDMI_CRT_'+name in neo and 'HDMI_CRT_'+name in top and 'HDMI_CRT_'+name in ports
    for bit in ('[80]','[85:81]','[90:86]','[95:91]','[100:96]'):
        assert bit in neo
    for name in ('HDMI H-Size','HDMI V-Size','HDMI H-Position','HDMI V-Position'):
        assert name in neo
    assert 'hdmi_crt_window.sv' in qip
    assert '.active(crt_geometry_enable && !direct_video && !LFB_EN)' in top
    assert 'assign VGA_DISABLE = 0;' in neo
    assert '$signed(h_size)' in src and '$signed(v_size)' in src
    assert 'hoverscan' in src and 'voverscan' in src
    assert '.ihzoom' in top and '.ivzoom' in top
    vhdl=(ROOT/'sys/ascal.vhd').read_text()
    assert 'hdmi_hcrop' in vhdl and 'hdmi_vcrop' in vhdl
    # Overscan at full HDMI height must yield a visible crop and zoom.
    for zoom in range(1,16):
        sh=224
        crop=(sh*zoom*13)//2048
        assert 0 < crop < sh//4
        assert sh-2*crop < sh
    # Default or shrinking must leave the source untouched.
    assert 'if(active && sh > 0 && h > sh && !v_size[4])' in src
    print('PASS: %s geometry parameter cases and HDL integration checks' % cases)

if __name__ == '__main__':
    run()
