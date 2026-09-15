# AWS VPC with Security Groups

## Description
This stack creates an AWS Virtual Private Cloud (VPC) with appropriate security groups. It supports optional EKS cluster configuration by adding the necessary tags to the VPC and subnets.

## Variables

### Required Variables

| Name | Description | Default |
|------|-------------|---------|
| vpc_name | VPC network name | &nbsp; |

### Optional Variables

| Name | Description | Default |
|------|-------------|---------|
| tier_level | Configuration for tier level | &nbsp; |
| vpc_id | VPC network identifier | null |
| eks_cluster | EKS cluster name | &nbsp; |
| aws_default_region | Default AWS region | eu-west-1 |

## Dependencies

### Substacks
- [config0-hub:::config0_core::tf_executor](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/tf_executor)
- [config0-hub:::aws_networking::aws_sg](https://api-app.config0.com/web_api/v1.0/stacks/config0-hub/aws_sg)

### Execgroups
- [config0-hub:::aws_networking::vpc_simple](https://api-app.config0.com/web_api/v1.0/exec/groups/config0-hub/aws_networking/vpc_simple)

### Scripts
None

## License
<pre>
Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.
</pre>