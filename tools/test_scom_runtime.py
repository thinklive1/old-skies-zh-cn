"""Guard minimal SCOM detours against data loss and unsupported layouts."""
import struct, unittest
from catalog import ROOT, read_json
from scom_runtime import parse, serialize, translate_scrollers


def fixture():
    table=read_json(ROOT/'source/scom-instructions.json')
    op={i['name']:i['opcode'] for i in table}
    code=[0]*4504;code[10:12]=[op['sourceline'],9];code[2221:2223]=[op['sourceline'],99]
    def s(text):return text.encode('ascii')+b'\0'
    tail=struct.pack('<i',2)+s('MakeScrollList$2')+struct.pack('<I',0x01000000)
    tail+=s('MakeEmail$4')+struct.pack('<I',0x01000000|2193)
    tail+=struct.pack('<i',1)+s('Scrollers.asc')+struct.pack('<iI',0,0xBEEFCAFE)
    names=['ScrollText1','ScrollText2','ScrollText3','ScrollText4','ListBoxEmailMessage1',
           'String::Truncate^1','String::get_Length','String::geti_Chars','String::AppendChar^1',
           'String::Append^1','ListBox::AddItem^1','ListBox::Clear^0']
    model=dict(version=90,globals=b'private-data',code=code,
               strings=b'unused\0English\0FROM:\0RECEIVED:\0SUBJECT:\0--------------------\0 \0',
               fixups=[(3,5)],imports=['','','']+names,tail=tail)
    return serialize(model),table


class ScrollerDetours(unittest.TestCase):
    def test_roundtrip_preserves_unreferenced_pool_and_all_bytes(self):
        blob,_=fixture();self.assertEqual(serialize(parse(blob)),blob)

    def test_only_two_source_lines_change_and_existing_pointers_survive(self):
        blob,table=fixture();patched,report=translate_scrollers(blob,table)
        a,b=parse(blob),parse(patched)
        self.assertEqual(report['changed_code_cells'],[10,11,2221,2222])
        for key in ['globals','strings','exports','sections','tail']:
            self.assertEqual(a[key],b[key])
        self.assertEqual(a['fixups'],b['fixups'][:len(a['fixups'])])
        self.assertEqual(b['imports'][0],'GetTranslation')
        for index,name in enumerate(a['imports']):
            if name:self.assertEqual(name,b['imports'][index])
        self.assertEqual(report['added_imports'],['GetTranslation','GetTextWidth','IsTranslationAvailable'])
        self.assertTrue(all(4504<=p<len(b['code']) for _,p in report['added_fixups']))

    def test_wrong_hook_or_occupied_import_rejected(self):
        blob,table=fixture()
        for kind in ['line','import','overlap']:
            script=parse(blob)
            if kind=='line':script['code'][11]=10
            if kind=='import':script['imports'][0]='ExistingFunction'
            if kind=='overlap':script['fixups'].append((3,11))
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                translate_scrollers(serialize(script),table)

    def test_double_patch_and_trailing_bytes_rejected(self):
        blob,table=fixture();patched,_=translate_scrollers(blob,table)
        for candidate in [patched,blob+b'extra']:
            with self.assertRaises(ValueError):translate_scrollers(candidate,table)

    def test_wrong_header_or_truncated_block_rejected(self):
        blob,_=fixture()
        for candidate in [b'XXXX'+blob[4:],blob[:17],blob[:-1]]:
            with self.assertRaises((ValueError,struct.error)):parse(candidate)


if __name__=='__main__':unittest.main()
