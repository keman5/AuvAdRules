# Sources and licensing

This repository publishes **supplemental rules only**, not a merged copy of
AdRules or HaGeZi Normal. Enable both baseline subscriptions independently:

- AdRules: https://adguardteam.github.io/HostlistsRegistry/assets/filter_29.txt
- HaGeZi Normal: https://adguardteam.github.io/HostlistsRegistry/assets/filter_34.txt

The generator downloads those exact lists only to remove already-covered custom
domains. Source URLs, hashes, plain domain counts and counts of other syntax are
recorded in `filters/manifest.json`; baseline contents are not in the output.
Exact and parent-domain matches of the same rule type are compared. Regex and
modifier-based coverage must be checked in the DNS engine before adding rules.

The scripts and custom additions are GPL-3.0; see `LICENSE`. Earlier commits
published a full HaGeZi Normal copy under its GPL-3.0 license; that historical
attribution remains applicable. HaGeZi's source acknowledgements are available
in [its README](https://github.com/hagezi/dns-blocklists/blob/main/README.md).

There are currently **no verified custom additions**. An empty supplement does
not replace the baseline lists and does not add splash-ad coverage.

## App-specific evidence

| App | Evidence | Acceptance status |
| --- | --- | --- |
| 闲鱼 | [Public path-rewrite reference](https://github.com/fmz200/wool_scripts/blob/main/Surge/module/split/partX/XianYu.sgmodule) targets `acs.m.goofish.com/gw/mtop.taobao.idlecommerce.splash.ads`; the same host also serves other app APIs | DNS cannot selectively block this path; not device-verified |
| 京东 | Baseline includes domains such as `ads-union.jd.com` and `addata.jd.com`; domain presence alone does not prove splash removal | Not device-verified |
| 爱思助手 | [Public URL-rewrite reference](https://github.com/fmz200/wool_scripts/blob/main/Surge/module/split/partA/AiSiAssistant.sgmodule) targets `list-app-m.i4.cn/getopfstadinfo.xhtml` | DNS cannot distinguish this path from other services on that host; no broad custom block added |

The reference above is a link for investigation, not an imported URL-rewrite
module. Never convert a path-specific rule into a whole-host rule without testing
the effect on normal app functionality. No device browsing logs are published.
