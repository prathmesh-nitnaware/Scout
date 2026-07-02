z#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting Render build..."

# 1. Install dependencies
pip install -r requirements.txt

# 2. Create artifacts directory if it doesn't exist
mkdir -p artifacts

# 3. Download the large artifact files if URLs are provided in Render Environment Variables
if [ -n "$PARQUET_URL" ]; then
    echo "Downloading candidate_features.parquet..."
    curl -L -o artifacts/candidate_features.parquet "$PARQUET_URL"
else
    echo "Warning: PARQUET_URL environment variable is not set. The app might fail to start if the file is missing."
fi

if [ -n "$EMBEDDINGS_URL" ]; then
    echo "Downloading embeddings.npy..."
    curl -L -o artifacts/embeddings.npy "$EMBEDDINGS_URL"
else
    echo "Warning: EMBEDDINGS_URL environment variable is not set. The app might fail to start if the file is missing."
fi

echo "Build complete."
