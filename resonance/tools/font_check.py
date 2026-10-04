"""Read Unicode cmap coverage from TrueType format 4/12 using standard library."""
import struct
def supported_codepoints(path,requested):
 data=path.read_bytes();u16=lambda p:struct.unpack_from('>H',data,p)[0];u32=lambda p:struct.unpack_from('>I',data,p)[0]
 count=u16(4);cmap=None
 for i in range(count):
  p=12+16*i
  if data[p:p+4]==b'cmap':cmap=u32(p+8);break
 if cmap is None:raise ValueError('Missing cmap')
 supported=set();handled=False
 for i in range(u16(cmap+2)):
  p=cmap+4+8*i;platform,encoding=u16(p),u16(p+2)
  if platform!=0 and not(platform==3 and encoding in (1,10)):continue
  start=cmap+u32(p+4);fmt=u16(start)
  if fmt==12:
   handled=True;groups=u32(start+12)
   for j in range(groups):
    first,last,glyph=struct.unpack_from('>III',data,start+16+12*j)
    for cp in requested:
     if first<=cp<=last and glyph+cp-first!=0:supported.add(cp)
  elif fmt==4:
   handled=True;n=u16(start+6)//2;ends=start+14;starts=ends+2*n+2;deltas=starts+2*n;offsets=deltas+2*n
   for cp in requested:
    if cp>65535:continue
    for j in range(n):
     if u16(starts+2*j)<=cp<=u16(ends+2*j):
      delta=u16(deltas+2*j);offset=u16(offsets+2*j)
      if offset:
       addr=offsets+2*j+offset+2*(cp-u16(starts+2*j));gid=u16(addr)
       if gid:gid=(gid+delta)&65535
      else:gid=(cp+delta)&65535
      if gid:supported.add(cp)
      break
 if not handled:raise ValueError('No supported Unicode cmap format')
 return supported
