#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting Render build..."

# 1. Install dependencies
pip install -r requirements.txt

# (Optional) Install gdown in case the user wants to use Google Drive links
pip install gdown

# 2. Create artifacts directory if it doesn't exist
mkdir -p artifacts

# Helper function to download using curl or gdown depending on the URL
download_file() {
    local url=$1
    local dest=$2
    
    if [[ "$url" == *"drive.google.com"* ]]; then
        echo "Detected Google Drive URL. Using gdown..."
        # Extract the file ID from the Google Drive URL
        FILE_ID=$(echo "$url" | grep -oP '(?<=/d/)[a-zA-Z0-9_-]+|(?<=id=)[a-zA-Z0-9_-]+')
        if [ -n "$FILE_ID" ]; then
            gdown "$FILE_ID" -O "$dest"
        else
            echo "Error: Could not extract Google Drive file ID from $url"
            gdown "$url" -O "$dest"
        fi
    else
        echo "Using curl to download..."
        curl -L -o "$dest" "$url"
    fi
    
    # Check file size (if it's less than 1MB, it's probably an HTML page, not the real data file)
    FILESIZE=$(stat -c%s "$dest" 2>/dev/null || stat -f%z "$dest" 2>/dev/null || echo "0")
    if [ "$FILESIZE" -lt 1000000 ]; then
        echo "========================================================================="
        echo "WARNING: The downloaded file $dest is surprisingly small ($FILESIZE bytes)."
        echo "This usually means the URL returned an HTML page (like a login or view page)"
        echo "instead of the actual raw file data."
        echo "Please ensure you are providing a DIRECT download link."
        echo "========================================================================="
    fi
}

# 3. Download the large artifact files if URLs are provided
if [ -n "$PARQUET_URL" ]; then
    echo "Downloading candidate_features.parquet..."
    download_file "$PARQUET_URL" "artifacts/candidate_features.parquet"
else
    echo "Warning: PARQUET_URL environment variable is not set."
fi

if [ -n "$EMBEDDINGS_URL" ]; then
    echo "Downloading embeddings.npy..."
    download_file "$EMBEDDINGS_URL" "artifacts/embeddings.npy"
else
    echo "Warning: EMBEDDINGS_URL environment variable is not set."
fi

echo "Build complete."
