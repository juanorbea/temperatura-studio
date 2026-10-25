#!/bin/sh
# Builds .venv-omnivoice: the OmniVoice voice engine in its own virtualenv (CPU PyTorch).
# Usage: scripts/setup_omnivoice.sh [--cuda]   (--cuda installs the default CUDA build of PyTorch instead)
set -eu
cd "$(dirname "$0")/.."
VENV=.venv-omnivoice
TORCH_INDEX="--index-url https://download.pytorch.org/whl/cpu"
[ "${1:-}" = "--cuda" ] && TORCH_INDEX=""
if command -v uv >/dev/null 2>&1; then
    uv venv "$VENV" --python 3.11
    uv pip install -p "$VENV/bin/python" torch torchaudio $TORCH_INDEX
    uv pip install -p "$VENV/bin/python" omnivoice==0.2.1 soundfile
else
    python3.11 -m venv "$VENV"
    "$VENV/bin/pip" install torch torchaudio $TORCH_INDEX
    "$VENV/bin/pip" install omnivoice==0.2.1 soundfile
fi
"$VENV/bin/python" -c "import omnivoice, torch; print('omnivoice ready, torch', torch.__version__)"
