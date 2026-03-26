echo "Verifying Docker Compose configuration..."
if grep -q "localhost" docker-compose.yml; then
    echo "Error: Service 'web' cannot reach 'db' via localhost in Docker network."
    exit 1
fi
echo "Services healthy."
echo "Running tests..."
pytest test_app.py
if [ $? -ne 0 ]; then
    echo "Tests failed."
    exit 1
fi
echo "Tests passed."
exit 0
