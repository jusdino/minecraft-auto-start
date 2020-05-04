locals {
  app_acronym = "mas"
  app_key = "${local.app_acronym}-${var.environment}"
  prod_non_prod = var.environment == "prod" ? "prod" : "non-prod"
}

resource "aws_key_pair" "front" {
  key_name = local.app_key
  public_key = var.public_key
}

data "terraform_remote_state" "mas_secrets" {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.aws_region
    key = "${local.prod_non_prod}/${var.aws_region}/${var.environment}/apps/${local.app_acronym}-secrets/terraform.tfstate"
  }
}

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.aws_region
    key = "${local.prod_non_prod}/${var.aws_region}/_global/vpc/terraform.tfstate"
  }
}

data "terraform_remote_state" "dns" {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.aws_region
    key = "${local.prod_non_prod}/${var.aws_region}/_global/dns/terraform.tfstate"
  }
}
