#!/bin/sh
set -e

CERT_DIR='/var/certs'
mkdir "$CERT_DIR"
echo "$SSL_CERT" >"${CERT_DIR}/cert.pem"
echo "$SSL_KEY" >"${CERT_DIR}/key.pem"
chmod 600 -R "$CERT_DIR"

gunicorn 'front:create_app()' \
  --keyfile "${CERT_DIR}/key.pem" \
  --certfile "${CERT_DIR}/cert.pem" \
  --access-logfile - \
  "$@"
