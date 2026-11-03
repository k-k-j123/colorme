import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "127.0.0.1")
    print(f"\n✨ ColorMe AI Wardrobe Stylist running at http://{host}:{port}\n")
    uvicorn.run("backend.app:app", host=host, port=port, reload=True)

