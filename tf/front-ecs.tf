resource "aws_ecs_cluster" "front" {
  name = "front"
  tags = merge({Name = "front"}, var.tags)
}

resource "aws_instance" "ecs_node" {
  count = var.front_instance_count
  ami = data.aws_ami.ecs.id
  // Fan out across subnets (AZs)
  subnet_id = data.terraform_remote_state.vpc.outputs.subnet_ids[count.index % length(data.terraform_remote_state.vpc.outputs.subnet_ids)]
  instance_initiated_shutdown_behavior = "terminate"
  instance_type = "t3.micro"
  key_name = aws_key_pair.front.key_name
  security_groups = [aws_security_group.front.id]
  associate_public_ip_address = true
  iam_instance_profile = aws_iam_instance_profile.ecs_node.name
  tags = merge({Name = "${local.app_key}-ecs-node"}, var.tags)
  volume_tags = merge({Name = "${local.app_key}-ecs-node-${count.index}"}, var.tags)
  user_data = <<USER_DATA
#!/bin/bash
echo "ECS_CLUSTER=${aws_ecs_cluster.front.name}" > /etc/ecs/ecs.config
echo "ECS_IMAGE_PULL_BEHAVIOR=always" >> /etc/ecs/ecs.config
USER_DATA
}

data "aws_ami" "ecs" {
  most_recent = true

  owners = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn-ami-*-amazon-ecs-optimized"]
  }
}

resource "aws_security_group" "front" {
  name = "${local.app_key}-${aws_ecs_cluster.front.name}"
  description = aws_ecs_cluster.front.name
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id

  ingress {
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = var.ssh_in_cidr_blocks
  }

  ingress {
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = var.ssh_in_cidr_blocks
  }

  egress {
    from_port = 0
    to_port = 65535
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge({Name = aws_ecs_cluster.front.name}, var.tags)
}

resource "aws_iam_role" "ecs_node" {
  path = "/${local.app_key}/"
  name = "ecs-node"
  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_policy" "ecs_node" {
  name = "${local.app_key}-ecs-node"
  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeTags",
                "ecs:DeregisterContainerInstance",
                "ecs:DiscoverPollEndpoint",
                "ecs:Poll",
                "ecs:RegisterContainerInstance",
                "ecs:StartTelemetrySession",
                "ecs:UpdateContainerInstancesState",
                "ecs:Submit*",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "ecs_node" {
  role = aws_iam_role.ecs_node.name
  policy_arn = aws_iam_policy.ecs_node.arn
}

resource "aws_iam_instance_profile" "ecs_node" {
  name = "ecs-node"
  role = aws_iam_role.ecs_node.name
}
