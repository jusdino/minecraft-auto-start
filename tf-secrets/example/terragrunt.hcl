# Terragrunt will copy the Terraform configurations specified by the source parameter, along with any files in the
# working directory, into a temporary folder, and execute your Terraform commands in that folder.
terraform {
	source = "git::https://github.com/jusdino/minecraft-auto-start.git//tf-secrets?ref=terraform"
}

# Include all settings from the root terragrunt.hcl file
include {
  path = find_in_parent_folders()
}

# These are the variables we have to pass in to use the module specified in the terragrunt configuration above
inputs = {
	infra_live_clone_url = "git@github.com:user/infrastructure-live-01.git"
	public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCfoPeq2Dbnl1ZsJT24/JmiT/3g/XK4D46nWhajJbg/bmJLcx1R+c+q4rjdkUr82PykZ3EEsh9WorBf/Uc6xqVg6hiNhjrhLKJQ3WdJTgA2TTHFRXfbShDIOGojrkmrXr47gXHWmnD9FDAYGx7AEx/9o3E1bKn6P8il6RJ9r3YEbngwS10O6SCApV/Rf9Z9Cj0pGR5PY7nhqiBs/Qrp9Y7Hgi6R8KgH7Ay5n9CNFU8tNCYIaATA6/5Ij1tXCe4tbp1SBvkNhsyeicAkr3NMXwzIbb05MSfswwavSzGfcmECE1LsflTaSpQ9WEcrloX24zcu0/YjmD8H2E3jjdYnAKg9"
	known_hosts = "|1|UFQ00InqffAwRfTuAgH4YqRoRbY=|vEMX3Hd3WDB3OPn8xxfEkiYrRzM= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ=="
  tags = {
		Env = "dev"
	}
}
