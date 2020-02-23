resource "aws_ecs_task_definition" "launcher" {
  family = "launcher"
  container_definitions = templatefile("${path.module}/task-definitions/launcher.json.tpl", {
      "known_hosts_parameter": aws_ssm_parameter.known_hosts.arn,
      "ssh_agent_key_parameter": aws_ssm_parameter.ssh_key.arn,
      "infra_live_clone_url_parameter": aws_ssm_parameter.clone_url.arn,
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

resource "aws_ssm_parameter" "known_hosts" {
  name = "/${local.app_key}/known-hosts"
  type = "SecureString"
  key_id = aws_kms_key.main.key_id
  value = var.known_hosts
  overwrite = true
}

resource "aws_ssm_parameter" "clone_url" {
  name = "/${local.app_key}/clone_url"
  type = "SecureString"
  key_id = aws_kms_key.main.key_id
  value = var.infra_live_clone_url
  overwrite = true
}

resource "aws_ssm_parameter" "ssh_key" {
  name = "/${local.app_key}/sh-key"
  type = "SecureString"
  key_id = aws_kms_key.main.key_id
  value = "NotInTfState"
  overwrite = true
}

resource "aws_iam_role" "launcher_execution" {
  path = "/${local.app_key}/"
  name = "launcher-execution"
  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_policy" "launcher_execution" {
  name = "${local.app_key}-launcher-execution"
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowGetParameters",
      "Effect": "Allow",
      "Action": "ssm:GetParameters",
      "Resource": [
        "arn:aws:ssm:*:*:parameter/${local.app_key}/*"
      ]
    },
    {
      "Sid": "AllowGetKMS",
      "Effect": "Allow",
      "Action": [
        "kms:ListKeys",
        "kms:ListAliases",
        "kms:Describe*",
        "kms:Decrypt"
      ],
      "Resource": "${aws_kms_key.main.arn}"
    },
    {
      "Sid": "AllowLogging",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "launcher_execution" {
  role = aws_iam_role.launcher_execution.name
  policy_arn = aws_iam_policy.launcher_execution.arn
}

resource "aws_iam_role" "launcher_task" {
  path = "/${local.app_key}/"
  name = "launcher-task"
  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

// Lock this down if you are not insane
resource "aws_iam_policy" "launcher_task" {
  name = "${local.app_key}-launcher-task"
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GodMode",
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "launcher_task" {
  role = aws_iam_role.launcher_task.name
  policy_arn = aws_iam_policy.launcher_task.arn
}
