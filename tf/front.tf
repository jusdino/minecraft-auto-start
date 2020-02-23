resource "aws_ecs_task_definition" "front" {
  family = "front"
  container_definitions = templatefile("${path.module}/task-definitions/front.json.tpl", {
      "auth_table_name": aws_dynamodb_table.auth.name,
      "servers_table_name": aws_dynamodb_table.servers.name,
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
  desired_count = 1
  launch_type = "EC2"
//  propagate_tags = "SERVICE"
//  tags = merge({Name = "front"}, var.tags)
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
    kms_key_arn = aws_kms_key.main.arn
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
    kms_key_arn = aws_kms_key.main.arn
  }
}
