"""Export nine-column budget rows for a calendar month by posting date."""
import argparse
import csv
from datetime import date
from pathlib import Path


def export_month(input_path, output_dir, year, month):
    start = date(year, month, 1)
    end = date(year + (month == 12), month % 12 + 1, 1)
    selected = []
    with Path(input_path).open(newline='', encoding='utf-8') as stream:
        for number, row in enumerate(csv.reader(stream), 1):
            if len(row) != 9:
                raise ValueError(f'Input row {number}: expected 9 columns, got {len(row)}')
            effective, posted = date.fromisoformat(row[0]), date.fromisoformat(row[1])
            if start <= posted < end:
                selected.append(row)
    selected.sort(key=lambda row: (row[1], row[0]))
    if not selected:
        raise ValueError('No rows posted in the requested month; no exports written')
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stem = f'out.{year:04d}-{month:02d}'
    for extension, delimiter in [('csv', ','), ('tsv', '\t')]:
        path = directory / f'{stem}.{extension}'
        with path.open('w', newline='', encoding='utf-8') as stream:
            csv.writer(stream, delimiter=delimiter).writerows(selected)
        with path.open(newline='', encoding='utf-8') as stream:
            if list(csv.reader(stream, delimiter=delimiter)) != selected:
                raise ValueError(f'Export round-trip failed: {path}')
    text = (directory / f'{stem}.tsv').read_bytes().decode('utf-8')
    clipboard = directory / f'{stem}.clipboard.txt'
    clipboard.write_bytes(text.encode('utf-16le'))
    if clipboard.read_bytes().decode('utf-16le') != text:
        raise ValueError('Clipboard encoding round-trip failed')
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year', type=int, required=True)
    parser.add_argument('--month', type=int, choices=range(1, 13), required=True)
    parser.add_argument('--input', type=Path, default=Path('out/out.csv'))
    parser.add_argument('--output-dir', type=Path, default=Path('out'))
    args = parser.parse_args()
    rows = export_month(args.input, args.output_dir, args.year, args.month)
    todos = sum(row[3].startswith('TODO') for row in rows)
    print(f'{args.year:04d}-{args.month:02d}: {len(rows)} rows by posting date, '
          f'9 columns, {todos} TODOs; CSV, TSV and UTF-16LE files in {args.output_dir}')


if __name__ == '__main__':
    main()
