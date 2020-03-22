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

data "terraform_remote_state" "mas_secrets" {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.tfstate_global_bucket_region
    key = "${var.aws_region}/${var.environment}/public/apps/${local.app_acronym}-secrets/terraform.tfstate"
  }
}

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.tfstate_global_bucket_region
    key = "${var.aws_region}/${var.environment}/public/vpc/terraform.tfstate"
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
