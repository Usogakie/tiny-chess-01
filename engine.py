# tiny-chess-01: 0x88 alpha-beta chess engine (negamax, null-move pruning, LMR, quiescence, TT, PST eval), 150k nodes/move, deterministic.
import json,os,sys,urllib.request as u,random
E=os.environ.get("MAKEFUN_ENV_URL") or sys.exit("no env")
V=(0,100,320,330,500,900,0)
KN=(33,31,18,14,-14,-18,-31,-33);KI=(1,-1,16,-16,15,17,-15,-17);BI=(15,17,-15,-17);RO=(1,-1,16,-16)
R=random.Random(7);Z=[[R.getrandbits(64) for _ in range(128)] for _ in range(13)];ZS=R.getrandbits(64);ZC=[R.getrandbits(64) for _ in range(16)];ZE=[R.getrandbits(64) for _ in range(8)]
KP=[15]*128
for s,v in((0,13),(7,14),(4,12),(112,7),(119,11),(116,3)):KP[s]=v
B=[0]*128;S=1;C=0;P=-1;H=0;KS=[4,116];TT={};ND=0;CAP=150000;KL=[[0,0] for _ in range(64)];INF=10**9
class TO(Exception):pass
def atk(s,c):
 for o in((-15,-17)if c>0 else(15,17)):
  t=s+o
  if not t&136 and B[t]==c:return 1
 for o in KN:
  t=s+o
  if not t&136 and B[t]==2*c:return 1
 for o in KI:
  t=s+o
  if not t&136 and B[t]==6*c:return 1
 for o in BI:
  t=s
  while 1:
   t+=o
   if t&136:break
   q=B[t]
   if q:
    if q in(3*c,5*c):return 1
    break
 for o in RO:
  t=s
  while 1:
   t+=o
   if t&136:break
   q=B[t]
   if q:
    if q in(4*c,5*c):return 1
    break
 return 0
def gen():
 ms=[]
 for f in range(128):
  if f&136:continue
  p=B[f]
  if not p or p*S<0:continue
  a=abs(p);d=16*S
  if a==1:
   t=f+d
   if not B[t]:
    if(f>>4)==(6 if S>0 else 1):
     for q in(5,4,3,2):ms.append(f|t<<7|q<<14)
    else:
     ms.append(f|t<<7)
     if(f>>4)==(1 if S>0 else 6):
      x=f+2*d
      if not B[x]:ms.append(f|x<<7|8<<17)
   for o in(15*S,17*S):
    t=f+o
    if t&136:continue
    q=B[t]
    if(q and q*S<0)or t==P:
     if(f>>4)==(6 if S>0 else 1):
      for q in(5,4,3,2):ms.append(f|t<<7|q<<14|1<<17)
     else:ms.append(f|t<<7|1<<17|(2<<17 if t==P else 0))
  elif a==2 or a==6:
   for o in(KN if a==2 else KI):
    t=f+o
    if t&136:continue
    q=B[t]
    if not q or q*S<0:ms.append(f|t<<7|(1<<17 if q else 0))
  else:
   for o in(BI if a==3 else RO if a==4 else BI+RO):
    t=f
    while 1:
     t+=o
     if t&136:break
     q=B[t]
     if not q:ms.append(f|t<<7)
     else:
      if q*S<0:ms.append(f|t<<7|1<<17)
      break
 if S>0:
  if C&1 and not B[5] and not B[6] and B[7]==4 and not atk(4,-1) and not atk(5,-1) and not atk(6,-1):ms.append(4|6<<7|4<<17)
  if C&2 and not B[3] and not B[2] and not B[1] and B[0]==4 and not atk(4,-1) and not atk(3,-1) and not atk(2,-1):ms.append(4|2<<7|4<<17)
 else:
  if C&4 and not B[117] and not B[118] and B[119]==-4 and not atk(116,1) and not atk(117,1) and not atk(118,1):ms.append(116|118<<7|4<<17)
  if C&8 and not B[115] and not B[114] and not B[113] and B[112]==-4 and not atk(116,1) and not atk(115,1) and not atk(114,1):ms.append(116|114<<7|4<<17)
 return ms
