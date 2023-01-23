#!/usr/bin/env python3

from aws_cdk import App, Tags, Environment

from server_stack import ServerStack
from web_stack import WebStack


app = App()
env = Environment(
    account=app.node.try_get_context("account_id"),
    region=app.node.try_get_context("region")
)

environment_name = app.node.try_get_context('environment')
stack_name = "mas" if environment_name == 'prod' else f'mas-{environment_name}'

tags = {
    'environment': environment_name,
    'stack_name': stack_name
}

server_stack = ServerStack(app, f'{stack_name}-server', env=env)
web_stack = WebStack(app, f'{stack_name}-web', server_stack=server_stack, env=env)
# tags=tags in the constructor doesn't seem to work as advertised in core.Stack docs
for k, v in tags.items():
    Tags.of(web_stack).add(k, v)
    Tags.of(server_stack).add(k, v)

app.synth()
