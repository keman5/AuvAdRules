import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('update', Path(__file__).resolve().parents[1] / 'scripts/update.py')
update = importlib.util.module_from_spec(spec)
spec.loader.exec_module(update)


class UpdateTests(unittest.TestCase):
    def test_shared_syntax_and_exceptions(self):
        self.assertEqual(update.parse('! comment\n[Adblock Plus]\n||ads.example.org^\n@@||safe.ads.example.org^\n||ads.example.org^'),
                         {'||ads.example.org^', '@@||safe.ads.example.org^'})

    def test_reject_non_dns_and_type_specific_rules(self):
        for bad in ['<html>Bad Gateway</html>', '||example.org^$dnstype=A',
                    '||example.org/path^', 'example.org##.ad', '||com^',
                    '||192.0.2.1^', '||bad..example.org^', '||-bad.example.org^']:
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                update.parse(bad)

    def test_large_change_is_rejected(self):
        with self.assertRaises(ValueError):
            update.validate_change(100, 69)
        with self.assertRaises(ValueError):
            update.validate_change(100, 151)
        update.validate_change(100, 95)

    def test_failed_update_preserves_last_good_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'filters').mkdir()
            target = root / 'filters/dns.txt'
            target.write_text('! last good\n||ads.example.org^\n')
            before = target.read_bytes()
            for bad in [b'<html>Unavailable</html>', b'! empty', b'||ads.example.org^']:
                with self.assertRaises(ValueError):
                    update.build({'adrules': bad, 'hagezi': bad}, root)
                self.assertEqual(target.read_bytes(), before)

    def test_supplement_excludes_exact_and_parent_coverage(self):
        base = {'||ads.example.org^', '@@||safe.example.org^'}
        custom = {'||ads.example.org^', '||child.ads.example.org^',
                  '@@||child.safe.example.org^', '||new.example.org^',
                  '@@||safe.ads.example.org^', '||notads.example.org^'}
        self.assertEqual(update.supplement(custom, base),
                         {'||new.example.org^', '@@||safe.ads.example.org^', '||notads.example.org^'})

    def test_empty_supplement_migration_and_no_op(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'rules').mkdir()
            (root / 'filters').mkdir()
            custom = root / 'rules/custom.txt'
            custom.write_text('! no additions\n')
            raw = ('\n'.join(f'||ad{i}.example.org^' for i in range(50_000)) + '\n').encode()
            target = root / 'filters/dns.txt'
            target.write_bytes(raw)  # Former full-copy publication.
            sources = {'adrules': raw, 'hagezi': raw}
            manifest = update.build(sources, root)
            self.assertEqual(manifest['published_rules'], 0)
            self.assertEqual(update.parse(target.read_text()), set())
            self.assertLess(target.stat().st_size, 1024)
            before = target.read_bytes()
            update.build({key: b'! changed comment\n' + raw for key in sources}, root)
            self.assertEqual(target.read_bytes(), before)
            custom.write_text('||ad1.example.org^\n||new.example.net^\n')
            result = update.build(sources, root)
            self.assertEqual(result['already_covered_rules'], 1)
            self.assertEqual(update.parse(target.read_text()), {'||new.example.net^'})
            # When either baseline gains the addition, remove it from the output.
            sources['adrules'] += b'||new.example.net^\n'
            self.assertEqual(update.build(sources, root)['published_rules'], 0)
            before = target.read_bytes()
            with self.assertRaises(ValueError):
                update.build({'adrules': raw, 'hagezi': b'<html>failure</html>'}, root)
            self.assertEqual(target.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
