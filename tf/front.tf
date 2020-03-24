resource "aws_ecs_task_definition" "front" {
  family = "front"
  container_definitions = templatefile("${path.module}/task-definitions/front.json.tpl", {
      "auth_table_name": aws_dynamodb_table.auth.name,
      "servers_table_name": aws_dynamodb_table.servers.name,
      "server_domain": data.terraform_remote_state.dns.outputs.hosted_zone_domain,
      "launcher_task_arn": aws_ecs_task_definition.launcher.arn,
      "launcher_network_config_parameter": aws_ssm_parameter.launcher_network_config.arn,
      "ssl_cert_parameter": data.terraform_remote_state.mas_secrets.outputs.ssl_cert_parameter_arn,
      "ssl_key_parameter": data.terraform_remote_state.mas_secrets.outputs.ssl_key_parameter_arn
      "cluster_arn": aws_ecs_cluster.front.arn,
      "aws_region": var.aws_region
    }
  )
  execution_role_arn = aws_iam_role.front_execution.arn
  task_role_arn = aws_iam_role.front_task.arn
  tags = merge({Name = "front"}, var.tags)
}

resource "aws_ecs_service" "front" {
  name = "front"
  cluster = aws_ecs_cluster.front.id
  task_definition = aws_ecs_task_definition.front.arn
  desired_count = var.front_instance_count
  launch_type = "EC2"
//  propagate_tags = "SERVICE"
//  tags = merge({Name = "front"}, var.tags)
}

resource "aws_ssm_parameter" "launcher_network_config" {
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

resource "aws_dynamodb_table" "auth" {
  name = "${local.app_key}-auth_"
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

resource "aws_dynamodb_table" "servers" {
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
