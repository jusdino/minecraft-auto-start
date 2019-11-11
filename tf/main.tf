provider "aws" {
  region = var.aws_region
}

terraform {
  backend "s3" {}
}

resource "aws_ecs_cluster" "front" {
  name = "front"
  tags = merge({Name = "front"}, var.tags)
}

module "front_asg" {
  source = "terraform-aws-modules/autoscaling/aws"
  version = "~> 3.0"

  user_data = <<USER_DATA
#!/bin/bash
echo "ECS_CLUSTER=${aws_ecs_cluster.front.name}" > /etc/ecs/ecs.config
USER_DATA

  name = aws_ecs_cluster.front.name

  lc_name = aws_ecs_cluster.front.name
  image_id = data.aws_ami.ecs.id
  instance_type = "t3.micro"
  iam_instance_profile = aws_iam_instance_profile.ecs_node.name
  key_name = aws_key_pair.front.key_name
  associate_public_ip_address = true
  security_groups = [aws_security_group.front.id]

  asg_name = aws_ecs_cluster.front.name
  vpc_zone_identifier = data.terraform_remote_state.vpc.outputs.subnet_ids
  health_check_type = "EC2"
  min_size = 0
  max_size = 1
  desired_capacity = 1
  wait_for_capacity_timeout = "300s"

  tags_as_map = merge({Name = aws_ecs_cluster.front.name}, var.tags)
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
  name = aws_ecs_cluster.front.name
  description = "Allow ssh in"
  vpc_id = data.terraform_remote_state.vpc.outputs.vpc_id

  ingress {
    from_port = 22
    to_port = 22
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

resource "aws_key_pair" "front" {
  key_name = "front"
  public_key = var.public_key
}

resource "aws_iam_role" "ecs_node" {
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

resource "aws_iam_policy" {
	name = "ecs_node"
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

data "terraform_remote_state" "vpc" {
  backend = "s3"
  config = {
    bucket = var.tfstate_global_bucket
    region = var.tfstate_global_bucket_region
    key = "dev/public/vpc/terraform.tfstate"
  }
}
