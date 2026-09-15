output "vpc_id" {
  description = "The ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_name" {
  description = "The name of the VPC"
  value       = aws_vpc.main.tags.Name
}

output "vpc" {
  description = "The name of the VPC (duplicate of vpc_name)"
  value       = aws_vpc.main.tags.Name
}

output "id" {
  description = "The ID of the VPC (duplicate of vpc_id)"
  value       = aws_vpc.main.id
}

output "name" {
  description = "The name of the VPC (duplicate of vpc_name)"
  value       = aws_vpc.main.tags.Name
}

output "public_route_table_id" {
  description = "The ID of the public route table"
  value       = aws_default_route_table.public.id
}

output "private_route_table_id" {
  description = "The ID of the private route table"
  value       = aws_route_table.private.id
}

output "public_subnet_ids" {
  description = "Comma-separated list of public subnet IDs"
  value       = join(",", [for subnet in aws_subnet.public : subnet.id])
}

output "private_subnet_ids" {
  description = "Comma-separated list of private subnet IDs"
  value       = join(",", [for subnet in aws_subnet.private : subnet.id])
}

# Additional helpful outputs
output "public_subnets" {
  description = "Map of public subnet details"
  value = {
    for az, subnet in aws_subnet.public : az => {
      id   = subnet.id
      cidr = subnet.cidr_block
      az   = subnet.availability_zone
    }
  }
}

output "private_subnets" {
  description = "Map of private subnet details"
  value = {
    for az, subnet in aws_subnet.private : az => {
      id   = subnet.id
      cidr = subnet.cidr_block
      az   = subnet.availability_zone
    }
  }
}

output "availability_zones" {
  description = "List of availability zones used"
  value       = local.azs
}