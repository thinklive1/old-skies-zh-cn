"""Check Latin rendering equality and draw translated glyph samples."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageChops,ImageFilter
from fontTools.ttLib import TTFont
from catalog import ROOT,write_json,read_json
import argparse,hashlib

def verify(assets,development=False):
    dest=ROOT/'build'/('development' if development else 'release')
    manifest=read_json(dest/'build-manifest.json');hashes={r['name']:r['sha256'] for r in manifest['files']}
    if not all(f'agsfnt{i}.ttf' in hashes for i in range(8)):raise ValueError('Font build incomplete; refused to inspect stale files')
    for i in range(8):
        name=f'agsfnt{i}.ttf'
        if hashlib.sha256((dest/name).read_bytes()).hexdigest()!=hashes[name]:raise ValueError('Font manifest mismatch: '+name)
    sizes={0:16,1:32,2:32,3:16,4:16,5:16,6:16,7:24}
    canvas=Image.new('RGB',(1060,700),'#111a24');draw=ImageDraw.Draw(canvas);results=[]
    latin='Technobabylon ABC xyz 0123456789 %s &99'
    chinese='中文测试：迷境、湿件、中枢，意识劫持者、鹌鹑。'
    for row,(i,size) in enumerate(sizes.items()):
        target=dest/f'agsfnt{i}.ttf';font=ImageFont.truetype(str(target),size)
        y=15+row*72
        draw.text((12,y),f'Font {i} / {size}px',fill='#69d6f5')
        draw.text((180,y),latin,font=font,fill='white')
        draw.text((180,y+32),chinese,font=font,fill='white')
        equal=None
        if i!=3:
            old=ImageFont.truetype(str(Path(assets)/target.name),size)
            a=Image.new('L',(900,80));b=a.copy()
            ImageDraw.Draw(a).text((0,0),latin,font=old,fill=255)
            ImageDraw.Draw(b).text((0,0),latin,font=font,fill=255)
            equal=ImageChops.difference(a,b).getbbox() is None
            if not equal:raise ValueError(f'Latin rendering changed for font {i}')
        results.append(dict(font=i,size=size,latin_pixels_equal=equal,sample_bbox=font.getbbox(chinese)))
    draw.text((12,615),'Font 2 outline + 1 foreground',fill='#69d6f5')
    draw.text((180,645),chinese,font=ImageFont.truetype(str(dest/'agsfnt2.ttf'),32),fill='white')
    draw.text((180,645),chinese,font=ImageFont.truetype(str(dest/'agsfnt1.ttf'),32),fill='#111a24')
    # Independent raster check: the 64-design-unit outline at 128px must cover
    # an eight-pixel dilation of the base glyph. A one-pixel tolerance handles
    # edge rasterization; the old separated copies leave visible interior gaps.
    base=Image.new('L',(256,256));outline=base.copy()
    ImageDraw.Draw(base).text((40,180),'中',font=ImageFont.truetype(str(dest/'agsfnt1.ttf'),128),fill=255,anchor='ls')
    ImageDraw.Draw(outline).text((40,180),'中',font=ImageFont.truetype(str(dest/'agsfnt2.ttf'),128),fill=255,anchor='ls')
    expected=base.point(lambda p:255 if p>=128 else 0).filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.MinFilter(3))
    missing=ImageChops.subtract(expected,outline.point(lambda p:255 if p>=128 else 0)).getbbox()
    if missing:raise ValueError('Outline has gaps in continuous dilation: '+str(missing))
    canvas.save(dest/'font-preview.png')
    write_json(dest/'font-render-check.json',dict(results=results,continuous_outline_core_covered=True,outline_sample='中 at 128px, eight-pixel dilation, one-pixel edge tolerance',game_visual_check='pending',method='Pillow/FreeType; not an in-game screenshot'))
    print('Latin pixels identical for 7 original TTFs; 8 font samples generated')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('assets');ap.add_argument('--development',action='store_true');a=ap.parse_args();verify(a.assets,a.development)
