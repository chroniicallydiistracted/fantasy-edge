# SAVE AS: setup_dev_deps.sh
# USAGE: chmod +x setup_dev_deps.sh && ./setup_dev_deps.sh
set -euo pipefail

echo "🔧 Installing system packages..."
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
  git curl ca-certificates unzip jq \
  build-essential pkg-config \
  python3 python3-venv python3-pip \
  postgresql-client redis-tools

echo "🟩 Installing Node 20 via nvm (user-local)..."
if [ ! -d "$HOME/.nvm" ]; then
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
fi
# shellcheck source=/dev/null
. "$HOME/.nvm/nvm.sh"
nvm install 20
nvm alias default 20
node -v && npm -v

echo "⬇️  Installing global CLIs (Vercel, Fly)..."
npm i -g vercel
if ! command -v flyctl >/dev/null 2>&1; then
  curl -fsSL https://fly.io/install.sh | sh
  export PATH="$HOME/.fly/bin:$PATH"
  # add to shell startup if not already present
  if ! grep -qs 'export PATH="$HOME/.fly/bin:$PATH"' "$HOME/.bashrc"; then
    echo 'export PATH="$HOME/.fly/bin:$PATH"' >> "$HOME/.bashrc"
  fi
fi

echo "🐳 Checking Docker/Compose..."
if command -v docker >/dev/null 2>&1; then
  docker --version || true
  docker compose version || echo "Note: docker compose plugin not detected—if using Docker Desktop on Windows, it's already bundled."
else
  echo "WARN: docker not found in PATH. If you use Docker Desktop for Windows, ensure WSL integration is enabled."
fi

echo "✅ Done."
echo "Installed: git, curl, jq, build-essential, Python3 + pip/venv, psql client, redis-tools, Node 20 (nvm), vercel, flyctl."
echo "Next: open a new shell (or 'source ~/.bashrc') so nvm/flyctl are on PATH."
