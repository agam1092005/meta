echo "Starting GitHub Action simulation..."
if [ -z "$API_KEY" ]; then
    echo "Error: API_KEY is missing in environment."
    exit 1
fi

# Simulate secret validation
if [ "$API_KEY" != "supersecret" ]; then
    echo "Error: Invalid API_KEY. Check your GHA secrets and workflow mapping."
    exit 1
fi

echo "Deploying to production..."
echo "Linting passed."
echo "Tests passed."
echo "Build successful."
exit 0
