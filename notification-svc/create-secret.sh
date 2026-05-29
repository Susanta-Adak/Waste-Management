#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# create-secret.sh
#
# Creates (or updates) the notification-svc-secrets Kubernetes Secret from
# values in .env.  Safe to re-run — uses kubectl apply via --dry-run piped
# to replace so it works whether the secret already exists or not.
#
# Usage:
#   ./create-secret.sh [--env-file PATH]
#
# Options:
#   --env-file   path to the env file  (default: .env in this directory)
# ---------------------------------------------------------------------------

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"
NAMESPACE="notification-svc"
SECRET_NAME="notification-svc-secrets"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'
log()   { echo -e "${GREEN}[✔]${NC} $*"; }
info()  { echo -e "${CYAN}[→]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✘] $*${NC}" >&2; exit 1; }
step()  { echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }

# ── argument parsing ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case $1 in
    --env-file) ENV_FILE="$2"; shift 2 ;;
    *) error "Unknown option: $1" ;;
  esac
done

# ── load .env ────────────────────────────────────────────────────────────────
step "Loading environment from ${ENV_FILE}"

[[ -f "${ENV_FILE}" ]] || error ".env file not found at '${ENV_FILE}'.\n  Copy .env.example → .env and fill in your values."

# Parse key=value lines; skip comments and blanks
_load_env() {
  while IFS= read -r line || [[ -n "$line" ]]; do
    # strip inline comments and leading/trailing whitespace
    line="${line%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -z "$line" || "$line" == \#* ]] && continue
    [[ "$line" == *=* ]] || continue
    local key="${line%%=*}"
    local val="${line#*=}"
    # strip surrounding quotes if present
    val="${val%\"}"
    val="${val#\"}"
    val="${val%\'}"
    val="${val#\'}"
    export "$key=$val"
  done < "$1"
}

_load_env "${ENV_FILE}"

# ── apply defaults for local dev if vars are empty ───────────────────────────
SECRET_KEY="${SECRET_KEY:-$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))' 2>/dev/null || echo "change-me-$(date +%s)")}"
DB_PASSWORD="${DB_PASSWORD:-postgres}"
EMAIL_HOST_USER="${EMAIL_HOST_USER:-}"
EMAIL_HOST_PASSWORD="${EMAIL_HOST_PASSWORD:-}"
TWILIO_ACCOUNT_SID="${TWILIO_ACCOUNT_SID:-}"
TWILIO_AUTH_TOKEN="${TWILIO_AUTH_TOKEN:-}"

info "SECRET_KEY        : ${SECRET_KEY:0:8}…(redacted)"
info "DB_PASSWORD       : ${DB_PASSWORD:0:3}…(redacted)"
info "EMAIL_HOST_USER   : ${EMAIL_HOST_USER:-<empty>}"
info "TWILIO_ACCOUNT_SID: ${TWILIO_ACCOUNT_SID:-<empty>}"

# ── ensure namespace exists ──────────────────────────────────────────────────
step "Ensuring namespace '${NAMESPACE}'"

kubectl get namespace "${NAMESPACE}" &>/dev/null \
  || kubectl create namespace "${NAMESPACE}"
log "Namespace ready"

# ── generate secret.yaml and apply ──────────────────────────────────────────
step "Generating k8s-config/secret.yaml"

SECRET_FILE="${SCRIPT_DIR}/k8s-config/secret.yaml"

kubectl create secret generic "${SECRET_NAME}" \
  --namespace "${NAMESPACE}" \
  --from-literal=secret-key="${SECRET_KEY}" \
  --from-literal=db-password="${DB_PASSWORD}" \
  --from-literal=email-host-user="${EMAIL_HOST_USER}" \
  --from-literal=email-host-password="${EMAIL_HOST_PASSWORD}" \
  --from-literal=twilio-account-sid="${TWILIO_ACCOUNT_SID}" \
  --from-literal=twilio-auth-token="${TWILIO_AUTH_TOKEN}" \
  --dry-run=client -o yaml > "${SECRET_FILE}"

log "Written → ${SECRET_FILE}"

step "Applying secret '${SECRET_NAME}' in namespace '${NAMESPACE}'"

kubectl apply -f "${SECRET_FILE}"

log "Secret '${SECRET_NAME}' applied"

# ── verify ───────────────────────────────────────────────────────────────────
step "Verifying secret keys"

KEYS=$(kubectl get secret "${SECRET_NAME}" -n "${NAMESPACE}" \
  -o jsonpath='{.data}' | tr ',' '\n' | grep -o '"[^"]*":' | tr -d '"' | tr -d ':')

for key in secret-key db-password email-host-user email-host-password twilio-account-sid twilio-auth-token; do
  if echo "${KEYS}" | grep -q "^${key}$"; then
    log "  ${key}"
  else
    warn "  ${key} — missing!"
  fi
done

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Secret '${SECRET_NAME}' is ready.${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
