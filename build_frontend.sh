#!/bin/bash

# Define paths relative to the current script location
FRONTEND_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/frontend
TEMPLATES_DIR=terno/frontend/templates/frontend
STATIC_DIR=terno/frontend/static

# Step 1: Run npm build inside frontend directory
echo "Step 1: Running npm build..."
npm --prefix $FRONTEND_DIR run build

# Step 2: Copy index.html to Django templates directory
echo "Step 2: Copying index.html to Django templates directory..."
cp $FRONTEND_DIR/dist/index.html $TEMPLATES_DIR/index.html

# Step 3: Remove all files in Django static directory
echo "Step 3: Removing all files in Django static directory..."
rm -rf $STATIC_DIR/*

# Step 4: Copy assets to Django static directory
echo "Step 4: Copying assets to Django static directory..."
cp -r $FRONTEND_DIR/dist/assets/* $STATIC_DIR

echo "Build process completed successfully!"