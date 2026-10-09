# CON-66 engine-timeout proof execgroup. No AWS resource at all: one
# hashicorp/time sleep whose apply outlives the order's timeout T, so an
# overrun at T leaves nothing in the cloud, only a tfstate.
terraform {
  required_version = ">= 1.1.0"

  required_providers {
    time = {
      source  = "hashicorp/time"
      version = "~> 0.12"
    }
  }
}

resource "time_sleep" "outlive_t" {
  create_duration = "400s"
}
