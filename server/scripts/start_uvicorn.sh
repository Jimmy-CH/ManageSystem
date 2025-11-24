#!/bin/bash
exec uvicorn server.asgi:application \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --log-level info \
    --timeout-keep-alive 60

