output "kms_key_id" {
  value = aws_kms_key.main.key_id
}

output "kms_key_arn" {
  value = aws_kms_key.main.arn
}

output "known_hosts_parameter_name" {
  value = aws_ssm_parameter.known_hosts.name
}

output "clone_url_parameter_name" {
  value = aws_ssm_parameter.clone_url.name
}

output "ssh_key_parameter_name" {
  value = aws_ssm_parameter.clone_url.name
}

output "known_hosts_parameter_arn" {
  value = aws_ssm_parameter.known_hosts.arn
}

output "clone_url_parameter_arn" {
  value = aws_ssm_parameter.clone_url.arn
}

output "ssh_key_parameter_arn" {
  value = aws_ssm_parameter.clone_url.arn
}
