import os
import sys

# Добавляем текущую директорию в пути поиска Python
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from planner import create_app

app = create_app()

if __name__ == "__main__":
    print("🚀 NANDA Backend is starting...")
    app.run(host='127.0.0.1', port=5001, debug=True)