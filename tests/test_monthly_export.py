"""Posting-month exports preserve purchase dates, signs and duplicate rows."""
import csv
import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / '.agents/skills/monthly-budget-update/scripts/export_month.py'
spec = importlib.util.spec_from_file_location('monthly_export', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TestMonthlyExport(unittest.TestCase):
    def test_posted_boundaries_duplicates_and_encoding(self):
        def row(effective, posted, amount='4.80'):
            return [effective, posted, amount, 'Discretionary', '', 'Example trip',
                    'Café, shop\titem', '', 'Example bank']
        duplicate = row('2025-08-30', '2025-09-01')
        last_day = row('2025-09-29', '2025-09-30', '-12.34')
        october = row('2025-09-30', '2025-10-01')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'input.csv'
            with source.open('w', newline='', encoding='utf-8') as stream:
                csv.writer(stream).writerows([october, last_day, duplicate, duplicate,
                                             row('2025-08-29', '2025-08-31')])
            result = module.export_month(source, root / 'out', 2025, 9)
            self.assertEqual(result, [duplicate, duplicate, last_day])
            self.assertEqual(module.export_month(source, root / 'out', 2025, 10), [october])
            clipboard = (root / 'out/out.2025-09.clipboard.txt').read_bytes().decode('utf-16le')
            self.assertEqual(clipboard, (root / 'out/out.2025-09.tsv').read_bytes().decode('utf-8'))

    def test_december_and_invalid_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'input.csv'
            row = ['2025-11-30', '2025-12-31', '10', 'Groceries', '', '', 'Test', '', 'Bank']
            with source.open('w', newline='') as stream:
                csv.writer(stream).writerows([row])
            self.assertEqual(module.export_month(source, root / 'out', 2025, 12), [row])
            source.write_text('bad,row\n')
            with self.assertRaises(ValueError):
                module.export_month(source, root / 'out', 2025, 12)


if __name__ == '__main__':
    unittest.main()
