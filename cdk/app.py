#!/usr/bin/env python3

from aws_cdk import App, Tags, Environment

from persistent_stack import PersistentStack
from server_stack import ServerStack
from web_stack import WebStack


app = App()
env = Environment(
    account=app.node.try_get_context("account_id"),
    region=app.node.try_get_context("region")
)

environment_name = app.node.try_get_context('environment')
sub_domain = app.node.try_get_context('sub_domain')
stack_name = "mas" if environment_name == 'prod' else f'mas-{environment_name}'

tags = {
    'Environment': environment_name,
    'StackName': stack_name
}

if environment_name != 'prod':
    sub_domain = f'{environment_name}.{sub_domain}'
api_domain_name = f'start.{sub_domain}'

persistent_stack = PersistentStack(app, stack_name, env=env, api_domain_name=api_domain_name, sub_domain=sub_domain)
server_stack = ServerStack(app, f'{stack_name}-server', env=env, persistent_stack=persistent_stack)
web_stack = WebStack(
    app, f'{stack_name}-web',
    api_domain_name=api_domain_name,
    sub_domain=sub_domain,
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
