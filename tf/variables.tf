variable "tfstate_global_bucket" {
  type = string
}

variable "tfstate_global_bucket_region" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "environment" {
  type = string
}

variable "front_instance_count" {
  type = string
  default = 1
}

variable "ssh_in_cidr_blocks" {
  type = list(string)
  description = "List of cidr blocks to allow ssh in from"
}

variable "public_key" {
  type = string
  description = "Public key for asg instances"
}

variable "tags" {
  type = map(string)
}

variable "known_hosts" {
  type = string
  description = "SSH known hosts to add to launcher ECS task"
}

variable "infra_live_clone_url" {
  type = string
  description = "URL to clone infrastructure live from"
}