from aws_cdk import (
    core as cdk,
    aws_cognito as cognito
)


class CognitoStack(cdk.Construct):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        user_pool = cognito.UserPool(
            self, 'Users'
        )
        cdk.CfnOutput(self, 'UserPoolId', value=user_pool.user_pool_id)
        user_client = cognito.UserPoolClient(
            self, 'UsersClient',
            user_pool=user_pool,
            access_token_validity=cdk.Duration.minutes(60),
            generate_secret=False
        )
        cdk.CfnOutput(self, 'UserPoolClientId', value=user_client.user_pool_client_id)
