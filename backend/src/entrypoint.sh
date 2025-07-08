echo "Starting backend"
uvicorn main:app --host "$FASTAPI_HOSTS" --port "$FASTAPI_PORTS" --reload

