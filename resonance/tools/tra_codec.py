"""Lossless AGS TRA dictionary reader/writer; leaves all other blocks untouched."""
import struct
KEY=b'Avis Durgan'
def encrypt(text):
 raw=text.encode('utf-8')+b'\0'
 data=bytes((x+KEY[i%len(KEY)])&255 for i,x in enumerate(raw))
 return struct.pack('<i',len(data))+data
def decrypt(data):
 raw=bytes((x-KEY[i%len(KEY)])&255 for i,x in enumerate(data))
 if not raw or raw[-1]!=0 or b'\0' in raw[:-1]:raise ValueError('Invalid string terminator')
 return raw[:-1].decode('utf-8',errors='strict')
def extract(blob):
 if blob[:15]!=b'AGSTranslation\0':raise ValueError('Bad TRA signature')
 offset=15
 while offset+8<=len(blob):
  kind,size=struct.unpack_from('<ii',blob,offset)
  if kind<1 or size<0 or offset+8+size>len(blob):raise ValueError('Invalid block bounds')
  end=offset+8+size
  if kind==1:
   pos=offset+8;rows=[]
   def read():
    nonlocal pos
    if pos+4>end:raise ValueError('Truncated string length')
    n=struct.unpack_from('<i',blob,pos)[0];pos+=4
    if n<1 or pos+n>end:raise ValueError('Invalid string length')
    value=decrypt(blob[pos:pos+n]);pos+=n;return value
   while pos<end:
    en,zh=read(),read()
    if not en and not zh:break
    rows.append({'id':len(rows),'en':en,'zh':zh})
   if pos!=end:raise ValueError('Dictionary size mismatch')
   return rows,offset,end
  offset=end
 raise ValueError('Dictionary missing')
def compile_tra(blob,rows):
 old,start,end=extract(blob)
 if [r['en'] for r in rows]!=[r['en'] for r in old]:raise ValueError('English keys changed')
 payload=b''.join(encrypt(r['en'])+encrypt(r['zh']) for r in rows)+encrypt('')*2
 return blob[:start]+struct.pack('<ii',1,len(payload))+payload+blob[end:]
