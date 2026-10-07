"""Fixtures for byte-limited contextual key splitting and checksum rejection."""
import hashlib, struct, unittest
from copy import deepcopy
from context_data import patch_asset, aliases
from encoding_bridge import select_pairs
from tra import compile_tra, parse_tra


class ContextData(unittest.TestCase):
    def setUp(self):
        self.original = b'header|&1 Hi!\0|code|&1 Hi!\0|end'
        story = self.original.index(b'&1 Hi!')
        comment = self.original.index(b'&1 Hi!', story + 1)
        self.changed = self.original.replace(b'&1 Hi!', b'&1 Hi.', 1)
        self.spec = dict(asset_size=len(self.original),
            source_sha256=hashlib.sha256(self.original).hexdigest(),
            patched_sha256=hashlib.sha256(self.changed).hexdigest(),
            changed_bytes=[story + 5],
            entries=[dict(source='&1 Hi!', runtime_key='&1 Hi.',
                story_offset=story, commentary_offset=comment)])

    def test_story_split_preserves_commentary_and_all_other_bytes(self):
        self.assertEqual(patch_asset(self.original, self.spec), self.changed)
        self.assertEqual(len(self.original), len(self.changed))
        self.assertTrue(self.changed.endswith(b'|code|&1 Hi!\0|end'))

    def test_wrong_source_rejected(self):
        for data in (self.original + b'x', b'X' + self.original[1:]):
            with self.assertRaises(ValueError): patch_asset(data, self.spec)

    def test_bad_recipe_offsets_lengths_or_hash_rejected(self):
        for change in ('story', 'commentary', 'length', 'changes', 'hash'):
            spec = deepcopy(self.spec)
            if change in ('story', 'commentary'): spec['entries'][0][change + '_offset'] += 1
            if change == 'length': spec['entries'][0]['runtime_key'] += 'X'
            if change == 'changes': spec['changed_bytes'] = []
            if change == 'hash': spec['patched_sha256'] = '0' * 64
            with self.subTest(change=change), self.assertRaises(ValueError): patch_asset(self.original, spec)

    def test_actual_recipe_pairs_keep_commentary_english(self):
        for uid, entry in aliases().items():
            rows = [dict(id=uid, source=entry['source'], target='&' + entry['source'].split()[0][1:] + ' 测试译文', status='reviewed', reason='')]
            pairs, bridges = select_pairs(rows)
            result = parse_tra(compile_tra(pairs, 1, 'Test'))['pairs']
            self.assertEqual(result[entry['source']], entry['source'])
            self.assertEqual(result[entry['runtime_key']], rows[0]['target'])
            self.assertEqual(bridges, [uid])
            self.assertEqual(rows[0]['status'], 'reviewed')
            rows[0]['status'] = 'untranslated'
            self.assertEqual(dict(select_pairs(rows)[0])[entry['runtime_key']], entry['source'])

    def test_runtime_alias_collision_rejected(self):
        entry = next(iter(aliases().values()))
        rows = [dict(id='fixture', source=entry['runtime_key'], target='', status='untranslated', reason='')]
        with self.assertRaises(ValueError): select_pairs(rows)

    def gui_fixture(self):
        original=struct.pack('<i',84)+self.original[4:]
        modified=bytearray(original)
        story=self.spec['entries'][0]['story_offset']
        modified[story+5]=ord('.')
        modified[:4]=struct.pack('<i',212)
        spec=deepcopy(self.spec)
        spec.update(source_sha256=hashlib.sha256(original).hexdigest(),
                    patched_sha256=hashlib.sha256(modified).hexdigest(),
                    changed_bytes=[0,story+5],gui_controls=[dict(offset=0,
                    before_flags=84,after_flags=212,fingerprint=original[:4].hex())])
        return original,bytes(modified),spec

    def test_gui_translation_bit_preserves_all_other_bytes(self):
        original,modified,spec=self.gui_fixture()
        self.assertEqual(patch_asset(original,spec),modified)
        self.assertEqual(struct.unpack_from('<i',modified)[0]^84,128)

    def test_gui_fingerprint_or_unrelated_flag_changes_rejected(self):
        original,_,spec=self.gui_fixture()
        for kind in ['fingerprint','flags','offset']:
            altered=deepcopy(spec)
            if kind=='fingerprint':altered['gui_controls'][0]['fingerprint']='00000000'
            if kind=='flags':altered['gui_controls'][0]['after_flags']=213
            if kind=='offset':altered['gui_controls'][0]['offset']=-1
            with self.subTest(kind=kind),self.assertRaises(ValueError):
                patch_asset(original,altered)


if __name__ == '__main__': unittest.main()
