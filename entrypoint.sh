#!/bin/sh
set -e

if [ "$APP_MODE" = "SETUP" ]; then
  echo ">>> Running in SETUP mode..."
  exec python setup_app.py
else
  echo ">>> Running in RUN mode..."
  
  # --- PASSO DE DIAGNÓSTICO ---
  echo "--- Verificando o conteúdo de /etc/supervisor/conf.d/ ---"
  ls -la /etc/supervisor/conf.d/
  echo "--------------------------------------------------------"
  
  # Inicia a aplicação principal
  exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
fi
