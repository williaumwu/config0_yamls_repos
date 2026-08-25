# config0_yamls_repos
## Parallel tracks

Each track has its own `purpose` label and its own resource names, so tracks can run at the same
time without their selectors matching each other's records.

| Track | purpose label | Run order |
|---|---|---|
| `rds-track/` | `eval-rds` | `vpc` -> `rds` |
| `eks-track/` | `eval-eks` | `vpc` -> `eks` |
| `multistack-track/` | `eval-multistack` | single run |
| `envsql-track/` | `eval-envsql` | single run |
| `platform/` | `eval-config0` | one sequential track: `vpc` -> `network-vars-set` -> `nat` -> `rds` -> `eks` |
