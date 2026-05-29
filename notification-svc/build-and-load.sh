#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# build-and-load.sh
#
# Builds the notification-svc Docker image and loads it into every worker
# node of a kind cluster so Kubernetes can pull it without a registry.
#
# Usage:
#   ./build-and-load.sh [OPTIONS]
#
# Options:
#   -c, --cluster   kind cluster name  (default: kind)
#   -t, --tag       image tag          (default: latest)
#   -d, --deploy    apply k8s manifests after loading
#   -h, --help      show this help
#
# Examples:
#   ./build-and-load.sh
#   ./build-and-load.sh --cluster my-cluster --tag v1.2.0
#   ./build-and-load.sh --deploy
# ---------------------------------------------------------------------------

set -euo pipefail

# ── defaults ────────────────────────────────────────────────────────────────
IMAGE_NAME="notification-svc"
IMAGE_TAG="latest"
CLUSTER_NAME="kind"
DEPLOY=false
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── colours ─────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'
log()   { echo -e "${GREEN}[✔]${NC} $*"; }
info()  { echo -e "${CYAN}[→]${NC} $*"; }
warn()  { echo -e "${YELLOW}[!]${NC} $*"; }
error() { echo -e "${RED}[✘] $*${NC}" >&2; exit 1; }
step()  { echo -e "\n${CYAN}━━━ $* ━━━${NC}"; }

# ── argument parsing ─────────────────────────────────────────────────────────
usage() {
  grep '^#' "$0" | grep -v '#!/' | sed 's/^# \{0,3\}//'
  exit 0
}

while [[ $# -gt 0 ]]; do
  case $1 in
    -c|--cluster) CLUSTER_NAME="$2"; shift 2 ;;
    -t|--tag)     IMAGE_TAG="$2";    shift 2 ;;
    -d|--deploy)  DEPLOY=true;       shift   ;;
    -h|--help)    usage ;;
    *) error "Unknown option: $1" ;;
  esac
done

FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

# ── prerequisite checks ──────────────────────────────────────────────────────
step "Checking prerequisites"

for cmd in docker kind kubectl; do
  if command -v "$cmd" &>/dev/null; then
    log "$cmd found ($(command -v "$cmd"))"
  else
    error "$cmd is not installed or not in PATH"
  fi
done

if ! kind get clusters 2>/dev/null | grep -q "^${CLUSTER_NAME}$"; then
  error "kind cluster '${CLUSTER_NAME}' not found.\n  Run: kind create cluster --name ${CLUSTER_NAME}"
fi
log "kind cluster '${CLUSTER_NAME}' is running"

# ── resolve worker nodes ─────────────────────────────────────────────────────
step "Resolving worker nodes in cluster '${CLUSTER_NAME}'"

WORKER_NODES=()
while IFS= read -r node; do
  [[ -n "$node" ]] && WORKER_NODES+=("$node")
done < <(kind get nodes --name "${CLUSTER_NAME}" 2>/dev/null | grep -v 'control-plane' || true)

if [[ ${#WORKER_NODES[@]} -eq 0 ]]; then
  warn "No dedicated worker nodes found — loading to all nodes instead"
  NODE_ARG=""
else
  log "Worker nodes detected:"
  for n in "${WORKER_NODES[@]}"; do
    info "  • $n"
  done
  NODE_ARG="--nodes $(IFS=,; echo "${WORKER_NODES[*]}")"
fi

# ── docker build ─────────────────────────────────────────────────────────────
step "Building Docker image"

info "Context : ${SCRIPT_DIR}"
info "Image   : ${FULL_IMAGE}"

docker build \
  --tag "${FULL_IMAGE}" \
  --file "${SCRIPT_DIR}/Dockerfile" \
  "${SCRIPT_DIR}"

log "Image built: ${FULL_IMAGE}"
info "Size: $(docker image inspect "${FULL_IMAGE}" --format='{{.Size}}' | numfmt --to=iec)"

# ── kind load ────────────────────────────────────────────────────────────────
step "Loading image into kind cluster '${CLUSTER_NAME}'"

# shellcheck disable=SC2086
kind load docker-image "${FULL_IMAGE}" \
  --name "${CLUSTER_NAME}" \
  ${NODE_ARG}

log "Image '${FULL_IMAGE}' loaded into worker node(s)"

# verify the image is visible on each worker via crictl
step "Verifying image on worker nodes"
for node in "${WORKER_NODES[@]}"; do
  if docker exec "${node}" crictl images 2>/dev/null | grep -q "${IMAGE_NAME}"; then
    log "${node}: image present"
  else
    warn "${node}: image not found via crictl (may still be loading)"
  fi
done

# ── optional k8s deploy ──────────────────────────────────────────────────────
if [[ "${DEPLOY}" == true ]]; then
  step "Applying Kubernetes manifests"
  NAMESPACE="notification-svc"

  info "Creating / updating secret..."
  bash "${SCRIPT_DIR}/create-secret.sh"

  info "Applying namespace..."
  kubectl apply -f "${SCRIPT_DIR}/k8s-config/namespace.yaml"

  info "Applying configmap..."
  kubectl apply -f "${SCRIPT_DIR}/k8s-config/configmap.yaml"

  info "Applying deployment..."
  kubectl apply -f "${SCRIPT_DIR}/k8s-config/deployment.yaml"

  info "Applying service..."
  kubectl apply -f "${SCRIPT_DIR}/k8s-config/service.yaml"

  echo ""
  log "Manifests applied. Waiting for rollout..."
  kubectl rollout status deployment/notification-svc -n "${NAMESPACE}" --timeout=120s

  echo ""
  log "Pods:"
  kubectl get pods -n "${NAMESPACE}"
fi

# ── done ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Done! '${FULL_IMAGE}' is ready on all worker nodes.${NC}"
if [[ "${DEPLOY}" == false ]]; then
  echo -e "${CYAN}  To also deploy:  ./build-and-load.sh --deploy${NC}"
fi
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