def make(m):
 global H,C,P,S
 f=m&127;t=m>>7&127;q=m>>14&7;fl=m>>17;pc=B[f];cap=0;cs=-1;oh=H;oc=C;oe=P
 if fl&2:cs=t-16*S;cap=B[cs];B[cs]=0;H^=Z[cap+6][cs]
 elif B[t]:cap=B[t];cs=t
 H^=Z[pc+6][f]
 if cap:H^=Z[cap+6][cs]
 B[f]=0;B[t]=q*S if q else pc;H^=Z[B[t]+6][t]
 if abs(pc)==6:KS[0 if pc>0 else 1]=t
 if fl&4:
  if t==6:B[5]=4;B[7]=0;H^=Z[10][7]^Z[10][5]
  elif t==2:B[3]=4;B[0]=0;H^=Z[10][0]^Z[10][3]
  elif t==118:B[117]=-4;B[119]=0;H^=Z[2][119]^Z[2][117]
  elif t==114:B[115]=-4;B[112]=0;H^=Z[2][112]^Z[2][115]
 H^=ZC[C];C&=KP[f]&KP[t];H^=ZC[C]
 if oe>=0:H^=ZE[oe&7]
 P=f+16*S if fl&8 else -1
 if P>=0:H^=ZE[P&7]
 H^=ZS;S=-S
 return(pc,cap,cs,oc,oe,oh)
def unmake(m,u):
 global H,C,P,S
 pc,cap,cs,oc,oe,oh=u;f=m&127;t=m>>7&127;fl=m>>17
 B[f]=pc;B[t]=0
 if cap:B[cs]=cap
 if abs(pc)==6:KS[0 if pc>0 else 1]=f
 if fl&4:
  if t==6:B[7]=4;B[5]=0
  elif t==2:B[0]=4;B[3]=0
  elif t==118:B[119]=-4;B[117]=0
  elif t==114:B[112]=-4;B[115]=0
 C,P,H,S=oc,oe,oh,-S
def nul():
 global H,P,S
 u=(P,H);H^=ZS
 if P>=0:H^=ZE[P&7]
 P=-1;S=-S;return u
def unn(u):
 global H,P,S
 P,H=u;S=-S
T=('KKKKKKKKLMMGGMMLLJIKKIJLKKKOOKKKLLMPPMLLMMOQQOMMUUUUUUUUKKKKKKKK','ACEEEECACGKLLKGCELMNNMLEEKNOONKEELNOONLEEKMNNMKECGKKKKGCACEEEECA','GIIIIIIGILKKKKLIIMMMMMMIIKMMMMKIILLMMLLIIKLMMLKIIKKKKKKIGIIIIIIG','KKKLLKKKJKKKKKKJJKKKKKKJJKKKKKKJJKKKKKKJJKKKKKKJLMMMMMMLKKKKKKKK','GIIJJIIGIKLKKKKIILLLLLKIKKLLLLKJJKLLLLKJIKLLLLKIIKKKKKKIGIIJJIIG','OQMKKMQOOOKKKKOOIGGGGGGIGEECCEEGECCAACCEECCAACCEECCAACCEECCAACCE','AEEEEEEAEEKKKKEEEIOQQOIEEIQSSQIEEIQSSQIEEIOQQOIEEGIKKIGEACEGGECA')
def ev():
 s=0;wb=0;bb=0;tot=0;wk=0;bk=0
 for q in range(128):
  if q&136:continue
  p=B[q]
  if not p:continue
  a=abs(p);v=V[a];i=(q>>4)*8+(q&7) if p>0 else (7-(q>>4))*8+(q&7)
  if a==1:v+=(ord(T[0][i])-75)*5
  elif a==2:v+=(ord(T[1][i])-75)*5
  elif a==3:
   v+=(ord(T[2][i])-75)*5
   if p>0:wb+=1
   else:bb+=1
  elif a==4:v+=(ord(T[3][i])-75)*5
  elif a==5:v+=(ord(T[4][i])-75)*5
  elif a==6:
   if p>0:wk=q
   else:bk=q
  if a<6:tot+=V[a]
  s+=v if p>0 else -v
 if wb>1:s+=25
 if bb>1:s-=25
 for q,g in((wk,1),(bk,-1)):
  i=(q>>4)*8+(q&7) if g>0 else (7-(q>>4))*8+(q&7)
  s+=g*(ord((T[5] if tot>=2400 else T[6])[i])-75)*5
 return s*S
def qs(a,b,pl):
 global ND
 ND+=1
 if ND>CAP:raise TO
 if pl>12:return ev()
 s=ev();ck=atk(KS[0 if S>0 else 1],-S);n=0
 if not ck:
  if s>=b:return b
  if s>a:a=s
 ms=[m for m in gen() if ck or m>>17&1]
 ms.sort(key=lambda m:V[abs(B[m>>7&127])],reverse=True)
 for m in ms:
  if not ck:
   q=B[m>>7&127];v=V[abs(q)] if q else 100
   if s+v+100<a:continue
  s0=S;u=make(m)
  if atk(KS[0 if s0>0 else 1],-s0):unmake(m,u);continue
  n+=1
  try:s=-qs(-b,-a,pl+1)
  except TO:unmake(m,u);raise
  unmake(m,u)
  if s>=b:return b
  if s>a:a=s
 if ck and n==0:return -99999+pl
 return a
