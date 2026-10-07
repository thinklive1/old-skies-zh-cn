"""Regression fixtures for encoding, dictionary matching and protected tokens."""
import unittest,struct
from tra import compile_tra,parse_tra
from catalog import protected,errors
from encoding_bridge import select_pairs

class Formats(unittest.TestCase):
    def test_percentages_and_real_placeholders_in_prose(self):
        source='99% of %d records, with a 53% loss and 86.8% chance'
        target='共 %d 条记录的 99%，损失 53%，概率 86.8%'
        self.assertEqual(protected(source),protected(target))
        self.assertIn('changed protected tokens',errors(dict(source=source,target=target.replace('53%','35%'),status='translated')))
        self.assertEqual(protected('Value: % d')['printf'],['% d'])
    def test_identity_bridges_do_not_count_as_translations(self):
        rows=[dict(id='1',source='São Paulo',target='',status='untranslated',reason=''),
              dict(id='2',source='&285 Puskás',target='',status='excluded',reason='开发者解说沿用英文'),
              dict(id='3',source='Plain English',target='',status='untranslated',reason=''),
              dict(id='4',source='Hello',target='你好',status='translated',reason=''),
              dict(id='5',source='café.png',target='',status='excluded',reason='运行时资源路径')]
        pairs,bridges=select_pairs(rows,True)
        self.assertEqual(bridges,['1','2'])
        self.assertEqual(dict(pairs),{'São Paulo':'São Paulo','&285 Puskás':'&285 Puskás','Hello':'你好'})
        self.assertEqual(rows[0]['status'],'untranslated')
        self.assertEqual(parse_tra(compile_tra(pairs,1,'Test'))['pairs'],dict(pairs))
        self.assertNotIn('Hello',dict(select_pairs(rows,False)[0]))
    def test_mixed_cp1252_and_utf8(self):
        pairs=[('Puskás','普什卡什'),('São Paulo','圣保罗'),('&99 Wait...','&99 等等……'),('Use %s on %s','把%s用在%s上')]
        d=parse_tra(compile_tra(pairs,1186933,'Technobabylon'))
        self.assertEqual(d['pairs'],dict(pairs));self.assertEqual(d['options']['encoding'],'UTF-8')
        self.assertEqual(d['uid'],1186933);self.assertEqual(d['fonts_direction'],(-1,-1,1))
        for source in d['pairs']:self.assertEqual(source.encode('cp1252').decode('cp1252'),source)
    def test_voice_and_format_tokens(self):
        self.assertEqual(protected('&1 %s[[@IN@'),protected('&1 中文%s[[@IN@'))
        r=dict(source='&2 Hello %d[',target='&3 你好%s',status='translated')
        self.assertIn('changed protected tokens',errors(r))
    def test_truncated_rejected(self):
        d=compile_tra([('Hi','你好')],1,'Test')
        for cut in [0,15,20,len(d)-1]:
            with self.assertRaises((ValueError,struct.error)):parse_tra(d[:cut])
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):compile_tra([('Hi','你好'),('Hi','您好')],1,'Test')
    def test_empty_rejected(self):
        with self.assertRaises(ValueError):compile_tra([('Hi','')],1,'Test')
    def test_trailing_rejected(self):
        with self.assertRaises(ValueError):parse_tra(compile_tra([('Hi','你好')],1,'Test')+b'x')

if __name__=='__main__':unittest.main()
