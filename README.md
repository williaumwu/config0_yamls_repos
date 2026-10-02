# config0_yamls_repos
## Region prerequisites

Run `server-config/config0.yaml` ONCE per region, right after onboarding, before any track
that configures a server. It installs the region's EC2 key pair and the EventBridge SSM
executor, replacing the legacy bastion host. It is never a substack of an environment stack.

Its records carry these labels, which is how the consuming stacks find them:

```yaml
labels:
  general:
    purpose: server-configuration
    managed_by: config0
  infrastructure:
    cloud: aws
    area: server-config
    product: ssm-ec2-exec   # ssh-key-pair on the key pair stack
    region: ap-northeast-1
```

No environment label - these are region-scoped, not environment-scoped.

`ssm-host-docker/` (story 07) installs the same two stacks under its own
`purpose: ssm-host-docker`; that story is the install test, not the production install.

Every host-order stack must pass `install_name` matching the install record it depends on,
because discovery raises when two installs exist in one region.

| Install | Folder | Region | Install name | Stories that read it |
|---|---|---|---|---|
| region prerequisite (ap-northeast-1) | `server-config/` | `ap-northeast-1` | `server-config` | 07, 08, 09, `ec2-public-ssh/`, `ec2-windows/`, `rds-iam/` |
| region prerequisite (eu-west-1) | `server-config-euw1/` | `eu-west-1` | `server-euw1` | 109 |

Story 07 is the install test and uses its own `install_name: story07`, not either row above.
Stories 07, 08 and 09 run in `ap-northeast-1`, so they need the `server-config` install.
Story 109 runs through the platform, which pins `aws_default_region: eu-west-1`, so it needs
the `server-euw1` install (from `server-config-euw1/`) instead.

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
| `envnosql-track/` | `eval-envnosql` | single run (`env_name: evalnosql`, MongoDB replica + EKS, story 09). Needs `server-config` in the region. |
| `platform/` | `eval-config0` | one sequential track: `vpc` -> `network-vars-set` -> `nat` -> `rds` -> `eks` |
| `platform/env-sql/` | `eval-config0-env` | single run, story 105, passing as of 2026-08-20. Self-contained: brings its own network substack, depends on none of 102-104. |
| `platform/env-nosql/` | `eval-config0-nosql` | single run, story 109 (`env_name: nosql`), never run. Self-contained the same way in its own purpose namespace, so a live 105 never satisfies its checks; depends on none of 102-105. Needs the `server-euw1` install (`server-config-euw1/`) in the platform's region (eu-west-1). |
| `ec2-public-ssh/` | `ec2-public-ssh` | single run, CON-11 `ec2` kind `ssh` level target: public Ubuntu host with a scenario `aws_sg` (bastion group, 22 open). Reuses the `ssm-host-docker/` VPC; needs `server-config`. |
| `ec2-windows/` | `ec2-windows` | single run, CON-11 `ec2_windows` kind target: private Windows Server 2022 host, SSM-managed. Reuses the `ssm-host-docker/` VPC; needs `server-config`. |
| `rds-iam/` | `rds-iam` | single run, CON-11 `rds` kind target: own VPC -> MySQL RDS with IAM database authentication -> host `rds-iam-host-01` in the same VPC. Needs `server-config` and the `aws_storage` publish that adds `iam_database_authentication_enabled` to `aws_rds`. |
| `ecs/` | `ecs` | single run, CON-11 `ecs` kind target: own VPC -> ECS cluster `eval-config0-ecs` with one nginx Fargate service `web`, ECS Exec on, no public IP. Needs the `aws` publish that adds the `aws_ecs_service` stack. |

## Regions

AWS allows 5 VPCs per region by default, so the parallel tracks are spread across four
regions rather than piled into one. Each region below stays at 3 VPCs or fewer.

| Region | Tracks | VPCs created |
|---|---|---|
| `ap-northeast-1` | `server-config/` (0), `ssm-host-docker/` (1), `mongodb/` (0), `workspace-isolation/` + `workspace-two-calls/` (0), `envnosql-track/` (1, via env_nosql's network substack), `ec2-public-ssh/` (0), `ec2-windows/` (0), `rds-iam/` (1), `ecs/` (1) | 4 |
| `ap-southeast-1` | `vpc-track/` (1), `rds-track/` (1), `eks-track/` (1) | 3 |
| `eu-west-1` | `server-config-euw1/` (0), `platform/` (1), `platform/env-sql/` (1), `platform/env-nosql/` (1) | 3 |
| `us-west-2` | `multistack-track/` (1), `envsql-track/` (1), `ssm-ec2-exec-eventbridge-longbuild/` (1) | 3 |

`platform/` pins `aws_default_region: eu-west-1` in its own stack, so the platform stories
stay in eu-west-1 and read the `server-euw1` install.
