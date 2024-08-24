import json
import textwrap

from constructs import Construct
from aws_cdk import RemovalPolicy, CfnOutput, Duration
from aws_cdk.aws_cognito import UserPool, UserInvitationConfig, UserPoolClient
from aws_cdk.aws_ssm import StringParameter


class Users(Construct):
    """
    User management resources
    """

    def __init__(self, scope: Construct, construct_id: str, domain_name: str, removal: RemovalPolicy, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        email_body = textwrap.dedent(
            f'You are invited to join a Minecraft-Auto-Start server at https://{domain_name}/ui/.  '
            f'Your username is {{username}} and temporary password is {{####}}.'
        )
        self.user_pool = UserPool(
            self, 'Users',
            removal_policy=removal,
            user_invitation=UserInvitationConfig(
                email_subject='Minecraft-Auto-Start invitation',
                email_body=email_body
            )
        )
        CfnOutput(self, 'UserPoolId', value=self.user_pool.user_pool_id)
        self.user_client = UserPoolClient(
            self, 'UsersClient',
            user_pool=self.user_pool,
            access_token_validity=Duration.minutes(60),
            generate_secret=False
        )
        self.user_pool_parameter = StringParameter(
            self, 'UserPoolConfig',
            string_value=json.dumps({
                'UserPoolId': self.user_pool.user_pool_id,
                'ClientId': self.user_client.user_pool_client_id
            })
        )
        CfnOutput(self, 'UserPoolClientId', value=self.user_client.user_pool_client_id)
