#!/bin/bash
set -euo pipefail

DROPLET_IP="146.190.121.68"   # same IP you SSH into
IMAGE="corbettbw/dataviz-portfolio"
NAME="dataviz-portfolio"

# Fail early if Docker Desktop isn't running
docker info > /dev/null 2>&1 || { echo "Docker Desktop isn't running."; exit 1; }

echo "==> Building image (linux/amd64)"
docker build --platform linux/amd64 -t "$IMAGE" .

echo "==> Pushing to Docker Hub"
docker push "$IMAGE"

echo "==> Swapping container on droplet"
ssh root@"$DROPLET_IP" bash -s <<EOF
set -u
docker pull $IMAGE
docker stop $NAME 2>/dev/null || true
docker rm $NAME 2>/dev/null || true
docker run -d -p 8050:8050 --name $NAME $IMAGE
docker network connect kamal $NAME 2>/dev/null || true
sleep 5

if [ "\$(docker inspect -f '{{.State.Running}}' $NAME)" = "true" ]; then
  echo "==> Container is running"
  docker logs $NAME
  docker exec kamal-proxy kamal-proxy list
else
  echo "==> Container exited. Logs:"
  docker logs $NAME
  exit 1
fi
EOF

echo "==> Done: https://portfolio.corbettwinningham.com"

# chmod +x deploy.sh   # once
# ./deploy.sh          # every deploy