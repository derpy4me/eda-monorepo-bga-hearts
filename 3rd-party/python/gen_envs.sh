#! /bin/bash

uv export --output-file requirements.txt
uv export --dev --output-file requirements-dev.txt
uv export --group test --output-file requirements-test.txt
uv lock
pants generate-lockfiles
pants export --export-py-resolve-format=symlinked_immutable_virtualenv --export-resolve=reqs-dev
