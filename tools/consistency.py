from catalog import ROOT
from apply_review import apply
import collections,json,re

rows=json.loads((ROOT/'catalog.json').read_text('utf-8'))
accepted=collections.defaultdict(set)
for row in rows:
    if row['target']!=row['original']:accepted[row['original']].add(row['target'])
shared={old:next(iter(values)) for old,values in accepted.items() if len(values)==1}
shared.update({
    '您单击按钮。':'你按下按钮。',
    '您单击按钮':'你按下按钮。',
    '你决定介入':'你决定走进去。',
    '这是一台奇怪的不合时宜的自动售货机。':'这台自动售货机，有些古怪，与这里格格不入。',
    '这是你那台奇怪的不合时宜的自动售货机。':'这是你那台古怪的自动售货机，与这里格格不入。',
    '它似乎分配了...音乐？？':'它出货的东西，好像是……音乐？？',
    '它似乎分配了音乐':'它似乎能播放音乐。',
    '它似乎可以分配音乐？':'它似乎能播放音乐？',
    '使用机器吗？':'要使用这台机器吗？',
    '你决定不使用机器':'你决定暂时不使用这台机器。',
    '你已经去过这个房间了。。':'这个房间，你已经来过了……',
    '...你不确定这意味着什么':'……你不确定这是什么意思。',
    '...奇怪的':'……真奇怪。',
    '再来一次我就可以交易了！':'再找一枚，就能换了！',
})
protected=re.compile(r'(\{[^}]*\}|\[[^\]]*\]|\\(?:[nrt"\'\\]|u[0-9a-fA-F]{4}))')
han=r'\u3400-\u9fff'
changes={}
for row in rows:
    value=row['target']
    if value==row['original'] and value in shared:value=shared[value]
    for old,new in [('内存深度','记忆深处'),('内存核心','记忆核心'),('临时房间','时空房间')]:
        value=value.replace(old,new)
    value=value.replace('{/字体}','{/font}').replace('{/颜色}','{/color}').replace('{/尺寸}','{/size}').replace('{size=*0。5}','{size=*0.5}').replace('[persistent。coins]','[persistent.coins]').replace('[镇民]','[townpeople]')
    parts=protected.split(value)
    for i in range(0,len(parts),2):
        text=parts[i]
        if not re.search('['+han+']',text):continue
        text=re.sub('(['+han+r'])\s*,\s*',r'\1，',text)
        text=re.sub(r',\s*(?=['+han+'])','，',text)
        text=re.sub('(['+han+r'])\.(?!\.)',r'\1。',text)
        text=text.replace('。。','……')
        text=re.sub(r'\.{2,}','……',text)
        parts[i]=text
    value=''.join(parts)
    e=row.get('english') or ''
    # Keep artists' registered names rather than assigning unrelated dictionary meanings.
    artist_range=(1398<=row['id']<=2617 or 2647<=row['id']<=2722 or 2730<=row['id']<=3231)
    if artist_range and row['label'].endswith('sign') and re.fullmatch(r'[A-Z0-9 !.*+:;_-]{2,45}',e) and not e.startswith(('HOP ','97 ')):
        value=e
    if value!=row['target']:changes[row['id']]=value
apply('0013-consistency-punctuation',changes,allow_tag_repair=True)
