# AWS VPC Module

This OpenTofu module creates a fully configured AWS VPC with public and private subnets across multiple availability zones. The module also includes internet gateways, route tables, and VPC endpoints for S3 and DynamoDB services.

## Features

- Creates a VPC with customizable CIDR block (default: 10.10.0.0/16)
- Provisions public and private subnets in two availability zones
- Sets up internet gateway for public subnet access
- Configures route tables for public and private subnets
- Creates VPC endpoints for S3 and DynamoDB services
- Applies customizable tags to all resources

## Requirements

- OpenTofu >= 1.8.8
- AWS provider

## Usage

```hcl
module "vpc" {
  source = "./path/to/module"

  vpc_name          = "my-application-vpc"
  aws_default_region = "us-west-2"
  
  cloud_tags = {
    Environment = "Production"
    Owner       = "DevOps Team"
  }
}
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| aws_default_region | The AWS region where resources will be created | string | "us-east-1" | no |
| vpc_name | The name of the VPC | string | "default_vpc_name_config0" | no |
| vpc_tags | Additional tags to apply to VPC resources | map(string) | {} | no |
| public_subnet_tags | Additional tags to apply to public subnets | map(string) | {"kubernetes.io/role/elb": "1"} | no |
| private_subnet_tags | Additional tags to apply to private subnets | map(string) | {"kubernetes.io/role/internal_elb": "1"} | no |
| cloud_tags | Global tags to apply to all resources | map(string) | {} | no |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | The ID of the VPC |
| vpc_name | The name of the VPC |
| id | The ID of the VPC (duplicate of vpc_id) |
| name | The name of the VPC (duplicate of vpc_name) |
| vpc | The name of the VPC (duplicate of vpc_name) |
| public_route_table_id | The ID of the public route table |
| private_route_table_id | The ID of the private route table |
| public_subnet_ids | Comma-separated list of public subnet IDs |
| private_subnet_ids | Comma-separated list of private subnet IDs |

## VPC Configuration

The VPC is configured with the following CIDR blocks:

- VPC CIDR: 10.10.0.0/16
- Public Subnets:
  - AZ a: 10.10.101.0/24
  - AZ b: 10.10.102.0/24
- Private Subnets:
  - AZ a: 10.10.201.0/24
  - AZ b: 10.10.202.0/24

## License

Copyright (C) 2025 Gary Leong <gary@config0.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.