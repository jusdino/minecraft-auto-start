output "auth_db_name" {
  value = aws_dynamodb_table.auth.name
}
output "servers_db_name" {
  value = aws_dynamodb_table.servers.name
}