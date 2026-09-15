# Routing
resource "aws_default_route_table" "public" {
  default_route_table_id = aws_vpc.main.main_route_table_id

  lifecycle {
    ignore_changes = [tags]
  }

  tags = merge(
    var.cloud_tags,
    var.vpc_tags,
    {
      Name    = "${var.vpc_name}-route-public"
      Product = "route-table"
    },
  )
}

resource "aws_route" "public_internet_gateway" {
  route_table_id         = aws_default_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.this.id

  timeouts {
    create = "5m"
  }
}

resource "aws_route_table_association" "public" {
  for_each       = local.public_subnets
  subnet_id      = aws_subnet.public[each.key].id
  route_table_id = aws_default_route_table.public.id
}

resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  lifecycle {
    ignore_changes = [tags]
  }

  tags = merge(
    var.cloud_tags,
    var.vpc_tags,
    {
      Name    = "${var.vpc_name}-route-private"
      Product = "route-table"
    },
  )
}

resource "aws_route_table_association" "private" {
  for_each       = local.private_subnets
  subnet_id      = aws_subnet.private[each.key].id
  route_table_id = aws_route_table.private.id
}

# NAT Gateway (opt-in via enable_nat_gateway, default false)
# Only where the user package needs public package repositories from a
# private subnet - one NAT in the first public subnet, egress default
# route added to the private route table.
resource "aws_eip" "nat" {
  count      = var.enable_nat_gateway ? 1 : 0
  domain     = "vpc"
  depends_on = [aws_internet_gateway.this]

  tags = merge(
    var.cloud_tags,
    var.vpc_tags,
    {
      Name    = "${var.vpc_name}-nat-eip"
      Product = "eip"
    },
  )
}

resource "aws_nat_gateway" "this" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[local.azs[0]].id
  depends_on    = [aws_internet_gateway.this]

  tags = merge(
    var.cloud_tags,
    var.vpc_tags,
    {
      Name    = "${var.vpc_name}-nat-gateway"
      Product = "nat-gateway"
    },
  )
}

resource "aws_route" "private_nat_gateway" {
  count                  = var.enable_nat_gateway ? 1 : 0
  route_table_id         = aws_route_table.private.id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.this[0].id

  timeouts {
    create = "5m"
  }
}