# Sources and licensing

This repository publishes **supplemental rules only**, not a merged copy of
AdRules or HaGeZi Normal. Enable both baseline subscriptions independently:

- AdRules: https://adguardteam.github.io/HostlistsRegistry/assets/filter_29.txt
- HaGeZi Normal: https://adguardteam.github.io/HostlistsRegistry/assets/filter_34.txt

The generator downloads those exact lists only to remove already-covered custom
domains. Source URLs, hashes, supported domain rule counts and counts of other syntax are
recorded in `filters/manifest.json`; baseline contents are not in the output.
Exact and parent-domain matches of the same rule type and priority are compared.
Only the optional $important modifier is supported; other modifiers and regex
require DNS engine review.

The scripts and custom additions are GPL-3.0; see `LICENSE`. Earlier commits
published a full HaGeZi Normal copy under its GPL-3.0 license; that historical
attribution remains applicable. HaGeZi's source acknowledgements are available
in [its README](https://github.com/hagezi/dns-blocklists/blob/main/README.md).

On 2026-11-01, the user supplied `dns_blocklist.txt`: 34 unique domain rules, all
with `$important`. They are retained in `rules/custom.txt` without changing their
priority. Source SHA-256: `9dcf450adc2a8a041c2723f7b0d7e0c56bfe7ee173110541ef2fd0befdae6cd0`.
These are user-supplied blocks, not independently verified ad-only domains.
They include broad business domains such as `pinduoduo.com`, `api.weibo.com`,
and `adtidy.org`; normal app/service functionality may be affected.
The supplement does not replace the baseline lists.

## App-specific evidence

| App | Evidence | Acceptance status |
| --- | --- | --- |
| 闲鱼 | [Public path-rewrite reference](https://github.com/fmz200/wool_scripts/blob/main/Surge/module/split/partX/XianYu.sgmodule) targets `acs.m.goofish.com/gw/mtop.taobao.idlecommerce.splash.ads`; the same host also serves other app APIs | DNS cannot selectively block this path; not device-verified |
| 京东 | Baseline includes domains such as `ads-union.jd.com` and `addata.jd.com`; domain presence alone does not prove splash removal | Not device-verified |
| 爱思助手 | [Public URL-rewrite reference](https://github.com/fmz200/wool_scripts/blob/main/Surge/module/split/partA/AiSiAssistant.sgmodule) targets `list-app-m.i4.cn/getopfstadinfo.xhtml` | DNS cannot distinguish this path from other services on that host; no broad custom block added |

The reference above is a link for investigation, not an imported URL-rewrite
module. Never convert a path-specific rule into a whole-host rule without testing
the effect on normal app functionality. No device browsing logs are published.
