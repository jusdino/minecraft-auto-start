resource aws_ssm_parameter launcher_network_config {
  name = "${local.app_key}-launcher-network-config"
  type = "String"
  value = jsonencode({
    "awsvpcConfiguration" = {
      "subnets" = data.terraform_remote_state.vpc.outputs.subnet_ids,
      "securityGroups" = [aws_security_group.launcher.id],
      "assignPublicIp" = "ENABLED"
    }
  })
}

resource aws_dynamodb_table auth {
  name = "${local.app_key}-auth"
  billing_mode = "PAY_PER_REQUEST"
  hash_key = "email"
  attribute {
    name = "email"
    type = "S"
  }
  server_side_encryption {
    enabled = true
    kms_key_arn = data.terraform_remote_state.mas_secrets.outputs.kms_key_arn
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
