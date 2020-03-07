# Terragrunt will copy the Terraform configurations specified by the source parameter, along with any files in the
# working directory, into a temporary folder, and execute your Terraform commands in that folder.
terraform {
  source = "git::https://github.com/jusdino/terraform-modules.git//minecraft-server?ref=dev"
}

# Include all settings from the root terragrunt.hcl file
include {
  path = find_in_parent_folders()
}

# These are the variables we have to pass in to use the module specified in the terragrunt configuration above
inputs = {
  name = "__SERVER_NAME__"
  instance_type = "t3.small"
  memory = "1536m"
  tags = {
    Name = "__SERVER_NAME__"
    Env = "dev"
  }
}
