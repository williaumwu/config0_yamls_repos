# Per-account fixture copies

Some top-level scenarios bake the T1 account id 570017720022 into bucket names, labels
or ids. A parallel track that runs one of those scenarios on its own account uses the
copy here instead.

`accounts/<account id>/<scenario>/config0.yaml` mirrors `<scenario>/config0.yaml` with
570017720022 replaced by `<account id>`, and nothing else changed. In
`484888470684/vpc-peering/`, the second account 604227045267 is also replaced by
530751148851 (T3's second account). The top-level originals stay the T1 fixtures.

`TRACK_FIXTURE_PREFIX` in the code repo's `user-stories/tracks/T<n>.env` selects a
folder: empty for T1 (the top-level scenarios), `accounts/<account id>` for the others.

| Folder | Track | Scenarios |
|---|---|---|
| `402909940697/` | T2 | `server-config`, `server-config-euw1`, `ssm-host-docker` |
| `484888470684/` | T3 | `vpc-peering` |
| `360260271775/` | T4 | `server-config`, `ssm-host-docker` |
