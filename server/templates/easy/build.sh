echo "Installing dependencies..."
# Typo: pyest instead of pytest
pyest requirements.txt
if [ $? -ne 0 ]; then
    echo "Dependency installation failed."
    exit 1
fi
echo "Dependencies installed."

echo "Running tests..."
pytest test_app.py
if [ $? -ne 0 ]; then
    echo "Tests failed."
    exit 1
fi
echo "Tests passed."
exit 0
