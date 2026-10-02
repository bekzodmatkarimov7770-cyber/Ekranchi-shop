import numpy as np, wave, os
SR=48000; D=os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","public","sfx"); os.makedirs(D, exist_ok=True)
rng=np.random.default_rng(7)
def t(d): return np.arange(int(SR*d))/SR
def env(x,a=0.002,dec=0.1):
    n=len(x); tt=np.arange(n)/SR
    e=np.minimum(1,tt/a)*np.exp(-tt/dec); return x*e
def lp(x,k):  # one-pole lowpass, k in 0..1
    y=np.zeros_like(x); s=0
    for i,v in enumerate(x): s+=k*(v-s); y[i]=s
    return y
def hp(x,k): return x-lp(x,k)
def save(name,x,g=0.9):
    x=np.asarray(x,dtype=float); m=np.max(np.abs(x)) or 1; x=x/m*g
    st=np.stack([x,x],1)
    with wave.open(f"{D}/{name}.wav","wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st*32767).astype(np.int16).tobytes())
# tap: soft click + body
tt=t(0.09); tap=env(np.sin(2*np.pi*1600*tt)*0.5+hp(rng.standard_normal(len(tt)),0.3)*0.6,0.0005,0.012)+env(np.sin(2*np.pi*190*tt),0.001,0.03)*0.7
save("tap",tap,0.7)
# key: typing tick
tt=t(0.05); save("key",env(hp(rng.standard_normal(len(tt)),0.5)*0.8+np.sin(2*np.pi*2600*tt)*0.3,0.0003,0.008),0.45)
# pop: rising blip
tt=t(0.14); f=500+1100*(tt/tt[-1]); save("pop",env(np.sin(2*np.pi*np.cumsum(f)/SR),0.002,0.05),0.6)
# whoosh: swept filtered noise
d=0.55; tt=t(d); n=rng.standard_normal(len(tt)); y=np.zeros_like(n); s=0
for i,v in enumerate(n):
    k=0.02+0.25*np.sin(np.pi*i/len(n))**2; s+=k*(v-s); y[i]=s
save("whoosh",y*np.sin(np.pi*tt/d)**1.5,0.6)
# success ding: two notes
def bell(f,d,dec):
    tt=t(d); return env(np.sin(2*np.pi*f*tt)+0.35*np.sin(2*np.pi*2*f*tt)+0.12*np.sin(2*np.pi*3.01*f*tt),0.003,dec)
a=bell(1046.5,0.9,0.28); b=bell(1568,0.9,0.35); off=int(0.09*SR)
ding=np.zeros(len(b)+off); ding[:len(a)]+=a; ding[off:off+len(b)]+=b; save("ding",ding,0.65)
# notification: telegram-like double chirp
c1=bell(1318.5,0.35,0.07); c2=bell(1760,0.5,0.12); off=int(0.11*SR)
nt=np.zeros(len(c2)+off); nt[:len(c1)]+=c1; nt[off:]+=c2; save("notify",nt,0.6)
# riser
d=1.4; tt=t(d); f=200*np.exp(tt/d*np.log(8)); r=np.sin(2*np.pi*np.cumsum(f)/SR)*0.4+lp(rng.standard_normal(len(tt)),0.15)*0.8
save("riser",r*(tt/d)**2,0.5)
# impact / boom
tt=t(1.6); f=110*np.exp(-tt*6)+42; boom=env(np.sin(2*np.pi*np.cumsum(f)/SR),0.002,0.45)+env(lp(rng.standard_normal(len(tt)),0.2),0.001,0.08)*0.8
save("impact",boom,0.9)
# slide (short swish for scrolls)
d=0.3; tt=t(d); y=lp(rng.standard_normal(len(tt)),0.12)*np.sin(np.pi*tt/d)**2; save("swish",y,0.35)
# coin/cash for price drop
c=bell(1975.5,0.5,0.09); c2=bell(2637,0.6,0.15); off=int(0.06*SR); cc=np.zeros(len(c2)+off); cc[:len(c)]+=c; cc[off:]+=c2; save("coin",cc,0.55)
# --- light beat bed (110 bpm, 48 s) ---
bpm=110; beat=60/bpm; L=58; out=np.zeros(int(SR*L))
def put(x,at,g=1):
    i=int(at*SR); j=min(len(out),i+len(x)); out[i:j]+=x[:j-i]*g
kt=t(0.35); kick=env(np.sin(2*np.pi*np.cumsum(55+90*np.exp(-kt*30))/SR),0.001,0.12)
ht=t(0.06); hat=env(hp(rng.standard_normal(len(ht)),0.7),0.0005,0.012)
st_=t(0.25); snare=env(hp(rng.standard_normal(len(st_)),0.25),0.001,0.06)*0.7+env(np.sin(2*np.pi*190*st_),0.001,0.05)*0.4
bass_notes=[55,55,65.4,49]  # A1 A1 C2 G1
pad_ch=[[220,261.6,329.6],[220,261.6,329.6],[261.6,329.6,392],[196,246.9,293.7]]
bar=4*beat; nb=int(L/bar)+1
for b in range(nb):
    t0=b*bar
    for k in range(4):
        put(kick,t0+k*beat,0.9 if k in (0,2) else 0.0)
        if k in (1,3): put(snare,t0+k*beat,0.55)
        for hh in range(2): put(hat,t0+k*beat+hh*beat/2,0.25 if hh else 0.15)
    f=bass_notes[b%4]; bt=t(bar)
    bass=np.sin(2*np.pi*f*bt)*0.5+np.sin(2*np.pi*2*f*bt)*0.15
    pulse=np.ones_like(bt)
    for k in range(8): 
        i=int(k*beat/2*SR); pulse[i:i+int(0.03*SR)]*=np.linspace(0,1,int(0.03*SR))[:len(pulse[i:i+int(0.03*SR)])]
    put(bass*pulse*np.exp(-((bt%(beat/2))*3)),t0,0.55)
    pad=sum(np.sin(2*np.pi*ff*bt)+0.3*np.sin(2*np.pi*ff*1.003*bt) for ff in pad_ch[b%4])
    put(pad*np.minimum(1,bt/0.4)*np.minimum(1,(bar-bt)/0.4),t0,0.09)
out=lp(out,0.6); save("beat",out,0.8)
print("ok")
