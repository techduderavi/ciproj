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

def debug_file_access():
    """Debug function to check file access permissions"""
    try:
        print(f"Current working directory: {os.getcwd()}")
        print(f"Directory listing: {os.listdir('.')}")
        print(f"Data directory exists: {os.path.exists('data')}")
        if os.path.exists('data'):
            print(f"Data directory contents: {os.listdir('data')}")
        print(f"Database file exists: {os.path.exists('data/database.db')}")
    except Exception as e:
        print(f"Debug error: {e}")

# Call this function before initializing the database
debug_file_access()

# Initialize LaunchDarkly client (use your SDK key or a dummy one for testing)
ld_sdk_key = os.environ.get("LD_SDK_KEY", "sdk-key-123")
ldclient.set_config(Config(ld_sdk_key))
ld_client = ldclient.get()

# Initialize SQLite database
def get_db_connection():
    db_path = os.path.join('data', 'database.db')
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if they don't exist
def init_db():
    # Ensure the data directory exists
    os.makedirs('data', exist_ok=True)
    
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

# READ - Get all items
@app.route('/api/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return jsonify([dict(item) for item in items])

# READ - Get a specific item
@app.route('/api/items/<item_id>', methods=['GET'])
def get_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    conn.close()
    
    if item is None:
        return jsonify({"error": "Item not found"}), 404
    
    return jsonify(dict(item))

# CREATE - Add a new item
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

# UPDATE - Update an existing item
@app.route('/api/items/<item_id>', methods=['PUT'])
@feature_flag('enable-write-operations', default=True)
def update_item(item_id):
    data = request.json
    
    if not data or 'content' not in data:
        return jsonify({"error": "Content field is required"}), 400
    
    conn = get_db_connection()
    
    # Check if item exists
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if item is None:
        conn.close()
        return jsonify({"error": "Item not found"}), 404
    
    # Update the item
    conn.execute('UPDATE items SET content = ? WHERE id = ?',
                (data['content'], item_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': item_id,
        'content': data['content'],
        'created_at': dict(item)['created_at']
    })

# DELETE - Delete an item
@app.route('/api/items/<item_id>', methods=['DELETE'])
@feature_flag('enable-write-operations', default=True)
def delete_item(item_id):
    conn = get_db_connection()
    
    # Check if item exists
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if item is None:
        conn.close()
        return jsonify({"error": "Item not found"}), 404
    
    # Delete the item
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": f"Item {item_id} deleted successfully"})

@app.route('/api/experimental', methods=['GET'])
@feature_flag('experimental-endpoint', default=False)
def experimental():
    return jsonify({"message": "This is an experimental feature"})

@app.route('/health')
def health():
    # Health check endpoint for deployment verification
    return jsonify({"status": "healthy", "environment": os.environ.get('DEPLOYMENT_ENV', 'unknown')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
