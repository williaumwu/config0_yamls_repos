resource "aws_subnet" "public" {
  for_each                = local.public_subnets
  cidr_block              = each.value
  vpc_id                  = aws_vpc.main.id
  map_public_ip_on_launch = true
  availability_zone       = each.key

  lifecycle {
    ignore_changes = [tags]
  }

  tags = merge(
    var.cloud_tags,
    var.vpc_tags,
    var.public_subnet_tags,
    {
      Name               = "${var.vpc_name}-service-public-${substr(each.key, -1, 1)}"
      subnet_environment = "public"
    },
  )
}

resource "aws_subnet" "private" {
  for_each                = local.private_subnets
  cidr_block              = each.value
  vpc_id                  = aws_vpc.main.id
  map_public_ip_on_launch = false # Changed to false since these are private subnets
  availability_zone       = each.key

  lifecycle {
    ignore_changes = [tags]
  }

  tags = merge(
    var.cloud_tags,
    var.vpc_tags,
    var.private_subnet_tags,
    {
      Name               = "${var.vpc_name}-service-private-${substr(each.key, -1, 1)}"
      subnet_environment = "private"
    },
  )
}