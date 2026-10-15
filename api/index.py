import sys
import os

# Ensure the root project directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wsgi import app

# Vercel Serverless Function entrypoint
if __name__ == "__main__":
    app.run()
