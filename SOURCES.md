# Sources and licensing

The baseline is [HaGeZi Multi NORMAL](https://github.com/hagezi/dns-blocklists),
`adblock/multi.txt`, distributed under GPL-3.0. The complete license is included
in `LICENSE`. HaGeZi's underlying source acknowledgements and attribution are
maintained in [its README](https://github.com/hagezi/dns-blocklists/blob/main/README.md).
This repository's scripts, custom rules and combined output are also GPL-3.0.

The baseline corresponds to the Normal list offered as `filter_34` by AdGuard's
HostlistsRegistry. Rule counts and revisions may differ between refresh times.
Do not enable both copies solely to increase coverage; identical rules add no
coverage.

Each successful build records the fetched source URL, SHA-256, rule counts,
output SHA-256 and check time in `filters/manifest.json`. Git history retains
previous published versions. Failed updates leave the published list unchanged.

## App-specific evidence

| App | Evidence | Acceptance status |
| --- | --- | --- |
| 闲鱼 | Baseline includes advertising / telemetry domains; no captured current-version splash request attributed here | Not device-verified |
| 京东 | Baseline includes domains such as `ads-union.jd.com` and `addata.jd.com`; domain presence alone does not prove splash removal | Not device-verified |
| 爱思助手 | [Public URL-rewrite reference](https://github.com/fmz200/wool_scripts/blob/main/Surge/module/split/partA/AiSiAssistant.sgmodule) targets `list-app-m.i4.cn/getopfstadinfo.xhtml` | DNS cannot distinguish this path from other services on that host; no broad custom block added |

The reference above is a link for investigation, not an imported URL-rewrite
module. Never convert a path-specific rule into a whole-host rule without testing
the effect on normal app functionality. No device browsing logs are published.
