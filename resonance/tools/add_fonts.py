"""Add only required Unicode glyphs from matching Fusion Pixel upstream fonts.

Requires fontTools==4.60.1. Old outlines and metrics are verified unchanged.
"""
from pathlib import Path
import json,hashlib,copy
from fontTools.ttLib import TTFont
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def outline(font,name):
 g=font['glyf'][name]
 if g.isComposite():return g.compile(font['glyf'])
 coords,ends,flags=g.getCoordinates(font['glyf'])
 return (list(coords),list(ends),list(flags),g.numberOfContours)
def main():
 rows=json.loads((ROOT/'source/translations.v1.1.json').read_text(encoding='utf-8'))
 requested={ord(c) for r in rows for c in r['zh'] if ord(c)>127}
 out=ROOT/'source/fonts';out.mkdir(exist_ok=True)
 report=[]
 for p in sorted((ROOT/'baseline/v1.0.1/PatchFiles').glob('*.ttf')):
  f=TTFont(p,recalcTimestamp=False);old_order=f.getGlyphOrder()[:]
  old_metrics=copy.deepcopy(f['hmtx'].metrics)
  old_shapes={g:outline(f,g) for g in old_order}
  globals_before=[f['head'].unitsPerEm,f['hhea'].ascent,f['hhea'].descent,f['hhea'].lineGap,f['OS/2'].sTypoAscender,f['OS/2'].sTypoDescender,f['OS/2'].usWinAscent,f['OS/2'].usWinDescent]
  size=f['head'].unitsPerEm//100
  upstream_path=ROOT/f'source/font_upstream/fusion-{size}.ttf'
  src=TTFont(upstream_path,recalcTimestamp=False)
  assert src['head'].unitsPerEm==f['head'].unitsPerEm
  missing=sorted(requested-set(f.getBestCmap()))
  assert not set(missing)-set(src.getBestCmap()),(size,'upstream missing')
  added={}
  for cp in missing:
   name=f'v11_u{cp:04X}';assert name not in old_order
   glyph=copy.deepcopy(src['glyf'][src.getBestCmap()[cp]])
   assert not glyph.isComposite(), 'Composite requires dependency copying'
   # Force expansion while still tied to source font.
   glyph.getCoordinates(src['glyf'])
   f['glyf'][name]=glyph
   f['hmtx'].metrics[name]=src['hmtx'].metrics[src.getBestCmap()[cp]]
   assert glyph.yMax<=f['hhea'].ascent and glyph.yMin>=f['hhea'].descent
   added[cp]=name
  f.setGlyphOrder(old_order+list(added.values()))
  for table in f['cmap'].tables:
   if table.isUnicode():table.cmap.update({cp:name for cp,name in added.items() if table.format==12 or cp<=65535})
  target=out/p.name;f.save(target)
  reread=TTFont(target,recalcTimestamp=False)
  assert reread.getGlyphOrder()[:len(old_order)]==old_order
  assert all(outline(reread,g)==old_shapes[g] and reread['hmtx'].metrics[g]==old_metrics[g] for g in old_order)
  assert globals_before==[reread['head'].unitsPerEm,reread['hhea'].ascent,reread['hhea'].descent,reread['hhea'].lineGap,reread['OS/2'].sTypoAscender,reread['OS/2'].sTypoDescender,reread['OS/2'].usWinAscent,reread['OS/2'].usWinDescent]
  assert requested<=set(reread.getBestCmap())
  report.append({'font':p.name,'pixel_size':size,'baseline_sha256':digest(p),'upstream_sha256':digest(upstream_path),'output_sha256':digest(target),'added_codepoints':missing,'added_characters':''.join(map(chr,missing)),'old_glyph_count':len(old_order),'old_glyph_order_shapes_widths_unchanged':True,'global_metrics_unchanged':True,'all_translation_unicode_covered':True})
 (ROOT/'qa/font_expansion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
