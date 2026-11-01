# Supplement publication verification — 2026-11-01

The subscription is now a supplement, not a full baseline copy. Earlier full-list
DNS checks do not prove any custom addition or app splash-ad removal.

| Check | Result |
| --- | --- |
| Generator regressions | 7 tests passed: priority preservation, strict syntax, unsupported syntax rejection, baseline count guard, failed-update preservation, exact/parent coverage, migration to empty output and stable output |
| Input baselines | AdRules filter_29 and HaGeZi Normal filter_34; downloaded only for comparison |
| Verified custom additions | 0 |
| Locally generated blocking rules | 34 user-supplied rules, preserving `$important`; source and generated rule sets match |
| Device splash-ad removal | Not verified; DNS cannot distinguish paths on a shared host |

Baseline rules must remain separately enabled on Home and clients. Automatic
comparison covers domain rules and parent domains of the same rule type and
priority; regex and other modifiers require an actual engine check when reviewing additions.
`filters/manifest.json` records source and output hashes. Failed baseline fetches
or invalid input leave the previous publication unchanged.
