import pathlib, json

# 1. Check output files exist
out = pathlib.Path('data/processed/text')
txts = sorted(out.rglob('*.txt'))
print('Output .txt files found:', len(txts))
for t in txts:
    size = t.stat().st_size
    print(' ', t.relative_to(out), ' (', size, 'bytes)')

# 2. Verify page boundaries in one sample file
sample = txts[0]
content = sample.read_text(encoding='utf-8')
boundaries = [line for line in content.splitlines() if '<<<PAGE_BREAK' in line]
print('Sample:', sample.name, '- page boundaries found:', len(boundaries))
print('First boundary:', boundaries[0].strip())
print('Last boundary: ', boundaries[-1].strip())

# 3. Spot-check a snippet of actual extracted text
non_empty = [chunk.strip() for chunk in content.split('<<<PAGE_BREAK') if chunk.strip()]
print('First text snippet (first 300 chars):', non_empty[0][:300] if non_empty else 'EMPTY')

# 4. Load and show summary JSON
summary = json.loads(pathlib.Path('data/processed/logs/phase1_summary.json').read_text())
print('PDFs discovered:', summary['pdfs_discovered'])
print('Succeeded:', summary['succeeded'])
print('Failed:', summary['failed'])
print('Total pages:', summary['total_pages'])
print('Total chars:', summary['total_chars'])
print('Empty pages:', summary['total_empty_pages'])

# 5. Show per-PDF page counts
print('--- Per-PDF results ---')
for r in summary['results']:
    pdf_name = pathlib.Path(r['pdf']).name
    print(pdf_name, '| pages:', r['pages'], '| chars:', r['total_chars'], '| empty_pages:', r['empty_pages'], '| status:', r['status'])
