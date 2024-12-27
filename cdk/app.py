#!/usr/bin/env python3

from aws_cdk import App, Environment

from stacks.persistent import PersistentStack
from stacks.server import ServerStack
from stacks.web import WebStack


class MASApp(App):
    """
    Minecraft-Auto-Start CDK App
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        env = Environment(
            account=self.node.try_get_context("account_id"),
            region=self.node.try_get_context("region")
        )

        environment_name = self.node.get_context('environment')
        sub_domain = self.node.get_context('sub_domain')
        stack_name = "mas" if environment_name == 'prod' else f'mas-{environment_name}'

        tags = {
            'Environment': environment_name,
            'StackName': stack_name
        }

        if environment_name != 'prod':
            sub_domain = f'{environment_name}.{sub_domain}'
        api_domain_name = f'start.{sub_domain}'

        persistent_stack = PersistentStack(
            self, stack_name,
            env=env,
            api_domain_name=api_domain_name,
            sub_domain=sub_domain,
            tags=tags
        )
        server_stack = ServerStack(
            self, f'{stack_name}-server',
            env=env,
            persistent_stack=persistent_stack,
            tags=tags
        )
        WebStack(
            self, f'{stack_name}-web',
            api_domain_name=api_domain_name,
            sub_domain=sub_domain,
            persistent_stack=persistent_stack,
            server_stack=server_stack,
            env=env,
            tags=tags
        )


if __name__ == '__main__':
    MASApp().synth()
