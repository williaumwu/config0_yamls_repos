# Gateway Endpoints
resource "aws_vpc_endpoint" "s3" {
  depends_on      = [aws_vpc.main]
  vpc_id          = aws_vpc.main.id
  service_name    = "com.amazonaws.${var.aws_default_region}.s3"
  route_table_ids = [aws_route_table.private.id, aws_default_route_table.public.id]

  tags = merge(
    var.cloud_tags,
    {
      Product = "vpc_endpoint"
      Name    = "s3-gw-endpt-${var.vpc_name}"
    },
  )
}

resource "aws_vpc_endpoint" "dynamodb" {
  depends_on      = [aws_vpc.main]
  vpc_id          = aws_vpc.main.id
  service_name    = "com.amazonaws.${var.aws_default_region}.dynamodb"
  route_table_ids = [aws_route_table.private.id, aws_default_route_table.public.id]

  tags = merge(
    var.cloud_tags,
    {
      Product = "vpc_endpoint"
      Name    = "dynamodb-gw-endpt-${var.vpc_name}"
    },
  )
}

# SSM Interface Endpoints (opt-in via enable_ssm_endpoints, default false)
# Required for SSM SendCommand against no-public-IP hosts: without
# ssm/ssmmessages/ec2messages interface endpoints the agent on a private
# server never reaches the SSM service.
resource "aws_security_group" "ssm_endpoints" {
  count       = var.enable_ssm_endpoints ? 1 : 0
  name        = "ssm-endpoints-${var.vpc_name}"
  description = "Allow HTTPS from the VPC to the SSM interface endpoints"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTPS from the VPC"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.main.cidr_block]
  }

  tags = merge(
    var.cloud_tags,
    {
      Product = "security_group"
      Name    = "ssm-endpoints-${var.vpc_name}"
    },
  )
}

resource "aws_vpc_endpoint" "ssm_interface" {
  for_each = var.enable_ssm_endpoints ? toset(["ssm", "ssmmessages", "ec2messages"]) : toset([])

  depends_on          = [aws_vpc.main]
  vpc_id              = aws_vpc.main.id
  service_name        = "com.amazonaws.${var.aws_default_region}.${each.key}"
  vpc_endpoint_type   = "Interface"
  private_dns_enabled = true
  subnet_ids          = [for subnet in aws_subnet.private : subnet.id]
  security_group_ids  = [aws_security_group.ssm_endpoints[0].id]

  tags = merge(
    var.cloud_tags,
    {
      Product = "vpc_endpoint"
      Name    = "${each.key}-if-endpt-${var.vpc_name}"
    },
  )
}

