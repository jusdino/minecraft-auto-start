import json
from unittest import TestCase


class TestSynth(TestCase):
    def test_synth(self):
        from app import MASApp

        with open('cdk.context.json', 'r') as f:
            context = json.load(f)

        # Suppresses lambda bundling for tests
        context['aws:cdk:bundling-stacks'] = []

        app = MASApp(context=context)
        app.synth()
