set -e

echo "Disabling automatic CRLF -- LF conversion..."
git config core.autocrlf false

echo "Forcing git to normalize to LF on checkout and commit..."
git config core.eol lf

echo "enabling safe-CRLF checking (will refuse commits with mixed line endings)"
git config core.safecrlf true

echo "Removing .venv (if exists)..."
rm -rf .venv

echo "Creating python virtual environment (.venv)..."
python -m venv .venv

echo "Installing pip dependencies..."
./__python -m pip install -r requirements.txt

echo "Setup complete!"

set +e