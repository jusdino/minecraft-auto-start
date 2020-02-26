provider "aws" {
  region = var.aws_region
}

terraform {
  backend "s3" {}
}

locals {
  app_acronym = "mas"
  app_key = "${local.app_acronym}-${var.environment}"
}

resource "aws_key_pair" "front" {
  key_name = "front"
  public_key = var.public_key
}

resource "aws_kms_key" "main" {
  description = local.app_key
  deletion_window_in_days = 7
}

resource "aws_kms_alias" "main" {
  name = "alias/${local.app_key}"
  target_key_id = aws_kms_key.main.key_id
}

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.tfstate_global_bucket_region
    key = "us-west-1/dev/public/vpc/terraform.tfstate"
  }
}

data "terraform_remote_state" "dns" {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.tfstate_global_bucket_region
    key = "_global/dns/terraform.tfstate"
  }
}
