"""Keep the game's Latin designs/metrics, add only missing translated glyphs.

Requires fonttools. Original fonts are read from the user's own verified assets.
Outputs are local build artifacts, never a copy of the entire game archive.
"""
from pathlib import Path
import argparse,copy,hashlib,json
import pathops
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools import subset
from catalog import ROOT,load,read_json,write_json
from tra import parse_tra

def make_fonts(assets,development=False):
    assets=Path(assets);baseline=read_json(ROOT/'source/baseline.json')
    hashes={a['name']:a['sha256'] for a in baseline['asset_manifest']}
    dest=ROOT/'build'/('development' if development else 'release');dest.mkdir(parents=True,exist_ok=True)
    cfg=read_json(ROOT/'project.json')
    tra_path=dest/(cfg['translation_name']+'.tra')
    if not tra_path.exists():raise ValueError('Build the matching TRA before building its fonts')
    compiled=parse_tra(tra_path.read_bytes());chars=set('中文汉化测试，。！？：“”……—')
    for target in compiled['pairs'].values():chars.update(target)
    primary_provenance=read_json(ROOT/'fonts/provenance.json');primary_path=ROOT/'fonts'/primary_provenance['font_file']
    if hashlib.sha256(primary_path.read_bytes()).hexdigest()!=primary_provenance['font_sha256']:raise ValueError('Primary font provenance mismatch')
    donor=TTFont(primary_path);donor_set=donor.getGlyphSet();dc=donor.getBestCmap()
    fallback_root=ROOT/'fonts/noto-fallback';provenance=read_json(fallback_root/'provenance.json')
    for entry in provenance['files']:
        if hashlib.sha256((fallback_root/entry['file']).read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Fallback font provenance mismatch')
    fallback=TTFont(fallback_root/'NotoSansSC[wght].ttf');fc=fallback.getBestCmap()
    fallback_set=fallback.getGlyphSet(location={'wght':provenance['weight']})
    allchars={ord(c) for c in chars if ord(c)>=32};records=[]
    heights={0:768,1:448,2:448,4:640,5:640,6:768,7:448}
    for index,height in heights.items():
        original=assets/f'agsfnt{index}.ttf'
        if hashlib.sha256(original.read_bytes()).hexdigest()!=hashes[original.name]:raise ValueError('Original font hash mismatch')
        f=TTFont(original,recalcTimestamp=False);cmap=f.getBestCmap()
        # Fusion Pixel does not contain U+2212. For the axis minus button,
        # reuse the original font's hyphen-minus glyph and advance explicitly.
        aliases=[]
        if 0x2212 in allchars and 0x2212 not in cmap:
            for table in f['cmap'].tables:
                if table.isUnicode():table.cmap[0x2212]=cmap[0x2d]
            aliases.append({'codepoint':'U+2212','glyph_source':'U+002D'})
        missing=allchars-set(f.getBestCmap())
        if missing-(set(dc)|set(fc)):raise ValueError('Unsupported glyphs: '+repr(''.join(chr(c) for c in sorted(missing-(set(dc)|set(fc))))))
        fallback_chars=[]
        for cp in sorted(missing):
            use_fallback=cp not in dc
            glyphset,codes,font=(fallback_set,fc,fallback) if use_fallback else (donor_set,dc,donor)
            if use_fallback:fallback_chars.append(chr(cp))
            glyph_name='zh_u'+f'{cp:06X}';record=DecomposingRecordingPen(glyphset);glyphset[codes[cp]].draw(record)
            bounds=BoundsPen(None);record.replay(bounds)
            # The donor's 12px cell has 1200 design units. Fit the cell into the
            # game's original ascent without changing Latin font metrics.
            scale=height/font['head'].unitsPerEm
            tx=64;ty=100*scale
            pen=TTGlyphPen(None)
            if index==2:
                base=pathops.Path();record.replay(TransformPen(base.getPen(),(scale,0,0,scale,tx,ty)))
                base=pathops.simplify(base,fix_winding=True)
                border=pathops.Path();base.draw(border.getPen())
                border.stroke(128,pathops.LineCap.BUTT_CAP,pathops.LineJoin.MITER_JOIN,4)
                # A continuous 64-unit expansion avoids gaps between discrete
                # copies of the thin pixel strokes. Union the border with ink.
                expanded=pathops.op(base,border,pathops.PathOp.UNION,fix_winding=True)
                expanded.draw(pen)
            else:
                record.replay(TransformPen(pen,(scale,0,0,scale,tx,ty)))
            glyph=pen.glyph();glyph.recalcBounds(f['glyf'])
            if hasattr(glyph,'flags') and len(glyph.flags):glyph.flags[0]|=0x40
            order=list(f.getGlyphOrder())
            f['glyf'][glyph_name]=glyph
            if glyph_name not in order:order.append(glyph_name)
            f.setGlyphOrder(order)
            advance=round(glyphset[codes[cp]].width*scale+128)
            f['hmtx'][glyph_name]=(advance,getattr(glyph,'xMin',0))
            for table in f['cmap'].tables:
                if table.isUnicode() and (cp<=65535 or table.format in (12,13)):table.cmap[cp]=glyph_name
        # Mark generated fonts as project builds. Preserve the game's layout metrics.
        for n in f['name'].names:
            if n.nameID in (1,3,4,6):
                name=f'TB-ZH-CN-{index}'
                n.string=name.encode(n.getEncoding(),errors='replace')
        target=dest/original.name;f.save(target,reorderTables=False)
        reread=TTFont(target)
        if allchars-set(reread.getBestCmap()):raise ValueError('Written font lost glyphs')
        for metric in ('ascent','descent','lineGap'):
            if getattr(reread['hhea'],metric)!=getattr(TTFont(original)['hhea'],metric):raise ValueError('Changed original line metrics')
        records.append(dict(name=target.name,added_glyphs=len(missing),fallback_chars=fallback_chars,aliases=aliases,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),size=target.stat().st_size))
    # Font 3 is originally a bitmap WFN font with multiplier 2. A TTF is tried
    # before WFN by AGS; its base size falls back to 8 and is multiplied to 16.
    replacement=TTFont(ROOT/'fonts/fusion-pixel-12px-proportional-zh_hans.ttf',recalcTimestamp=False)
    for table in replacement['cmap'].tables:
        if table.isUnicode():table.cmap[0x2212]=replacement.getBestCmap()[0x2d]
    missing=allchars-set(replacement.getBestCmap());fallback_chars=[]
    if missing-set(fc):raise ValueError('Font 3 is missing required glyphs')
    for cp in sorted(missing):
        glyph_name='fallback_u'+f'{cp:06X}';record=DecomposingRecordingPen(fallback_set);fallback_set[fc[cp]].draw(record)
        scale=replacement['head'].unitsPerEm/fallback['head'].unitsPerEm
        pen=TTGlyphPen(None);record.replay(TransformPen(pen,(scale,0,0,scale,0,0)));glyph=pen.glyph();glyph.recalcBounds(replacement['glyf'])
        order=list(replacement.getGlyphOrder());replacement['glyf'][glyph_name]=glyph;replacement.setGlyphOrder(order+[glyph_name])
        replacement['hmtx'][glyph_name]=(round(fallback_set[fc[cp]].width*scale),getattr(glyph,'xMin',0))
        if 'vmtx' in replacement:replacement['vmtx'][glyph_name]=(replacement['head'].unitsPerEm,replacement['hhea'].ascent-getattr(glyph,'yMax',0))
        for table in replacement['cmap'].tables:
            if table.isUnicode() and (cp<=65535 or table.format in (12,13)):table.cmap[cp]=glyph_name
        fallback_chars.append(chr(cp))
    options=subset.Options();options.recalc_timestamp=False
    sub=subset.Subsetter(options=options);sub.populate(unicodes=allchars|set(range(32,256)));sub.subset(replacement)
    for n in replacement['name'].names:
        if n.nameID in (1,3,4,6):n.string='TB-ZH-CN-3'.encode(n.getEncoding(),errors='replace')
    target=dest/'agsfnt3.ttf';replacement.save(target)
    if allchars-set(TTFont(target).getBestCmap()):raise ValueError('Font 3 subset lost required glyphs')
    records.append(dict(name=target.name,added_glyphs=len(allchars),fallback_chars=fallback_chars,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),size=target.stat().st_size,method='TTF replaces WFN via AGS lookup; original bitmap Latin design changes',aliases=[{'codepoint':'U+2212','glyph_source':'U+002D'}]))
    write_json(dest/'font-report.json',dict(fonts=records,glyphs_required=len(allchars),visual_verification='pending'))
    manifest_path=dest/'build-manifest.json'
    if manifest_path.exists():
        manifest=read_json(manifest_path);manifest['files']=[r for r in manifest['files'] if not r['name'].startswith('agsfnt')]+[{k:v for k,v in r.items() if k in {'name','size','sha256'}} for r in records];write_json(manifest_path,manifest)
    print(json.dumps(records,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('assets');ap.add_argument('--development',action='store_true');a=ap.parse_args();make_fonts(a.assets,a.development)
