#!/usr/bin/env python3
"""Build a common domain-only AdGuard DNS subscription. GPL-3.0."""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/multi.txt'
MAX_BYTES = 32 * 1024 * 1024
LABEL = r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?'
RULE = re.compile(r'(?:@@)?\|\|(' + LABEL + r'(?:\.' + LABEL + r')+)\^')


def parse(content):
    rules = set()
    for number, line in enumerate(content.splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('!') or line == '[Adblock Plus]':
            continue
        match = RULE.fullmatch(line)
        if not match or len(match[1]) > 253 or match[1].split('.')[-1].isdigit():
            raise ValueError(f'Unsupported DNS rule on line {number}')
        rules.add(line)
    return rules


def validate_change(previous, current):
    if previous:
        ratio = len(current) / len(previous)
        if not 0.7 <= ratio <= 1.5:
            raise ValueError('Rule count changed by more than -30%/+50%; review upstream manually')


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        os.chmod(temporary, 0o644)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def build(raw, root=ROOT):
    if len(raw) > MAX_BYTES:
        raise ValueError('Upstream exceeds download limit')
    upstream = parse(raw.decode('utf-8-sig'))
    if not 50_000 <= len(upstream) <= 500_000:
        raise ValueError('Unexpected upstream size; keep last good publication')
    custom = parse((root / 'rules/custom.txt').read_text())
    merged = upstream | custom
    destination = root / 'filters/dns.txt'
    previous = parse(destination.read_text()) if destination.exists() else set()
    validate_change(previous, merged)
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    body = '\n'.join(sorted(merged)) + '\n'
    # Keep the subscription unchanged when only upstream comments changed.
    if merged != previous or not destination.exists():
        header = '\n'.join([
            '! Title: AuvAdRules DNS',
            '! Description: HaGeZi Normal plus reviewed custom domain rules; IPv4 and IPv6 DNS',
            '! Homepage: https://github.com/keman5/AuvAdRules',
            '! License: GPL-3.0; see LICENSE and SOURCES.md',
            '! Expires: 12 hours',
            f'! Last modified: {now}',
            f'! Version: {now}',
            f'! Number of entries: {len(merged)}',
            f'! Source: {SOURCE}',
        ]) + '\n'
        atomic_write(destination, (header + body).encode())
    manifest = {
        'checked_at_utc': now,
        'source': SOURCE,
        'source_sha256': hashlib.sha256(raw).hexdigest(),
        'source_rules': len(upstream),
        'custom_rules': len(custom),
        'published_rules': len(merged),
        'published_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
        'device_ad_removal_verified': False,
    }
    atomic_write(root / 'filters/manifest.json', (json.dumps(manifest, indent=2) + '\n').encode())
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-file', type=Path, help='Offline verification with a downloaded upstream snapshot')
    args = parser.parse_args()
    if args.source_file:
        raw = args.source_file.read_bytes()
    else:
        request = urllib.request.Request(SOURCE, headers={'User-Agent': 'AuvAdRules/1.0'})
        with urllib.request.urlopen(request, timeout=60) as response:
            if response.status != 200:
                raise ValueError(f'Upstream HTTP {response.status}')
            raw = response.read(MAX_BYTES + 1)
    result = build(raw)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