def sr(d,a,b,pl):
 global ND
 ND+=1
 if ND>CAP:raise TO
 if d==0:return qs(a,b,pl)
 e=TT.get(H);tm=0
 if e:
  if e[0]>=d:
   if e[3]==0:return e[1]
   if e[3]==1 and e[1]>=b:return e[1]
   if e[3]==2 and e[1]<=a:return e[1]
  tm=e[2]
 ck=atk(KS[0 if S>0 else 1],-S)
 if ck:d+=1
 elif d>2:
  u=nul()
  try:s=-sr(d-3,-b,1-b,pl+1)
  except TO:unn(u);raise
  unn(u)
  if s>=b:return b
 ms=gen()
 def ky(m):
  sc=1000000 if m==tm else 9000 if m in KL[pl] else 0
  q=B[m>>7&127]
  if q:sc+=V[abs(q)]*10-V[abs(B[m&127])]
  return sc
 ms.sort(key=ky,reverse=True)
 best=-INF;bm=0;al=a
 for j,m in enumerate(ms):
  s0=S;u=make(m)
  if atk(KS[0 if s0>0 else 1],-s0):unmake(m,u);continue
  try:
   rd=d-1
   if j>2 and d>2 and not m>>17&1 and m!=tm:rd=d-2
   s=-sr(rd,-b,-a,pl+1)
   if rd<d-1 and s>a:s=-sr(d-1,-b,-a,pl+1)
  except TO:unmake(m,u);raise
  unmake(m,u)
  if s>best:best=s;bm=m
  if s>a:a=s
  if a>=b:
   if not m>>17&1:KL[pl][1]=KL[pl][0];KL[pl][0]=m
   TT[H]=(d,best,bm,1)
   return best
 if bm==0:return -99999+pl if ck else 0
 TT[H]=(d,best,bm,0 if al<best<b else 2)
 if len(TT)>200000:TT.clear()
 return best
# iterative deepening to depth 6 under a fixed node budget; deterministic, no clock.
def root():
 global ND
 ms=gen();bm=ms[0] if ms else 0;ND=0
 for D in range(1,7):
  try:
   a=-INF;b=INF;best=-INF;cb=bm
   ms.sort(key=lambda m:0 if m==cb else 1)
   for m in ms:
    s0=S;u=make(m)
    if atk(KS[0 if s0>0 else 1],-s0):unmake(m,u);continue
    try:s=-sr(D-1,-b,-a,1)
    except TO:unmake(m,u);raise
    unmake(m,u)
    if s>best:best=s;cb=m
    if s>a:a=s
   if cb:bm=cb
  except TO:break
 return bm
def setup(f):
 global B,S,C,P,H,KS
 B=[0]*128;H=0;C=0;P=-1;KS=[4,116]
 p=f.split();rows=p[0].split('/')
 for r,row in enumerate(rows):
  x=0
  for ch in row:
   if ch.isdigit():x+=int(ch)
   else:
    q=(7-r)*16+x;pc='pnbrqk'.index(ch.lower())+1;B[q]=pc if ch.isupper() else -pc;H^=Z[B[q]+6][q]
    if pc==6:KS[0 if ch.isupper() else 1]=q
    x+=1
 S=1 if p[1]=='w' else -1
 if S<0:H^=ZS
 for ch in p[2]:C|={'K':1,'Q':2,'k':4,'q':8}.get(ch,0)
 H^=ZC[C]
 if p[3]!='-':
  P=(ord(p[3][0])-97)+(int(p[3][1])-1)*16;H^=ZE[P&7]
def post(p,b):
 q=u.Request(E+p,data=json.dumps(b).encode(),headers={'content-type':'application/json'})
 try:
  with u.urlopen(q) as r2:return json.load(r2)
 except Exception as e:sys.exit(p+': '+str(e))
def uc(m):
 f=m&127;t=m>>7&127;pr=m>>14&7
 return 'abcdefgh'[f&7]+str((f>>4)+1)+'abcdefgh'[t&7]+str((t>>4)+1)+('nbrq'[pr-2] if pr else '')
while 1:
 g=post('/game',{})
 if g['status']=='done':break
 while g['status']=='your_move':
  setup(g['fen']);m=root();mv=uc(m)
  if mv not in g['legal_moves']:mv=g['legal_moves'][0]
  g=post('/move',{'game':g['game'],'move':mv})
 print('game',g['game'],g.get('outcome'),g.get('reason'),file=sys.stderr)
print('done',g.get('wins'),g.get('draws'),g.get('losses'),file=sys.stderr)
