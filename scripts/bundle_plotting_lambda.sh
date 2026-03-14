#!/usr/bin/env bash
# Install Plotting Lambda dependencies into lambda_src/plotting so CDK can package them.
# Run this once before: cdk deploy --all
set -e
cd "$(dirname "$0")/.."
pip install -r lambda_src/plotting/requirements.txt -t lambda_src/plotting --quiet
echo "Done. You can now run: cdk deploy --all"
