#!/bin/bash
# Keep Expo development server running with auto-restart

while true; do
    echo "Starting Expo development server..."
    npx expo start --tunnel --non-interactive
    
    echo "Expo server stopped. Restarting in 5 seconds..."
    sleep 5
done