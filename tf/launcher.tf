resource "aws_ecs_task_definition" "launcher" {
  family = "launcher"
  container_definitions = templatefile("${path.module}/task-definitions/launcher.json.tpl", {
      "known_hosts_parameter": data.terraform_remote_state.mas_secrets.outputs.known_hosts_parameter_arn,
      "ssh_agent_key_parameter": data.terraform_remote_state.mas_secrets.outputs.ssh_key_parameter_arn,
      "infra_live_clone_url_parameter": data.terraform_remote_state.mas_secrets.outputs.clone_url_parameter_arn,
      "log_group_name": aws_cloudwatch_log_group.launcher.name,
      "region": var.aws_region
    }
  )
  requires_compatibilities = ["FARGATE"]
  cpu = 1024
  memory = 2048
  network_mode = "awsvpc"
  execution_role_arn = aws_iam_role.launcher_execution.arn
  task_role_arn = aws_iam_role.launcher_task.arn
  tags = merge({Name = "launcher"}, var.tags)
}

resource "aws_security_group" "launcher" {
  name = "${local.app_key}-launcher"
  description = "${local.app_key}-launcher"
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id

  egress {
    from_port = 0
    to_port = 65535
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port = 0
    to_port = 65535
    protocol = "udp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge({Name = "launcher"}, var.tags)
}

resource "aws_cloudwatch_log_group" "launcher" {
  name = "/ecs/${local.app_key}-launcher"
  retention_in_days = 7
  tags = merge({Name = "launcher"}, var.tags)
}
