#!/bin/sh

# Generate runtime environment configuration
cat > /usr/share/nginx/html/env.js << EOF
window.ENV = {
  REACT_APP_API_URL: '${REACT_APP_API_URL:-http://localhost:8000/api}',
  REACT_APP_WS_URL: '${REACT_APP_WS_URL:-ws://localhost:8000/ws}',
  NODE_ENV: '${NODE_ENV:-production}'
};
EOF

echo "Environment configuration generated:"
cat /usr/share/nginx/html/env.js

# Execute the main command
exec "$@"