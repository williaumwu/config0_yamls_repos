# Declared only so the tfvars config0_publisher writes carry no undeclared keys.
variable "aws_default_region" {
  type    = string
  default = "ap-northeast-1"
}

variable "cloud_tags" {
  type    = map(string)
  default = {}
}
