set -e

pip-compile --no-emit-index-url --upgrade requirements.in
pip-compile --no-emit-index-url --upgrade requirements-dev.in
pip-compile --no-emit-index-url --upgrade launcher_lambda/requirements.in
pip-compile --no-emit-index-url --upgrade launcher_lambda/requirements-dev.in
pip-compile --no-emit-index-url --upgrade parameter_lambda/requirements.in
pip-compile --no-emit-index-url --upgrade servers_lambda/requirements.in
pip-compile --no-emit-index-url --upgrade servers_lambda/requirements-dev.in
bin/sync_deps.sh
