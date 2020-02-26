resource "aws_eip" "server" {
  count = var.front_instance_count
  instance = aws_instance.ecs_node[count.index].id
  vpc = true
  tags = merge({Name = "${local.app_key}-ecs-node-${count.index}" }, var.tags)
}

resource "aws_route53_record" "server" {
  zone_id = data.terraform_remote_state.dns.outputs.hosted_zone_id
  name = "start.${data.terraform_remote_state.dns.outputs.hosted_zone_domain}"
  type = "A"
  ttl = 60
  records = aws_eip.server[*].public_ip
}