data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  # Base CIDR block
  base_cidr = var.base_cidr # e.g., "10.11"

  # Number of subnets to create for each type (public and private)
  num_of_subnets = var.num_of_subnets # e.g., 2

  # Get available AZs based on region
  azs = slice(data.aws_availability_zones.available.names, 0, local.num_of_subnets)

  # Create public subnets dynamically
  public_subnets = {
    for i, az in local.azs :
    az => "${local.base_cidr}.${100 + i + 1}.0/24"
  }

  # Create private subnets dynamically
  private_subnets = {
    for i, az in local.azs :
    az => "${local.base_cidr}.${200 + i + 1}.0/24"
  }
}
