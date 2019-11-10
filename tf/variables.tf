variable "tfstate_global_bucket" {
  type = string
}

variable "tfstate_global_bucket_region" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "ssh_in_cidr_blocks" {
  type = list(string)
  description = "List of cidr blocks to allow ssh in from"
}

variable "tags" {
  type = map(string)
}