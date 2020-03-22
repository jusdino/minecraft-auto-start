[
  {
    "name": "launcher",
    "image": "jusdino/minecraft-auto-start-launcher:latest",
    "essential": true,
    "secrets": [
      {
        "name": "KNOWN_HOSTS",
        "valueFrom": "${known_hosts_parameter}"
      },
      {
        "name": "INFRA_LIVE_CLONE_URL",
        "valueFrom": "${infra_live_clone_url_parameter}"
      },
      {
        "name": "SSH_AGENT_KEY",
        "valueFrom": "${ssh_agent_key_parameter}"
      }
    ],
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-group": "${log_group_name}",
        "awslogs-region": "${region}",
        "awslogs-stream-prefix": "launcher"
      }
    }
  }
]
