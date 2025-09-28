from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from datetime import datetime
import json
import uuid
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import sqlite3
import os

app = Flask(__name__)
CORS(app)

# Database setup
def init_db():
    conn = sqlite3.connect('carbon_marketplace.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            balance REAL NOT NULL,
            retired_credits INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Projects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            project_type TEXT NOT NULL,
            location TEXT NOT NULL,
            available_credits INTEGER NOT NULL,
            price_per_credit REAL NOT NULL,
            verification_standard TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Portfolio table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            credits INTEGER NOT NULL,
            avg_purchase_price REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (project_id) REFERENCES projects (id),
            UNIQUE(user_id, project_id)
        )
    ''')
    
    # Transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            project_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price_per_credit REAL NOT NULL,
            total_amount REAL NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (project_id) REFERENCES projects (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Data models
@dataclass
class User:
    id: str
    name: str
    balance: float
    retired_credits: int = 0

@dataclass
class Project:
    id: str
    name: str
    project_type: str
    location: str
    available_credits: int
    price_per_credit: float
    verification_standard: str
    description: str

@dataclass
class Transaction:
    id: str
    user_id: str
    project_id: str
    transaction_type: str
    quantity: int
    price_per_credit: float
    total_amount: float
    timestamp: str

class CarbonMarketplace:
    def __init__(self):
        self.db_name = 'carbon_marketplace.db'
        init_db()
        self.seed_initial_data()
    
    def get_db_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def seed_initial_data(self):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] > 0:
            conn.close()
            return
        
        # Seed users
        users_data = [
            ('user1', 'GreenCorp Inc.', 100000.00, 30),
            ('user2', 'EcoStart Ltd.', 50000.00, 12),
            ('user3', 'Sustainable Dynamics', 75000.00, 18),
            ('user4', 'Carbon Neutral Co.', 120000.00, 25)
        ]
        
        cursor.executemany(
            "INSERT INTO users (id, name, balance, retired_credits) VALUES (?, ?, ?, ?)",
            users_data
        )
        
        # Seed projects
        projects_data = [
            ('proj1', 'Amazon Reforestation', 'Forestry', 'Brazil', 10000, 42.50, 'VCS', 
             'Large-scale reforestation project in the Amazon rainforest protecting biodiversity'),
            ('proj2', 'Wind Power Texas', 'Renewable Energy', 'USA', 15000, 38.75, 'Gold Standard',
             'Wind farm generating clean electricity and displacing fossil fuels'),
            ('proj3', 'Methane Capture', 'Waste Management', 'Germany', 8000, 52.30, 'VCS',
             'Landfill methane capture preventing potent greenhouse gas emissions'),
            ('proj4', 'Solar Farm India', 'Renewable Energy', 'India', 12000, 35.60, 'CDM',
             'Utility-scale solar installation providing clean energy access'),
            ('proj5', 'Ocean Cleanup', 'Nature-based', 'Pacific Ocean', 5000, 65.80, 'Blue Carbon',
             'Marine ecosystem restoration and plastic removal project'),
            ('proj6', 'Forest Conservation', 'REDD+', 'Indonesia', 20000, 28.90, 'VCS',
             'Avoided deforestation protecting tropical forest ecosystems'),
            ('proj7', 'Biogas Project', 'Renewable Energy', 'Kenya', 6000, 41.20, 'Gold Standard',
             'Community biogas systems from organic waste'),
            ('proj8', 'Geothermal Energy', 'Renewable Energy', 'Iceland', 18000, 44.70, 'VCS',
             'Geothermal power plant utilizing natural earth heat'),
            ('proj9', 'Soil Carbon', 'Agriculture', 'Australia', 9000, 39.40, 'ACCUs',
             'Regenerative farming practices sequestering carbon in soil')
        ]
        
        cursor.executemany(
            """INSERT INTO projects (id, name, project_type, location, available_credits, 
               price_per_credit, verification_standard, description) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            projects_data
        )
        
        # Seed some initial portfolio holdings
        portfolio_data = [
            ('port1', 'user1', 'proj1', 25, 42.50),
            ('port2', 'user1', 'proj2', 15, 38.75),
            ('port3', 'user1', 'proj3', 10, 52.30),
            ('port4', 'user2', 'proj4', 20, 35.60),
            ('port5', 'user2', 'proj5', 8, 65.80),
            ('port6', 'user3', 'proj6', 18, 28.90),
            ('port7', 'user3', 'proj7', 22, 41.20),
            ('port8', 'user4', 'proj8', 30, 44.70),
            ('port9', 'user4', 'proj9', 15, 39.40)
        ]
        
        cursor.executemany(
            """INSERT INTO portfolio (id, user_id, project_id, credits, avg_purchase_price) 
               VALUES (?, ?, ?, ?, ?)""",
            portfolio_data
        )
        
        conn.commit()
        conn.close()

# Initialize marketplace
marketplace = CarbonMarketplace()

# API Routes
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = marketplace.get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return jsonify([dict(row) for row in users])

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    conn = marketplace.get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user:
        return jsonify(dict(user))
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/projects', methods=['GET'])
def get_projects():
    conn = marketplace.get_db_connection()
    projects = conn.execute('SELECT * FROM projects').fetchall()
    conn.close()
    return jsonify([dict(row) for row in projects])

@app.route('/api/portfolio/<user_id>', methods=['GET'])
def get_user_portfolio(user_id):
    conn = marketplace.get_db_connection()
    portfolio = conn.execute('''
        SELECT p.*, pr.name as project_name, pr.project_type, pr.price_per_credit as current_price
        FROM portfolio p
        JOIN projects pr ON p.project_id = pr.id
        WHERE p.user_id = ?
    ''', (user_id,)).fetchall()
    conn.close()
    return jsonify([dict(row) for row in portfolio])

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    user_id = request.args.get('user_id')
    limit = request.args.get('limit', 50)
    
    conn = marketplace.get_db_connection()
    
    query = '''
        SELECT t.*, u.name as user_name, p.name as project_name
        FROM transactions t
        JOIN users u ON t.user_id = u.id
        JOIN projects p ON t.project_id = p.id
    '''
    params = []
    
    if user_id:
        query += ' WHERE t.user_id = ?'
        params.append(user_id)
    
    query += ' ORDER BY t.timestamp DESC LIMIT ?'
    params.append(limit)
    
    transactions = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([dict(row) for row in transactions])

@app.route('/api/buy', methods=['POST'])
def buy_credits():
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    quantity = data.get('quantity')
    
    if not all([user_id, project_id, quantity]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = marketplace.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get user and project info
        user = cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        project = cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,)).fetchone()
        
        if not user or not project:
            return jsonify({'error': 'User or project not found'}), 404
        
        total_cost = quantity * project['price_per_credit']
        
        # Check balance and availability
        if user['balance'] < total_cost:
            return jsonify({'error': 'Insufficient balance'}), 400
        
        if project['available_credits'] < quantity:
            return jsonify({'error': 'Not enough credits available'}), 400
        
        # Update user balance
        cursor.execute(
            'UPDATE users SET balance = balance - ? WHERE id = ?',
            (total_cost, user_id)
        )
        
        # Update project availability
        cursor.execute(
            'UPDATE projects SET available_credits = available_credits - ? WHERE id = ?',
            (quantity, project_id)
        )
        
        # Update or create portfolio entry
        existing_portfolio = cursor.execute(
            'SELECT * FROM portfolio WHERE user_id = ? AND project_id = ?',
            (user_id, project_id)
        ).fetchone()
        
        if existing_portfolio:
            # Calculate new average price
            old_total = existing_portfolio['credits'] * existing_portfolio['avg_purchase_price']
            new_total = old_total + total_cost
            new_credits = existing_portfolio['credits'] + quantity
            new_avg_price = new_total / new_credits
            
            cursor.execute(
                'UPDATE portfolio SET credits = ?, avg_purchase_price = ? WHERE user_id = ? AND project_id = ?',
                (new_credits, new_avg_price, user_id, project_id)
            )
        else:
            portfolio_id = str(uuid.uuid4())
            cursor.execute(
                'INSERT INTO portfolio (id, user_id, project_id, credits, avg_purchase_price) VALUES (?, ?, ?, ?, ?)',
                (portfolio_id, user_id, project_id, quantity, project['price_per_credit'])
            )
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        cursor.execute(
            '''INSERT INTO transactions (id, user_id, project_id, transaction_type, quantity, 
               price_per_credit, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (transaction_id, user_id, project_id, 'BUY', quantity, project['price_per_credit'], total_cost)
        )
        
        conn.commit()
        return jsonify({
            'message': 'Purchase successful',
            'transaction_id': transaction_id,
            'total_cost': total_cost
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@app.route('/api/sell', methods=['POST'])
def sell_credits():
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    quantity = data.get('quantity')
    price_per_credit = data.get('price_per_credit')
    
    if not all([user_id, project_id, quantity, price_per_credit]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = marketplace.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check portfolio
        portfolio = cursor.execute(
            'SELECT * FROM portfolio WHERE user_id = ? AND project_id = ?',
            (user_id, project_id)
        ).fetchone()
        
        if not portfolio or portfolio['credits'] < quantity:
            return jsonify({'error': 'Insufficient credits in portfolio'}), 400
        
        total_revenue = quantity * price_per_credit
        
        # Update user balance
        cursor.execute(
            'UPDATE users SET balance = balance + ? WHERE id = ?',
            (total_revenue, user_id)
        )
        
        # Update portfolio
        new_credits = portfolio['credits'] - quantity
        if new_credits == 0:
            cursor.execute(
                'DELETE FROM portfolio WHERE user_id = ? AND project_id = ?',
                (user_id, project_id)
            )
        else:
            cursor.execute(
                'UPDATE portfolio SET credits = ? WHERE user_id = ? AND project_id = ?',
                (new_credits, user_id, project_id)
            )
        
        # Update project availability
        cursor.execute(
            'UPDATE projects SET available_credits = available_credits + ? WHERE id = ?',
            (quantity, project_id)
        )
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        cursor.execute(
            '''INSERT INTO transactions (id, user_id, project_id, transaction_type, quantity, 
               price_per_credit, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (transaction_id, user_id, project_id, 'SELL', quantity, price_per_credit, total_revenue)
        )
        
        conn.commit()
        return jsonify({
            'message': 'Sale successful',
            'transaction_id': transaction_id,
            'total_revenue': total_revenue
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@app.route('/api/retire', methods=['POST'])
def retire_credits():
    data = request.json
    user_id = data.get('user_id')
    project_id = data.get('project_id')
    quantity = data.get('quantity')
    
    if not all([user_id, project_id, quantity]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    conn = marketplace.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check portfolio
        portfolio = cursor.execute(
            'SELECT * FROM portfolio WHERE user_id = ? AND project_id = ?',
            (user_id, project_id)
        ).fetchone()
        
        if not portfolio or portfolio['credits'] < quantity:
            return jsonify({'error': 'Insufficient credits in portfolio'}), 400
        
        # Update portfolio
        new_credits = portfolio['credits'] - quantity
        if new_credits == 0:
            cursor.execute(
                'DELETE FROM portfolio WHERE user_id = ? AND project_id = ?',
                (user_id, project_id)
            )
        else:
            cursor.execute(
                'UPDATE portfolio SET credits = ? WHERE user_id = ? AND project_id = ?',
                (new_credits, user_id, project_id)
            )
        
        # Update user's retired credits
        cursor.execute(
            'UPDATE users SET retired_credits = retired_credits + ? WHERE id = ?',
            (quantity, user_id)
        )
        
        # Record transaction
        transaction_id = str(uuid.uuid4())
        cursor.execute(
            '''INSERT INTO transactions (id, user_id, project_id, transaction_type, quantity, 
               price_per_credit, total_amount) VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (transaction_id, user_id, project_id, 'RETIRE', quantity, 0, 0)
        )
        
        conn.commit()
        return jsonify({
            'message': 'Credits retired successfully',
            'transaction_id': transaction_id,
            'co2_offset': f'{quantity} tons'
        })
        
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    
    finally:
        conn.close()

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    conn = marketplace.get_db_connection()
    
    # Market analytics
    total_trades = conn.execute('SELECT COUNT(*) as count FROM transactions WHERE transaction_type != "RETIRE"').fetchone()['count']
    total_volume = conn.execute('SELECT COALESCE(SUM(quantity), 0) as volume FROM transactions WHERE transaction_type != "RETIRE"').fetchone()['volume']
    avg_price = conn.execute('SELECT COALESCE(AVG(price_per_credit), 0) as avg FROM transactions WHERE transaction_type != "RETIRE"').fetchone()['avg']
    total_retired = conn.execute('SELECT COALESCE(SUM(retired_credits), 0) as retired FROM users').fetchone()['retired']
    
    # Project type distribution
    project_types = conn.execute('''
        SELECT project_type, COUNT(*) as count, SUM(available_credits) as total_credits
        FROM projects 
        GROUP BY project_type
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'market_stats': {
            'total_trades': total_trades,
            'total_volume': total_volume,
            'avg_price': round(avg_price, 2),
            'total_retired': total_retired
        },
        'project_distribution': [dict(row) for row in project_types]
    })

@app.route('/')
def index():
    return """
    <h1>Carbon Marketplace API</h1>
    <p>Backend API for Carbon Offset Trading Platform</p>
    <h2>Available Endpoints:</h2>
    <ul>
        <li>GET /api/users - List all users</li>
        <li>GET /api/users/{user_id} - Get user details</li>
        <li>GET /api/projects - List all projects</li>
        <li>GET /api/portfolio/{user_id} - Get user portfolio</li>
        <li>GET /api/transactions - Get transaction history</li>
        <li>POST /api/buy - Buy carbon credits</li>
        <li>POST /api/sell - Sell carbon credits</li>
        <li>POST /api/retire - Retire carbon credits</li>
        <li>GET /api/analytics - Get market analytics</li>
    </ul>
    """

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
