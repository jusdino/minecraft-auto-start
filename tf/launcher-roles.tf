resource aws_iam_role launcher_execution {
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

resource aws_iam_policy launcher_execution {
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
      "Resource": "${data.terraform_remote_state.mas_secrets.outputs.kms_key_arn}"
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

resource aws_iam_role_policy_attachment launcher_execution {
  role = aws_iam_role.launcher_execution.name
  policy_arn = aws_iam_policy.launcher_execution.arn
}

resource aws_iam_role launcher_task {
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
resource aws_iam_policy launcher_task {
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

resource aws_iam_role_policy_attachment launcher_task {
  role = aws_iam_role.launcher_task.name
  policy_arn = aws_iam_policy.launcher_task.arn
}
