"""AGS 3.6.1 TRA writer and strict round-trip reader, UTF-8/mixed source encoding.

Independent implementation from documented binary format. Reference:
https://github.com/adventuregamestudio/ags/tree/v3.6.1.35/Common/game
"""
import struct
KEY=b'Avis Durgan'
SIGNATURE=b'AGSTranslation\x00'
def enc(s):
    b=s.encode('utf-8')+b'\0'
    return struct.pack('<i',len(b))+bytes((c+KEY[i%len(KEY)])%256 for i,c in enumerate(b))
def block(n,p):return struct.pack('<ii',n,len(p))+p
def string(s):
    b=s.encode('utf-8');return struct.pack('<i',len(b))+b
def compile_tra(pairs,uid,name,normal=-1,speech=-1):
    pairs=list(pairs)
    if len(dict(pairs))!=len(pairs):raise ValueError('Duplicate dictionary key')
    if any(not s or not t for s,t in pairs):raise ValueError('Empty key/value')
    out=SIGNATURE+block(2,struct.pack('<i',uid)+enc(name))
    out+=block(1,b''.join(enc(s)+enc(t) for s,t in sorted(pairs))+enc('')+enc(''))
    out+=block(3,struct.pack('<iii',normal,speech,1))
    opts={'encoding':'UTF-8','gameencoding':'.1252'}
    p=struct.pack('<i',len(opts))+b''.join(string(k)+string(v) for k,v in sorted(opts.items()))
    out+=struct.pack('<i',0)+b'ext_sopts'.ljust(16,b'\0')+struct.pack('<q',len(p))+p
    return out+struct.pack('<i',-1)

def parse_tra(data):
    if not data.startswith(SIGNATURE):raise ValueError('Bad TRA signature')
    pos=len(SIGNATURE);result={'pairs':{},'options':{}}
    def read(fmt):
        nonlocal pos
        if pos+struct.calcsize(fmt)>len(data):raise ValueError('Truncated TRA')
        x=struct.unpack_from(fmt,data,pos);pos+=struct.calcsize(fmt);return x
    def getstring(encrypted=False):
        nonlocal pos
        n,=read('<i')
        if n<0 or pos+n>len(data):raise ValueError('Invalid TRA string size')
        b=data[pos:pos+n];pos+=n
        if encrypted:
            b=bytes((c-KEY[i%len(KEY)])%256 for i,c in enumerate(b))
            if not b.endswith(b'\0'):raise ValueError('Missing string terminator')
            b=b[:-1]
        return b.decode('utf-8')
    while True:
        n,=read('<i')
        if n==-1:break
        if n==0:
            ext=data[pos:pos+16].rstrip(b'\0').decode();pos+=16;size,=read('<q')
        else:ext='';size,=read('<i')
        if size<0 or pos+size>len(data):raise ValueError('Invalid TRA block size')
        end=pos+size
        if n==1:
            while True:
                s,t=getstring(True),getstring(True)
                if not s and not t:break
                if not s or s in result['pairs']:raise ValueError('Invalid/duplicate key')
                result['pairs'][s]=t
        elif n==2:
            result['uid'],=read('<i');result['name']=getstring(True)
        elif n==3:result['fonts_direction']=read('<iii')
        elif n==0 and ext=='ext_sopts':
            count,=read('<i')
            for _ in range(count):
                k,v=getstring(),getstring();result['options'][k]=v
        else:raise ValueError('Unsupported block')
        if pos!=end:raise ValueError('Block size mismatch')
    if pos!=len(data):raise ValueError('Trailing TRA data')
    return result
