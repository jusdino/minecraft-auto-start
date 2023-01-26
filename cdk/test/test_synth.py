import json
from unittest import TestCase


class TestSynth(TestCase):
    def test_synth(self):
        with open('cdk.context.json', 'r') as f:
            context = json.load(f)

        from aws_cdk import App, Tags, Environment

        from persistent_stack import PersistentStack
        from server_stack import ServerStack
        from web_stack import WebStack

        app = App(context=context)
        env = Environment(
            account=context["account_id"],
            region=context["region"]
        )

        environment_name = context['environment']
        stack_name = "mas" if environment_name == 'prod' else f'mas-{environment_name}'
        server_domain = app.node.try_get_context('server_domain')

        tags = {
            'environment': environment_name,
            'stack_name': stack_name
        }

        if environment_name != 'prod':
            server_domain = f'{environment_name}.{server_domain}'
        api_domain_name = f'start.{server_domain}'

        persistent_stack = PersistentStack(app, stack_name, env=env, domain_name=server_domain, api_domain_name=api_domain_name)
        server_stack = ServerStack(app, f'{stack_name}-server', env=env, persistent_stack=persistent_stack)
        web_stack = WebStack(
            app, f'{stack_name}-web',
            api_domain_name=api_domain_name,
            domain_name=server_domain,
            persistent_stack=persistent_stack,
            server_stack=server_stack,
            env=env
        )
        # tags=tags in the constructor doesn't seem to work as advertised in core.Stack docs
        for k, v in tags.items():
            Tags.of(persistent_stack).add(k, v)
            Tags.of(server_stack).add(k, v)
            Tags.of(web_stack).add(k, v)

        app.synth()
