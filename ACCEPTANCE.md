# Initial rule publication verification — 2026-10-29

These results verify the published DNS list, not removal of every advertisement
in any specific app or routing on a user's home network.

| Check | Result |
| --- | --- |
| Python update regression suite | 5 tests passed: shared syntax, rejected unsupported/type-specific rules, count-change guard, failed-update preservation, stable output on unchanged rules |
| Public subscription retrieval | HTTP success, SHA-256 matches initial local output |
| First GitHub Actions execution | `test` and `update` both succeeded: [run](https://github.com/keman5/AuvAdRules/actions/runs/40794556869) |
| AdGuard Home v0.107.79 actual engine | Loaded 172,000 rules and enabled filtering in an isolated local instance |
| DNS over IPv4 loopback, `ads-union.jd.com` A / AAAA | `0.0.0.0` / `::` |
| DNS over IPv6 loopback, `ads-union.jd.com` A / AAAA | `0.0.0.0` / `::` |
| Normal domain control, `example.com` AAAA | Public IPv6 addresses returned; IPv6 was not globally disabled |
| iOS client loading this published URL | Pending device verification |
| Home DHCPv4 / IPv6 RA and all LAN devices | Pending deployment and per-device verification |
| 闲鱼 / 京东 / 爱思助手 cold-start ads and normal functionality | Pending device verification; known path-specific cases exceed DNS-only capability |

Official Home release used for this isolated test:
`https://github.com/AdguardTeam/AdGuardHome/releases/download/v0.107.79/AdGuardHome_darwin_arm64.zip`
with verified GitHub release SHA-256
`916f50bcc16b452c63ab8289f523a3c637e84933460a0ae7525fec03e31de867`.
The temporary instance listened only on loopback and was stopped after the test;
no system DNS setting was changed.

Initial published filter SHA-256:
`9a51d158b87d9889928dda64446505158c95ef51851d25c090c0d1562e8e395f`.
Future updates may change it; consult `filters/manifest.json` and Git history.
