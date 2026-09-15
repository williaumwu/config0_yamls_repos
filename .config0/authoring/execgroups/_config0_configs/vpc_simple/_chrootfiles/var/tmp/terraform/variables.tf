variable "aws_default_region" {
  type        = string
  description = "The AWS region where resources will be created"
  default     = "us-east-1"
}

variable "vpc_name" {
  type        = string
  description = "The name of the VPC"
  default     = "default_vpc_name_config0"
}

variable "vpc_tags" {
  type        = map(string)
  description = "Additional tags to apply to VPC resources"
  default     = {}
}

variable "public_subnet_tags" {
  type        = map(string)
  description = "Additional tags to apply to public subnets"
  default     = { "kubernetes.io/role/elb" : "1" }
}

variable "private_subnet_tags" {
  type        = map(string)
  description = "Additional tags to apply to private subnets"
  default     = { "kubernetes.io/role/internal_elb" : "1" }
}

variable "cloud_tags" {
  type        = map(string)
  description = "Global tags to apply to all resources"
  default     = {}
}

variable "base_cidr" {
  type        = string
  description = "The base cidr for subnets"
  default     = "10.11"
}

variable "num_of_subnets" {
  type        = number
  description = "The number of subnets"
  default     = 2
}

variable "enable_ssm_endpoints" {
  type        = bool
  description = "Opt-in: create ssm/ssmmessages/ec2messages interface endpoints for no-public-IP SSM-managed hosts"
  default     = false
}

variable "enable_nat_gateway" {
  type        = bool
  description = "Opt-in: create a NAT gateway (with EIP) in the first public subnet and route private-subnet egress through it, for hosts that need public package repositories"
  default     = false
}



