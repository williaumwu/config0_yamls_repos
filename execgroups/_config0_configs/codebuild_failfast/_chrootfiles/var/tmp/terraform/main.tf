# CodeBuild fail-fast integration execgroup. No AWS resource at all: a
# precondition that is always false makes `plan` fail in the first seconds
# of the CodeBuild build, so the order fails within about a minute of the
# fire, long before its timeout T. Destroy of the empty state succeeds.
terraform {
  required_version = ">= 1.1.0"
}

resource "terraform_data" "failfast" {
  lifecycle {
    precondition {
      condition     = false
      error_message = "codebuild-failfast: deliberate plan failure"
    }
  }
}
