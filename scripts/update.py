#!/usr/bin/env python3
"""Build supplemental DNS rules without redistributing the baselines. GPL-3.0."""
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
BASELINES = {
    'adrules': 'https://adguardteam.github.io/HostlistsRegistry/assets/filter_29.txt',
    'hagezi': 'https://adguardteam.github.io/HostlistsRegistry/assets/filter_34.txt',
}
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
        ratio = current / previous
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


def parse_baseline(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('Baseline exceeds download limit')
    content = raw.decode('utf-8-sig')
    if '<html' in content.lower() or '<!doctype' in content.lower():
        raise ValueError('Baseline returned HTML')
    # Baselines may contain regex and modifiers. Only plain domain rules are
    # used for automatic deduplication; other syntax requires engine review.
    lines = [line.strip() for line in content.splitlines()
             if line.strip() and not line.startswith('!') and line != '[Adblock Plus]']
    domains = {line for line in lines if RULE.fullmatch(line)}
    if not 50_000 <= len(domains) <= 500_000:
        raise ValueError('Unexpected baseline size; keep last good publication')
    return domains, len(lines) - len(domains)


def supplement(custom, baseline):
    def covered(rule):
        prefix = '@@||' if rule.startswith('@@') else '||'
        labels = RULE.fullmatch(rule)[1].split('.')
        return any(prefix + '.'.join(labels[i:]) + '^' in baseline
                   for i in range(len(labels) - 1))
    return {rule for rule in custom if not covered(rule)}


def build(raw_sources, root=ROOT):
    if set(raw_sources) != set(BASELINES):
        raise ValueError('Both baselines are required')
    manifest_path = root / 'filters/manifest.json'
    previous_manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    baseline = set()
    sources = {}
    for key, url in BASELINES.items():
        rules, other = parse_baseline(raw_sources[key])
        previous = previous_manifest.get('baselines', {}).get(key, {}).get('domain_rules', 0)
        validate_change(previous, len(rules))
        baseline.update(rules)
        sources[key] = {'url': url, 'sha256': hashlib.sha256(raw_sources[key]).hexdigest(),
                        'domain_rules': len(rules), 'other_rules_not_compared': other}
    custom = parse((root / 'rules/custom.txt').read_text())
    output = supplement(custom, baseline)
    destination = root / 'filters/dns.txt'
    previous = parse(destination.read_text()) if destination.exists() else None
    now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    # Zero additions is valid. Never insert dummy blocks or baseline rules.
    # Migration from the former full list is deliberately not count-guarded.
    if output != previous or previous_manifest.get('mode') != 'supplement-only':
        header = '\n'.join([
            '! Title: AuvAdRules DNS Supplement',
            '! Description: Supplement only; enable AdRules filter_29 and HaGeZi Normal separately.',
            '! Homepage: https://github.com/keman5/AuvAdRules',
            '! License: GPL-3.0; see LICENSE and SOURCES.md',
            '! Expires: 12 hours',
            f'! Last modified: {now}',
            f'! Version: {now}',
            f'! Number of entries: {len(output)}',
            '! No verified additions yet.' if not output else '! Reviewed custom domain rules:',
        ]) + '\n'
        body = ''.join(rule + '\n' for rule in sorted(output))
        atomic_write(destination, (header + body).encode())
    manifest = {
        'mode': 'supplement-only',
        'checked_at_utc': now,
        'baselines': sources,
        'custom_rules': len(custom),
        'already_covered_rules': len(custom - output),
        'published_rules': len(output),
        'published_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
        'device_ad_removal_verified': False,
    }
    atomic_write(manifest_path, (json.dumps(manifest, indent=2) + '\n').encode())
    return manifest


def main():
    parser = argparse.ArgumentParser()
    for key in BASELINES:
        parser.add_argument('--' + key + '-file', type=Path, help='Offline baseline snapshot')
    args = parser.parse_args()
    raw_sources = {}
    for key, url in BASELINES.items():
        path = getattr(args, key + '_file')
        if path:
            raw_sources[key] = path.read_bytes()
        else:
            request = urllib.request.Request(url, headers={'User-Agent': 'AuvAdRules/2.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                if response.status != 200:
                    raise ValueError(f'Baseline HTTP {response.status}')
                raw_sources[key] = response.read(MAX_BYTES + 1)
    print(json.dumps(build(raw_sources), indent=2))


if __name__ == '__main__':
    main()
