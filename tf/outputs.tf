output auth_db_name{
  value = aws_dynamodb_table.auth.name
}

output servers_db_name{
  value = aws_dynamodb_table.servers.name
}

output launcher_task_arn{
  value = aws_ecs_task_definition.launcher.arn
}

output launcher_task_family{
  value = aws_ecs_task_definition.launcher.family
}

output launcher_network_config{
  value = aws_ssm_parameter.launcher_network_config.value
}
