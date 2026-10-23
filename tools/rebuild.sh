#!/usr/bin/env bash
set -eu
if [ "$#" -ne 1 ]; then echo 'Usage: bash tools/rebuild.sh /absolute/path/to/original.gba' >&2; exit 1; fi
project_path=$(cd "$(dirname "$0")/.." && pwd)
python3 "$project_path/tools/prepare_assets.py" "$1"
bash "$project_path/native/build.sh"
echo 'Resources and host runtime are ready. Build Android with tools/build_android_debug.py.'
