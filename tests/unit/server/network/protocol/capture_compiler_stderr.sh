#!/usr/bin/env bash

set -o pipefail

log_dir="${GITHUB_WORKSPACE:-$(pwd)}/build/linux-debug/test-logs"
mkdir -p "${log_dir}"
"$@" 2> >(tee -a "${log_dir}/compiler-stderr.log" >&2)
