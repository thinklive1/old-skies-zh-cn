"""Refuse formal release while language review or real game validation is pending."""
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'source/translations.v1.1.json').read_text(encoding='utf-8'))
pending=sum(r['status']=='inherited_not_reviewed' for r in rows)
errors=[]
if pending:errors.append(f'{pending} translation pairs are not individually reviewed')
playtest=root/'qa/playtest.json'
if not playtest.exists():errors.append('real game playtest report is absent')
else:
 report=json.loads(playtest.read_text(encoding='utf-8'))
 if not (report.get('passed') is True and report.get('version')=='1.1' and report.get('zip_sha256')):errors.append('real game playtest report is incomplete')
if errors:
 print('FORMAL RELEASE BLOCKED: '+'; '.join(errors));sys.exit(1)
print('Language and real-game gates passed; validate final ZIP and approvals before publishing.')
