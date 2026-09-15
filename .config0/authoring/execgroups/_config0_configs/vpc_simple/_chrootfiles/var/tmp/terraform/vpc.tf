resource "aws_vpc" "main" {
  cidr_block           = "${var.base_cidr}.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  lifecycle {
    ignore_changes = [tags]
  }

  tags = merge(
    var.cloud_tags,
    var.vpc_tags,
    {
      Name    = var.vpc_name
      Product = "vpc"
    },
  )
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.main.id

  lifecycle {
    ignore_changes = [tags]
  }

  tags = merge(
    var.cloud_tags,
    var.vpc_tags,
    {
      Name    = "${var.vpc_name}-internet-gateway"
      Product = "internet-gateway"
    },
  )
}