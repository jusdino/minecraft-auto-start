locals {
  app_acronym = "mas"
  app_key = "${local.app_acronym}-${var.environment}"
  prod_non_prod = var.environment == "prod" ? "prod" : "non-prod"
}

data terraform_remote_state mas_secrets {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.aws_region
    key = "${local.prod_non_prod}/${var.aws_region}/${var.environment}/apps/${local.app_acronym}-secrets/terraform.tfstate"
  }
}

data terraform_remote_state vpc {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.aws_region
    key = "${local.prod_non_prod}/${var.aws_region}/_global/vpc/terraform.tfstate"
  }
}

resource aws_dynamodb_table servers {
  name = "${local.app_key}-servers"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "hostname"
  attribute {
    name = "hostname"
    type = "S"
  }
  server_side_encryption {
    enabled = true
    kms_key_arn = data.terraform_remote_state.mas_secrets.outputs.kms_key_arn
  }
}
