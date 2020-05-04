variable "tfstate_global_bucket" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "environment" {
  type = string
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