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
            update.validate_change(set(range(100)), set(range(69)))
        with self.assertRaises(ValueError):
            update.validate_change(set(range(100)), set(range(151)))
        update.validate_change(set(range(100)), set(range(95)))

    def test_failed_update_preserves_last_good_file(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'filters').mkdir()
            target = root / 'filters/dns.txt'
            target.write_text('! last good\n||ads.example.org^\n')
            before = target.read_bytes()
            for bad in [b'<html>Unavailable</html>', b'! empty', b'||ads.example.org^']:
                with self.assertRaises(ValueError):
                    update.build(bad, root)
                self.assertEqual(target.read_bytes(), before)

    def test_merge_and_no_op_keep_subscription_timestamp(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'rules').mkdir()
            (root / 'rules/custom.txt').write_text('@@||safe.example.org^\n')
            raw = ('\n'.join(f'||ad{i}.example.org^' for i in range(50_000)) + '\n').encode()
            manifest = update.build(raw, root)
            self.assertEqual(manifest['published_rules'], 50_001)
            target = root / 'filters/dns.txt'
            before = target.read_bytes()
            update.build(b'! new upstream comment\n' + raw, root)
            self.assertEqual(target.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
