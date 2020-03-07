resource "aws_iam_role" "front_execution" {
  path = "/${local.app_key}/"
  name = "front-execution"
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

resource "aws_iam_policy" "front_execution" {
  name = "${local.app_key}-front-execution"
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowLogging",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AllowGetParameters",
      "Effect": "Allow",
      "Action": "ssm:GetParameters",
      "Resource": [
        "${aws_ssm_parameter.launcher_network_config.arn}"
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
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "front_execution" {
  role = aws_iam_role.front_execution.name
  policy_arn = aws_iam_policy.front_execution.arn
}

resource "aws_iam_role" "front_task" {
  path = "/${local.app_key}/"
  name = "front-task"
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

resource "aws_iam_policy" "front_task" {
  name = "${local.app_key}-front-task"
  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
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
      "Sid": "AllowDBReadWrite",
      "Effect": "Allow",
      "Action": [
        "dynamodb:BatchGetItem",
        "dynamodb:BatchWriteItem",
        "dynamodb:ConditionCheck",
        "dynamodb:DeleteItem",
        "dynamodb:DescribeLimits",
        "dynamodb:DescribeReservedCapacity",
        "dynamodb:DescribeReservedCapacityOfferings",
        "dynamodb:DescribeTable",
        "dynamodb:DescribeTimeToLive",
        "dynamodb:GetItem",
        "dynamodb:GetRecords",
        "dynamodb:ListTagsOfResource",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem"
      ],
      "Resource": [
        "${aws_dynamodb_table.auth.arn}",
        "${aws_dynamodb_table.servers.arn}"
      ]
    },
    {
      "Sid": "AllowRunTask",
      "Effect": "Allow",
      "Action": [
        "ecs:RunTask"
      ],
      "Resource": [
        "${aws_ecs_task_definition.launcher.arn}"
      ]
    },
    {
      "Sid": "AllowPassrole",
      "Effect": "Allow",
      "Action": [
        "iam:PassRole"
      ],
      "Resource": [
        "${aws_iam_role.launcher_execution.arn}",
        "${aws_iam_role.launcher_task.arn}"
      ]
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "front_task" {
  role = aws_iam_role.front_task.name
  policy_arn = aws_iam_policy.front_task.arn
}
