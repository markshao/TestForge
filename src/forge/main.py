import uvicorn
from forge.api import app

def main():
    print("Starting TestForge API Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
