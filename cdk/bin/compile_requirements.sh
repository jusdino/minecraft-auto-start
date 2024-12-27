set -e

pip-compile --no-emit-index-url --upgrade requirements.in
pip-compile --no-emit-index-url --upgrade requirements-dev.in
pip-compile --no-emit-index-url --upgrade lambdas/launcher/requirements.in
pip-compile --no-emit-index-url --upgrade lambdas/launcher/requirements-dev.in
pip-compile --no-emit-index-url --upgrade lambdas/parameter/requirements.in
pip-compile --no-emit-index-url --upgrade lambdas/servers/requirements.in
pip-compile --no-emit-index-url --upgrade lambdas/servers/requirements-dev.in
bin/sync_deps.sh
