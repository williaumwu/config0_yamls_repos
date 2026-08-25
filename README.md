# config0_yamls_repos
## Parallel tracks

Each track has its own `purpose` label and its own resource names, so tracks can run at the same
time without their selectors matching each other's records.

| Track | purpose label | Run order |
|---|---|---|
| `rds-track/` | `eval-rds` | `vpc` -> `rds` |
| `eks-track/` | `eval-eks` | `vpc` -> `eks` |
| `multistack-track/` | `eval-multistack` | single run |
| `vpc-track/` | `eval-vpc` | single run, runs in parallel with the other tracks |
| `envsql-track/` | `eval-envsql` | single run (`env_name: evalsql`, kept distinct from `platform/env-sql`) |
| `envnosql-track/` | `eval-envnosql` | single run (`env_name: evalnosql`, MongoDB replica + EKS, story 09) |
| `platform/` | `eval-config0` | one sequential track: `vpc` -> `network-vars-set` -> `nat` -> `rds` -> `eks` |
| `platform/env-sql/` | `eval-config0` | single run, story 105, passing as of 2026-08-20 |
