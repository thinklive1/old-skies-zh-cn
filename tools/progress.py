"""Produce an honest, reproducible progress inventory from the current catalog."""
import collections, datetime, hashlib
from catalog import ROOT, load, read_json, write_json

def report():
    source, rows, _ = load()
    counts = collections.Counter(r['status'] for r in rows.values())
    scripts = collections.defaultdict(collections.Counter)
    rooms = collections.defaultdict(collections.Counter)
    for original in source:
        status = rows[original['id']]['status']
        for name in {r['script'] for r in original['occurrences'] if r['script']}:
            scripts[name][status] += 1
        for name in {r['asset'] for r in original['occurrences'] if r['asset'].endswith('.crm')}:
            rooms[name][status] += 1
    cfg = read_json(ROOT/'project.json')
    gates = read_json(ROOT/'review/release-gates.json')
    issues = [read_json(p) for p in sorted((ROOT/'review/issues').glob('*.json'))]
    output = dict(
        generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        version=cfg['version'], release_state=cfg['release_state'],
        source_sha256=hashlib.sha256((ROOT/'source/catalog.en.json').read_bytes()).hexdigest(),
        translation_sha256=hashlib.sha256(b''.join(p.read_bytes() for p in sorted((ROOT/'translation').glob('*.json')))).hexdigest(),
        unique_source_keys=len(source), occurrences=sum(len(r['occurrences']) for r in source),
        translated_total=counts['translated']+counts['reviewed'], counts=dict(counts),
        scope_finalized=gates['source_scope_review_complete'],
        complete=not(counts['untranslated'] or counts['translated']) and all(v is True for v in gates.values()) and cfg['release_state']=='ready',
        scripts=dict(sorted(scripts.items())), rooms=dict(sorted(rooms.items())),
        unresolved_release_issues=[i['id'] for i in issues if i.get('release_blocking') and i.get('status')!='resolved'],
        next_work=(['用户进入游戏确认可见画面与正常游玩；收到反馈后记录验收或针对问题修订。'] if cfg['release_state']=='ready' else [
            '继续翻译各章对白、全局物品描述与对话选项；初期房间并不等于章节全文已完成。',
            '对照脚本调用确认内部控制键、调试文本、联系人与名单的最终范围；不可凭大写或长度直接排除。',
            '维持已实现的剧情/解说键分离：核对每次候选的运行时别名、英文解说与外置数据校验值。',
            '逐批二轮校对，锁定暂定译名与解谜指向；译文修改后重做凭据。',
            '核对实际游戏字体 3 的用途、中文换行、字幕宽度及界面布局。',
            '完整游戏检查、用户配置激活与正式发行包装；达到门槛后再安装正式目录。'
        ])
    )
    write_json(ROOT/'review/progress.json',output)
    print(f"{output['translated_total']} translated, {counts['reviewed']} reviewed, {counts['untranslated']} pending; scope "+('finalized' if output['scope_finalized'] else 'preliminary'))

if __name__=='__main__':report()
