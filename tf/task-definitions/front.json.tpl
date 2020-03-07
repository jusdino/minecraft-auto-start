[
  {
    "name": "front",
    "image": "jusdino/minecraft-auto-start-front:latest",
    "memory": 256,
    "essential": true,
    "environment": [
      {
        "name": "APP_NAME",
        "value": "front"
      },
      {
        "name": "FLASK_DEBUG",
        "value": "1"
      },
      {
        "name": "PYTHONUNBUFFERED",
        "value": "0"
      },
      {
        "name": "APP_SETTINGS",
        "value": "front.config.ProductionConfig"
      },
      {
        "name": "DYNAMODB_AUTH_TABLE_NAME",
        "value": "${auth_table_name}"
      },
      {
        "name": "DYNAMODB_SERVERS_TABLE_NAME",
        "value": "${servers_table_name}"
      },
      {
        "name": "AWS_DEFAULT_REGION",
        "value": "${aws_region}"
      },
      {
        "name": "SERVER_DOMAIN",
        "value": "${server_domain}"
      },
      {
        "name": "LAUNCHER_TASK_ARN",
        "value": "${launcher_task_arn}"
      },
      {
        "name": "CLUSTER_ARN",
        "value": "${cluster_arn}"
      }
    ],
    "secrets": [
      {
        "name": "LAUNCHER_NETWORK_CONFIG",
        "valueFrom": "${launcher_network_config_parameter}"
      }
    ],
    "portMappings": [
      {
        "containerPort": 5000,
        "hostPort": 80
      }
    ]
  }
]
