locals {
  app_acronym = "mas"
  app_key = "${local.app_acronym}-${var.environment}"
}

resource "aws_kms_key" "main" {
  description = local.app_key
  deletion_window_in_days = 7
}

resource "aws_kms_alias" "main" {
  name = "alias/${local.app_key}"
  target_key_id = aws_kms_key.main.key_id
}
