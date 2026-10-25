"""SWF header summary: version, size, stage, fps, frames, AS3 or AS2, DoAction count, FileAttributes.
   python swfheader.py game.swf [more.swf ...]"""
import sys,zlib,struct,glob
for p in sys.argv[1:]:
    d=open(p,'rb').read(); sig=d[:3]; ver=d[3]
    if sig==b'CWS': b=d[:8]+zlib.decompress(d[8:])
    elif sig==b'FWS': b=d
    else:
        print(p,sig,ver,'LZMA-compressed (ZWS): decompress with FFDec first');continue
    nbits=b[8]>>3; rl=(5+nbits*4+7)//8; o=8+rl
    rate=b[o+1]+b[o]/256; frames=struct.unpack('<H',b[o+2:o+4])[0]; o+=4
    def rb(v,s,n):
        r=0
        for i in range(n): r=(r<<1)|((v[s//8]>>(7-s%8))&1); s+=1
        return r
    xmax=rb(b,8*8+5+nbits,nbits); ymax=rb(b,8*8+5+nbits*3,nbits)
    fa=None; tags={}; as3=False; doaction=0; names=[]
    while o<len(b):
        h=struct.unpack('<H',b[o:o+2])[0]; t=h>>6; l=h&63; o+=2
        if l==63: l=struct.unpack('<I',b[o:o+4])[0]; o+=4
        if t in (72,82): as3=True
        if t in (12,59): doaction+=1
        if t==69: fa=b[o]
        tags[t]=tags.get(t,0)+1; o+=l
        if t==0: break
    print(f"{p}: SWF{ver} {len(d)//1024}KB {xmax/20:.0f}x{ymax/20:.0f} {rate}fps frames={frames} AS3={as3} doaction={doaction} attrs={'none' if fa is None else hex(fa)}")
