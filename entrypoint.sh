#!/bin/sh

# Sai imediatamente se um comando falhar
set -e

# Verifica o modo da aplicação
if [ "$APP_MODE" = "SETUP" ]; then
  echo ">>> Running in SETUP mode..."
  # Inicia o servidor web de instalação
  exec python setup_app.py
else
  echo ">>> Running in RUN mode..."
  # Inicia a aplicação principal com o Supervisor
  exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
fi
