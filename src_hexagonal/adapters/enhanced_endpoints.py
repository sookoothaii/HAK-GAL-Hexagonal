"""
Enhanced API Endpoints - Pagination & Bulk Operations
======================================================
Quick wins for better API performance
"""

from flask import Blueprint, jsonify, request
from typing import List, Dict, Any
import sqlite3
from pathlib import Path
from datetime import datetime

# Create Blueprint for enhanced endpoints
enhanced_api = Blueprint('enhanced_api', __name__)

class EnhancedEndpoints:
    """Additional API endpoints for better functionality"""
    
    def __init__(self, db_path='k_assistant_dev.db'):
        self.db_path = db_path
    
    def register_routes(self, app):
        """Register enhanced routes with the Flask app"""
        
        @app.route('/api/facts/paginated', methods=['GET'])
        def get_facts_paginated():
            """GET /api/facts/paginated - Paginated facts"""
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            search = request.args.get('search', '', type=str)
            
            # Limit per_page to prevent abuse
            per_page = min(per_page, 200)
            offset = (page - 1) * per_page
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Count total
                    if search:
                        count_query = "SELECT COUNT(*) FROM facts WHERE statement LIKE ?"
                        cursor = conn.execute(count_query, (f'%{search}%',))
                    else:
                        cursor = conn.execute("SELECT COUNT(*) FROM facts")
                    total = cursor.fetchone()[0]
                    
                    # Get page of facts
                    if search:
                        query = """
                            SELECT id, statement, confidence, source, created_at 
                            FROM facts 
                            WHERE statement LIKE ?
                            ORDER BY id DESC 
                            LIMIT ? OFFSET ?
                        """
                        cursor = conn.execute(query, (f'%{search}%', per_page, offset))
                    else:
                        query = """
                            SELECT id, statement, confidence, source, created_at 
                            FROM facts 
                            ORDER BY id DESC 
                            LIMIT ? OFFSET ?
                        """
                        cursor = conn.execute(query, (per_page, offset))
                    
                    facts = []
                    for row in cursor:
                        facts.append({
                            'id': row[0],
                            'statement': row[1],
                            'confidence': row[2],
                            'source': row[3],
                            'created_at': row[4]
                        })
                    
                    # Calculate pagination info
                    total_pages = (total + per_page - 1) // per_page
                    
                    return jsonify({
                        'facts': facts,
                        'pagination': {
                            'page': page,
                            'per_page': per_page,
                            'total': total,
                            'total_pages': total_pages,
                            'has_next': page < total_pages,
                            'has_prev': page > 1
                        }
                    })
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/facts/bulk', methods=['POST'])
        def bulk_add_facts():
            """POST /api/facts/bulk - Add multiple facts"""
            data = request.get_json()
            
            if not data or 'facts' not in data:
                return jsonify({'error': 'Missing facts array'}), 400
            
            facts_to_add = data['facts']
            if not isinstance(facts_to_add, list):
                return jsonify({'error': 'Facts must be an array'}), 400
            
            added = 0
            errors = []
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    for fact in facts_to_add:
                        try:
                            statement = fact.get('statement', '')
                            if not statement:
                                errors.append({'fact': fact, 'error': 'Missing statement'})
                                continue
                            
                            # Clean statement
                            if not statement.endswith('.'):
                                statement += '.'
                            
                            confidence = fact.get('confidence', 1.0)
                            source = fact.get('source', 'bulk_import')
                            
                            conn.execute("""
                                INSERT INTO facts (statement, confidence, source)
                                VALUES (?, ?, ?)
                            """, (statement, confidence, source))
                            added += 1
                            
                        except sqlite3.IntegrityError:
                            errors.append({'fact': fact, 'error': 'Duplicate'})
                        except Exception as e:
                            errors.append({'fact': fact, 'error': str(e)})
                    
                    conn.commit()
                    
                return jsonify({
                    'success': True,
                    'added': added,
                    'errors': errors,
                    'total': len(facts_to_add)
                }), 201
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/facts/bulk/delete', methods=['POST'])
        def bulk_delete_facts():
            """POST /api/facts/bulk/delete - Delete multiple facts"""
            data = request.get_json()
            
            if not data or 'statements' not in data:
                return jsonify({'error': 'Missing statements array'}), 400
            
            statements = data['statements']
            if not isinstance(statements, list):
                return jsonify({'error': 'Statements must be an array'}), 400
            
            deleted = 0
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    for statement in statements:
                        result = conn.execute(
                            "DELETE FROM facts WHERE statement = ?",
                            (statement,)
                        )
                        deleted += result.rowcount
                    
                    conn.commit()
                    
                return jsonify({
                    'success': True,
                    'deleted': deleted,
                    'requested': len(statements)
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/facts/stats', methods=['GET'])
        def get_facts_stats():
            """GET /api/facts/stats - Database statistics"""
            try:
                with sqlite3.connect(self.db_path) as conn:
                    # Total facts
                    cursor = conn.execute("SELECT COUNT(*) FROM facts")
                    total = cursor.fetchone()[0]
                    
                    # Unique sources
                    cursor = conn.execute("SELECT COUNT(DISTINCT source) FROM facts")
                    sources = cursor.fetchone()[0]
                    
                    # Average confidence
                    cursor = conn.execute("SELECT AVG(confidence) FROM facts")
                    avg_confidence = cursor.fetchone()[0] or 0
                    
                    # Facts by source
                    cursor = conn.execute("""
                        SELECT source, COUNT(*) as count 
                        FROM facts 
                        GROUP BY source 
                        ORDER BY count DESC 
                        LIMIT 10
                    """)
                    top_sources = []
                    for row in cursor:
                        top_sources.append({
                            'source': row[0],
                            'count': row[1]
                        })
                    
                    # Recent activity (last 24h, 7d, 30d)
                    cursor = conn.execute("""
                        SELECT 
                            SUM(CASE WHEN datetime(created_at) > datetime('now', '-1 day') THEN 1 ELSE 0 END) as last_24h,
                            SUM(CASE WHEN datetime(created_at) > datetime('now', '-7 days') THEN 1 ELSE 0 END) as last_7d,
                            SUM(CASE WHEN datetime(created_at) > datetime('now', '-30 days') THEN 1 ELSE 0 END) as last_30d
                        FROM facts
                    """)
                    activity = cursor.fetchone()
                    
                    return jsonify({
                        'total_facts': total,
                        'unique_sources': sources,
                        'average_confidence': round(avg_confidence, 3),
                        'top_sources': top_sources,
                        'activity': {
                            'last_24h': activity[0] or 0,
                            'last_7d': activity[1] or 0,
                            'last_30d': activity[2] or 0
                        }
                    })
                    
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @app.route('/api/facts/export', methods=['GET'])
        def export_facts():
            """GET /api/facts/export - Export facts as JSON"""
            format = request.args.get('format', 'json')
            limit = request.args.get('limit', 0, type=int)
            
            try:
                with sqlite3.connect(self.db_path) as conn:
                    if limit > 0:
                        query = "SELECT * FROM facts LIMIT ?"
                        cursor = conn.execute(query, (limit,))
                    else:
                        cursor = conn.execute("SELECT * FROM facts")
                    
                    facts = []
                    for row in cursor:
                        facts.append({
                            'id': row[0],
                            'statement': row[1],
                            'confidence': row[2],
                            'source': row[3],
                            'created_at': row[4],
                            'metadata': row[5] if len(row) > 5 else None
                        })
                    
                    if format == 'jsonl':
                        # Return as JSONL (newline-delimited JSON)
                        import json
                        lines = [json.dumps(fact) for fact in facts]
                        return '\n'.join(lines), 200, {'Content-Type': 'application/x-ndjson'}
                    else:
                        # Return as regular JSON
                        return jsonify({
                            'facts': facts,
                            'count': len(facts),
                            'exported_at': datetime.now().isoformat()
                        })
                        
            except Exception as e:
                return jsonify({'error': str(e)}), 500

# Usage: Import this in your main API file and register the endpoints
# from enhanced_endpoints import EnhancedEndpoints
# enhanced = EnhancedEndpoints()
# enhanced.register_routes(app)
