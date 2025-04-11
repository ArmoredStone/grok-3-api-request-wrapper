#!/bin/bash

# Help function
show_help() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -c, --content      User content to send in the request"
    echo "  -s, --system       System content to include (optional)"
    echo "  -a, --auth         Authorization token/API key"
    echo "  -u, --url          API URL (defaults to https://api.x.ai/v1/chat/completions)"
    echo "  -m, --model        Model to use (defaults to grok-3-latest)"
    echo "  -h, --help         Show this help message"
    echo "  -o, --output       Output file to save the response (optional)"
    echo
    echo "Example:"

    echo "  $0 -c \"What is the weather?\" -s \"You are a helpful assistant\" -o \"outputfile.md\""
    exit 1
}

# Default values
URL="https://api.x.ai/v1/chat/completions"
MODEL="grok-3-latest"
SYSTEM_CONTENT=""
USER_CONTENT=""
AUTH_TOKEN=""
OUTPUT_FILE=""

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--content)
            USER_CONTENT="$2"
            shift 2
            ;;
        -s|--system)
            SYSTEM_CONTENT="$2"
            shift 2
            ;;
        -u|--url)
            URL="$2"
            shift 2
            ;;
        -m|--model)
            MODEL="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -a|--auth)
            AUTH_TOKEN="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            ;;
    esac
done

if [ -z "$AUTH_TOKEN" ]; then
    # Load environment variables from .env file if it exists
    if [ -f .env ]; then
        echo "Loading AUTH_TOKEN variables from .env file..."
        set -o allexport
        source .env
        set +o allexport
    else
        echo ".env file not found. Proceeding with default values."
    fi
    if [ -z "$AUTH_TOKEN" ]; then
        echo "Error: Authorization token is required. Use -a or set AUTH_TOKEN in .env file."
        show_help
    fi
fi

# Check if required parameters are provided
if [ -z "$USER_CONTENT" ]; then
    echo "Error: User content (-c) is required."
    show_help
fi

# Create JSON payload
if [ -z "$SYSTEM_CONTENT" ]; then
    # JSON without system content
    JSON_PAYLOAD=$(cat <<EOF
{
  "messages": [
    {
      "role": "user",
      "content": "$USER_CONTENT"
    }
  ],
  "model": "$MODEL",
  "stream": false,
  "temperature": 0
}
EOF
)
else
    # JSON with system content
    JSON_PAYLOAD=$(cat <<EOF
{
  "messages": [
    {
      "role": "system",
      "content": "$SYSTEM_CONTENT"
    },
    {
      "role": "user",
      "content": "$USER_CONTENT"
    }
  ],
  "model": "$MODEL",
  "stream": false,
  "temperature": 0
}
EOF
)
fi

# Execute curl command
echo "Sending request to $URL..."
RESPONSE=$(curl -s "$URL" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $AUTH_TOKEN" \
    -d "$JSON_PAYLOAD")

# Display response with Python

source venv/bin/activate

save_response() {
    if [ -n "$OUTPUT_FILE" ]; then
        python3 parse_grok_response.py "$RESPONSE" | tee "$OUTPUT_FILE"
        echo "Response saved to $OUTPUT_FILE"
    else
        python3 parse_grok_response.py "$RESPONSE"
        echo "No output file specified. Response not saved."
    fi
}

save_response
