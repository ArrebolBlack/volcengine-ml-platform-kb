"""Check the small knowledge base; no cloud calls or third-party dependencies."""

from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


def main():
    root = Path(__file__).resolve().parents[1]
    files = [p for p in root.rglob('*') if p.is_file()
             and not any(part.startswith('.') or part == '__pycache__'
                         or part == 'local_private' for part in p.relative_to(root).parts)]
    errors = []
    # 2026-10: Zenith adds one runbook, a small HTTP helper/test and two JSON examples.
    if len(files) > 25 or sum(p.stat().st_size for p in files) > 1024 * 1024:
        errors.append('Active knowledge exceeds 25 files or 1 MiB; review duplication.')
    if len((root / 'README.md').read_text(encoding='utf-8').splitlines()) > 60:
        errors.append('Root README exceeds 60 lines.')
    allowed_suffixes = {'.md', '.yaml', '.py', '.json'}
    for path in files:
        rel = path.relative_to(root)
        if path.suffix not in allowed_suffixes:
            errors.append(f'{rel}: unexpected artifact type')
        if path.name != 'README.md' and path.name != 'INDEX.md':
            index = path.parent / ('README.md' if path.parent == root else 'INDEX.md')
            if not index.exists() or f']({path.name})' not in index.read_text(encoding='utf-8'):
                errors.append(f'{rel}: missing direct index entry')
        if path.suffix != '.md':
            continue
        text = path.read_text(encoding='utf-8')
        for target in re.findall(r'\]\(([^)]+)\)', text):
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                errors.append(f'{rel}: invalid local link {target}')
    for folder in ('docs', 'examples', 'institutions', 'scripts'):
        if f']({folder}/INDEX.md)' not in (root / 'README.md').read_text(encoding='utf-8'):
            errors.append(f'{folder}: missing root route')
    expected = {'TASK_NAME', 'IMAGE_URL', 'QUEUE_NAME', 'FLAVOR', 'VEPFS_ID', 'VEPFS_SUBPATH'}
    for path in (root / 'examples').glob('*.yaml'):
        text = path.read_text(encoding='utf-8')
        placeholders = set(re.findall(r'__([A-Z_]+)__', text)) - {'NAME'}
        if placeholders != expected:
            errors.append(f'{path.name}: undocumented or missing input placeholder')
        if re.search(r'haoce|se3wam|queue0\d+|v20260724|20252203765', text, re.I):
            errors.append(f'{path.name}: project/account-specific value')
        if re.search(r'(?m)^(Image|ResourceGroupID):', text):
            errors.append(f'{path.name}: legacy submit field')
        if re.search(r'(?m)^(UserCodePath|ImageCredential):', text):
            errors.append(f'{path.name}: unreviewed code upload or credential block')
    for error in errors:
        print(error)
    if errors:
        raise SystemExit(1)
    print(f'OK: {len(files)} active files, {sum(p.stat().st_size for p in files)} bytes; '
          'links, indexes and example boundaries checked. Cloud execution not tested.')


if __name__ == '__main__':
    main()
