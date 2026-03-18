#!/bin/bash
echo "=== ManufactureIQ — Starting ==="
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "✅ Backend started at http://localhost:8000"
echo "📚 API Docs at http://localhost:8000/docs"
echo ""
echo "To open frontend:"
echo "  Open frontend/index.html in your browser"
echo "  OR: cd ../frontend && python -m http.server 3000"
echo ""
echo "Press Ctrl+C to stop"
wait $BACKEND_PID
