from flask import Flask, render_template, jsonify, request
import os
import json
import uuid
from datetime import datetime
from functools import wraps
import sqlite3

# Feature flag client
import ldclient
from ldclient.config import Config

app = Flask(__name__)

# Initialize LaunchDarkly client (use your SDK key or a dummy one for testing)
ld_sdk_key = os.environ.get("LD_SDK_KEY", "sdk-key-123")
ldclient.set_config(Config(ld_sdk_key))
ld_client = ldclient.get()

# Initialize SQLite database
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
def init_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

init_db()

# Feature flag check decorator
def feature_flag(flag_name, default=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = {"key": request.remote_addr}
            # For local testing, you can override with environment variables
            if os.environ.get(f"ENABLE_{flag_name.upper()}", "false").lower() == "true":
                return f(*args, **kwargs)
            if ld_client.variation(flag_name, user, default):
                return f(*args, **kwargs)
            return jsonify({"error": "Feature not available"}), 403
        return decorated_function
    return decorator

@app.route('/')
def index():
    # Get deployment environment for blue/green display
    env = os.environ.get('DEPLOYMENT_ENV', 'blue')
    return render_template('index.html', env=env)

@app.route('/api/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])

@app.route('/api/items', methods=['POST'])
@feature_flag('enable-write-operations', default=True)
def add_item():
    data = request.json
    item_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()
    
    conn = get_db_connection()
    conn.execute('INSERT INTO items (id, content, created_at) VALUES (?, ?, ?)',
                (item_id, data.get('content', ''), created_at))
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': item_id,
        'content': data.get('content', ''),
        'created_at': created_at
    }), 201

@app.route('/api/experimental', methods=['GET'])
@feature_flag('experimental-endpoint', default=False)
def experimental():
    return jsonify({"message": "This is an experimental feature"})

@app.route('/health')
def health():
    # Health check endpoint for deployment verification
    #
    return jsonify({"status": "healthy", "environment": os.environ.get('DEPLOYMENT_ENV', 'unknown')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
