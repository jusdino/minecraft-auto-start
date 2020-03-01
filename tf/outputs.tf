output "auth_db_name" {
  value = aws_dynamodb_table.auth.name
}

output "servers_db_name" {
  value = aws_dynamodb_table.servers.name
}

output "front_fqdn" {
  value = aws_route53_record.server.fqdn
}