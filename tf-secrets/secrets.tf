resource "aws_ssm_parameter" "known_hosts" {
  name = "/${local.app_key}/known-hosts"
  type = "SecureString"
  key_id = aws_kms_key.main.key_id
  value = var.known_hosts
  overwrite = true
}

resource "aws_ssm_parameter" "clone_url" {
  name = "/${local.app_key}/clone-url"
  type = "SecureString"
  key_id = aws_kms_key.main.key_id
  value = var.infra_live_clone_url
  overwrite = true
}

resource "aws_ssm_parameter" "ssh_key" {
  name = "/${local.app_key}/ssh-key"
  type = "SecureString"
  key_id = aws_kms_key.main.key_id
  value = "NotInTfState"
  overwrite = true
}

resource "aws_ssm_parameter" "ssl_key" {
  name = "/${local.app_key}/ssl-key"
  type = "SecureString"
  key_id = aws_kms_key.main.key_id
  value = "NotInTfState"
  overwrite = true
}

resource "aws_ssm_parameter" "ssl_cert" {
  name = "/${local.app_key}/ssl-cert"
  type = "SecureString"
  key_id = aws_kms_key.main.key_id
  value = "NotInTfState"
  overwrite = true
}