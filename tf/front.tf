resource "aws_ecs_task_definition" "front" {
  family = "front"
  container_definitions = file("${path.module}/task-definitions/front.json")
}

resource "aws_ecs_service" "front" {
  name = "front"
  cluster = aws_ecs_cluster.front.id
  task_definition = aws_ecs_task_definition.front.arn
  desired_count = 1
  launch_type = "EC2"
  propagate_tags = "SERVICE"
  network_configuration {
    subnets = data.terraform_remote_state.vpc.outputs.subnet_ids
    security_groups = [aws_security_group.front.id]
  }
}