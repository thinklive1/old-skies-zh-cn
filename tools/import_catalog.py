"""Create immutable English catalog and independent editable translation shards."""
from pathlib import Path
import argparse, hashlib, json, re, collections

def classify(source, occurrences):
    if all(o['script']=='Commentary.asc' for o in occurrences):
        return 'excluded', '开发者解说沿用英文'
    if all(o['kind']=='parser-dictionary' for o in occurrences):
        return 'excluded', '文本解析器词典；直接替换会改变输入识别'
    if re.fullmatch(r'&\d+\s*',source):
        return 'preserve', '仅语音编号；无可翻译正文'
    if re.fullmatch(r'(?:Hotspot \d+|Object \d+|No hotspot|New (?:Label|Button))',source):
        return 'excluded', '编辑器默认占位名称'
    if re.fullmatch(r'[^\s]+\.(?:asc|ash|crm|dta|bmp|png|wav|ogg|mp3|avi|ogv|tmp|dat|txt)',source,re.I) or source.startswith(('$SAVEGAMEDIR$','$APPDATADIR$','$INSTALLDIR$')):
        return 'excluded', '运行时资源路径'
    if re.fullmatch(r'[\d\s%+*/:#._-]+',source):
        return 'preserve', '数字或符号'
    return 'untranslated', ''

def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

def create(raw, archive, root):
    raw=json.loads(Path(raw).read_text('utf-8')); index=json.loads(Path(archive).read_text('utf-8'))
    entries=raw.pop('entries'); grouped=collections.OrderedDict()
    for entry in entries:
        source=entry.pop('source'); grouped.setdefault(source,[]).append(entry)
    catalog=[]; shards=collections.defaultdict(list)
    for sequence,(source,refs) in enumerate(grouped.items(),1):
        uid=hashlib.sha256(source.encode('utf-8')).hexdigest()[:16]
        status,reason=classify(source,refs)
        row=dict(id=uid,sequence=sequence,source=source,occurrences=refs)
        catalog.append(row)
        shard='ui' if any(o['kind'] in ['gui-label','gui-button','character','inventory'] for o in refs) else refs[0]['asset'].removesuffix('.crm').removesuffix('.dta')
        shards[shard].append(dict(id=uid,source=source,target=source if status=='preserve' else '',status=status,reason=reason,review_notes=''))
    root=Path(root)
    if (root/'source/catalog.en.json').exists():
        raise ValueError('Catalog exists; use a reviewed migration rather than overwrite translations')
    write_json(root/'source/catalog.en.json',catalog)
    write_json(root/'source/game.json',raw)
    write_json(root/'source/baseline.json',dict(appid=307580,steam_build=24559207,exe_sha256=index['exe_sha256'],exe_size=index['exe_size'],engine=raw['engine'],game_uid=raw['game_uid'],source_sha256=hashlib.sha256((root/'source/catalog.en.json').read_bytes()).hexdigest(),asset_manifest=index['assets']))
    for name,rows in shards.items(): write_json(root/'translation'/f'{name}.zh-CN.json',rows)
    counts=collections.Counter(r['status'] for rows in shards.values() for r in rows)
    print(json.dumps(dict(unique=len(catalog),occurrences=len(entries),status=counts,shards=len(shards)),ensure_ascii=False))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('raw');ap.add_argument('archive');ap.add_argument('project');a=ap.parse_args();create(a.raw,a.archive,a.project)
