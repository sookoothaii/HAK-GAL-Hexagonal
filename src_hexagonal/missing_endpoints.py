"""
HAK-GAL Missing Endpoints Implementation
=========================================
Implements the missing endpoints that were causing 405 errors:
- /api/system/gpu
- /api/mojo/status  
- /api/metrics
- /api/limits
- /api/graph/emergency-status
"""

from flask import jsonify, request
import psutil
import time
import os
from pathlib import Path
import json
import subprocess

def register_missing_endpoints(app, fact_repository=None, reasoning_engine=None):
    """Register all missing endpoints that were causing 405 errors"""
    
    @app.route('/api/system/gpu', methods=['GET', 'OPTIONS'])
    def system_gpu():
        """GPU monitoring endpoint"""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        try:
            # Try to detect GPU using different methods
            gpu_info = {
                'available': False,
                'driver': 'Not detected',
                'devices': [],
                'cuda_available': False,
                'memory': {
                    'total': 0,
                    'used': 0,
                    'free': 0
                }
            }
            
            # Check for NVIDIA GPU using nvidia-smi
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free', 
                                       '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        parts = line.split(',')
                        if len(parts) >= 4:
                            gpu_info['available'] = True
                            gpu_info['driver'] = 'NVIDIA'
                            gpu_info['devices'].append({
                                'name': parts[0].strip(),
                                'memory_total': int(parts[1].strip()),
                                'memory_used': int(parts[2].strip()),
                                'memory_free': int(parts[3].strip())
                            })
                            gpu_info['memory']['total'] += int(parts[1].strip())
                            gpu_info['memory']['used'] += int(parts[2].strip())
                            gpu_info['memory']['free'] += int(parts[3].strip())
            except Exception:
                pass
            
            # Check for CUDA availability
            try:
                import torch
                gpu_info['cuda_available'] = torch.cuda.is_available()
                if gpu_info['cuda_available']:
                    gpu_info['cuda_devices'] = torch.cuda.device_count()
                    gpu_info['cuda_version'] = torch.version.cuda
            except ImportError:
                pass
            
            # If no GPU detected, return basic info
            if not gpu_info['available']:
                gpu_info['message'] = 'No GPU detected or GPU monitoring not available'
            
            return jsonify(gpu_info)
            
        except Exception as e:
            return jsonify({
                'available': False,
                'error': str(e),
                'message': 'GPU monitoring not available'
            })
    
    @app.route('/api/mojo/status', methods=['GET', 'OPTIONS'])
    def mojo_status():
        """Mojo integration status endpoint"""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        # Check if Mojo kernels are available
        mojo_info = {
            'enabled': False,
            'version': None,
            'kernels': [],
            'performance_boost': 0,
            'status': 'Not configured',
            'message': 'Mojo integration not active'
        }
        
        # Check if mojo_kernels.py exists and is enabled
        mojo_path = Path(__file__).parent / 'mojo_kernels.py.DISABLED'
        if mojo_path.exists():
            mojo_info['status'] = 'Disabled (file exists but renamed)'
            mojo_info['message'] = 'Mojo kernels file found but disabled'
        
        # Check for active Mojo module
        try:
            import mojo_kernels
            mojo_info['enabled'] = True
            mojo_info['status'] = 'Active'
            mojo_info['version'] = getattr(mojo_kernels, '__version__', '1.0')
            mojo_info['kernels'] = getattr(mojo_kernels, 'available_kernels', [])
            mojo_info['performance_boost'] = 250  # Claimed 250x boost
            mojo_info['message'] = 'Mojo kernels loaded and operational'
        except ImportError:
            pass
        
        return jsonify(mojo_info)
    
    @app.route('/api/metrics', methods=['GET', 'OPTIONS'])
    def system_metrics():
        """Detailed system metrics endpoint"""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        try:
            # Collect comprehensive system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process metrics
            process = psutil.Process()
            process_info = {
                'pid': process.pid,
                'memory_mb': process.memory_info().rss / 1024 / 1024,
                'cpu_percent': process.cpu_percent(interval=0.1),
                'threads': process.num_threads(),
                'open_files': len(process.open_files()),
                'connections': len(process.connections())
            }
            
            # Knowledge base metrics
            kb_metrics = {}
            if fact_repository:
                try:
                    kb_metrics = {
                        'total_facts': fact_repository.count(),
                        'repository_type': fact_repository.__class__.__name__,
                        'database_size_mb': 0
                    }
                    
                    # Try to get database file size
                    db_path = Path(__file__).parent.parent / 'hexagonal_kb.db'
                    if db_path.exists():
                        kb_metrics['database_size_mb'] = db_path.stat().st_size / 1024 / 1024
                except Exception:
                    pass
            
            # Network metrics
            net_io = psutil.net_io_counters()
            network_metrics = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout
            }
            
            return jsonify({
                'timestamp': time.time(),
                'system': {
                    'cpu_percent': cpu_percent,
                    'cpu_count': psutil.cpu_count(),
                    'memory': {
                        'total_mb': memory.total / 1024 / 1024,
                        'available_mb': memory.available / 1024 / 1024,
                        'used_mb': memory.used / 1024 / 1024,
                        'percent': memory.percent
                    },
                    'disk': {
                        'total_gb': disk.total / 1024 / 1024 / 1024,
                        'used_gb': disk.used / 1024 / 1024 / 1024,
                        'free_gb': disk.free / 1024 / 1024 / 1024,
                        'percent': disk.percent
                    }
                },
                'process': process_info,
                'knowledge_base': kb_metrics,
                'network': network_metrics,
                'uptime_seconds': time.time() - process.create_time()
            })
            
        except Exception as e:
            return jsonify({
                'error': str(e),
                'message': 'Failed to collect system metrics'
            }), 500
    
    @app.route('/api/limits', methods=['GET', 'OPTIONS'])
    def system_limits():
        """System limits and constraints endpoint"""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        try:
            import resource
            
            # Get system resource limits
            limits = {}
            
            # Define limit names
            limit_names = {
                resource.RLIMIT_CPU: 'cpu_time',
                resource.RLIMIT_FSIZE: 'file_size',
                resource.RLIMIT_DATA: 'data_segment',
                resource.RLIMIT_STACK: 'stack_size',
                resource.RLIMIT_CORE: 'core_file',
                resource.RLIMIT_RSS: 'resident_set',
                resource.RLIMIT_NPROC: 'processes',
                resource.RLIMIT_NOFILE: 'open_files',
                resource.RLIMIT_MEMLOCK: 'locked_memory',
                resource.RLIMIT_AS: 'address_space'
            }
            
            for limit_id, name in limit_names.items():
                try:
                    soft, hard = resource.getrlimit(limit_id)
                    limits[name] = {
                        'soft': soft if soft != resource.RLIM_INFINITY else 'unlimited',
                        'hard': hard if hard != resource.RLIM_INFINITY else 'unlimited'
                    }
                except Exception:
                    limits[name] = {'soft': 'unknown', 'hard': 'unknown'}
            
            # Application-specific limits
            app_limits = {
                'max_facts': 1000000,  # Maximum facts in knowledge base
                'max_query_length': 10000,  # Maximum query string length
                'max_reasoning_depth': 10,  # Maximum reasoning recursion depth
                'max_websocket_clients': 100,  # Maximum concurrent WebSocket connections
                'max_file_upload_mb': 100,  # Maximum file upload size
                'rate_limit_per_minute': 600,  # API rate limit
                'cache_ttl_seconds': 30,  # Cache time-to-live
                'session_timeout_minutes': 60  # Session timeout
            }
            
            # Knowledge base limits
            kb_limits = {}
            if fact_repository:
                try:
                    current_count = fact_repository.count()
                    kb_limits = {
                        'current_facts': current_count,
                        'max_facts': app_limits['max_facts'],
                        'usage_percent': round((current_count / app_limits['max_facts']) * 100, 2),
                        'remaining_capacity': app_limits['max_facts'] - current_count
                    }
                except Exception:
                    pass
            
            return jsonify({
                'system_limits': limits,
                'application_limits': app_limits,
                'knowledge_base_limits': kb_limits,
                'timestamp': time.time()
            })
            
        except ImportError:
            # Fallback for Windows or systems without resource module
            return jsonify({
                'system_limits': {
                    'message': 'System limits not available on this platform'
                },
                'application_limits': {
                    'max_facts': 1000000,
                    'max_query_length': 10000,
                    'max_reasoning_depth': 10,
                    'max_websocket_clients': 100,
                    'max_file_upload_mb': 100,
                    'rate_limit_per_minute': 600,
                    'cache_ttl_seconds': 30,
                    'session_timeout_minutes': 60
                },
                'knowledge_base_limits': {},
                'timestamp': time.time()
            })
    
    @app.route('/api/graph/emergency-status', methods=['GET', 'OPTIONS'])
    def graph_emergency_status():
        """Graph database emergency status endpoint"""
        if request.method == 'OPTIONS':
            return ('', 204)
        
        # Check for graph database components
        graph_status = {
            'operational': False,
            'database': 'Not configured',
            'status': 'OFFLINE',
            'nodes': 0,
            'edges': 0,
            'last_update': None,
            'emergency_mode': False,
            'message': 'Graph database not active',
            'components': {
                'neo4j': False,
                'redis_graph': False,
                'networkx': False,
                'custom_graph': False
            }
        }
        
        # Check for Neo4j
        try:
            from neo4j import GraphDatabase
            graph_status['components']['neo4j'] = True
            # Could attempt connection here if configured
        except ImportError:
            pass
        
        # Check for RedisGraph
        try:
            import redisgraph
            graph_status['components']['redis_graph'] = True
        except ImportError:
            pass
        
        # Check for NetworkX (in-memory graph)
        try:
            import networkx as nx
            graph_status['components']['networkx'] = True
            
            # If NetworkX is available, we could maintain an in-memory graph
            # For now, just report it's available
            graph_status['operational'] = True
            graph_status['database'] = 'NetworkX (in-memory)'
            graph_status['status'] = 'READY'
            graph_status['message'] = 'In-memory graph capabilities available'
            
        except ImportError:
            pass
        
        # Check for custom graph implementation
        graph_path = Path(__file__).parent / 'graph_adapter.py'
        if graph_path.exists():
            graph_status['components']['custom_graph'] = True
            graph_status['message'] = 'Custom graph adapter found but not loaded'
        
        # Emergency mode detection
        # This would be triggered by high memory usage or system issues
        try:
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                graph_status['emergency_mode'] = True
                graph_status['message'] = 'Emergency mode: High memory usage detected'
        except Exception:
            pass
        
        # If we have a fact repository, we could build graph metrics
        if fact_repository and graph_status['components']['networkx']:
            try:
                import networkx as nx
                # Build a simple graph from facts
                G = nx.DiGraph()
                
                # Try different methods to get facts
                facts = []
                try:
                    # Try direct method first
                    if hasattr(fact_repository, 'get_all'):
                        facts = fact_repository.get_all(limit=1000)
                    elif hasattr(fact_repository, 'get_paginated'):
                        facts = fact_repository.get_paginated(0, 1000)
                    else:
                        # Fall back to getting count and basic iteration
                        count = fact_repository.count() if hasattr(fact_repository, 'count') else 0
                        if count > 0 and hasattr(fact_repository, '__iter__'):
                            facts = list(fact_repository)[:1000]
                except Exception:
                    facts = []
                
                for fact in facts:
                    statement = fact.statement if hasattr(fact, 'statement') else str(fact)
                    if '(' in statement and ')' in statement:
                        pred = statement.split('(')[0]
                        args = statement.split('(')[1].split(')')[0]
                        if ',' in args:
                            e1, e2 = args.split(',', 1)
                            G.add_edge(e1.strip(), e2.strip(), predicate=pred)
                
                graph_status['nodes'] = G.number_of_nodes()
                graph_status['edges'] = G.number_of_edges()
                graph_status['last_update'] = time.time()
                
            except Exception as e:
                graph_status['message'] = f'Graph metrics unavailable: {str(e)}'
        
        return jsonify(graph_status)
    
    print("[OK] Missing endpoints registered:")
    print("  - GET /api/system/gpu")
    print("  - GET /api/mojo/status")
    print("  - GET /api/metrics")
    print("  - GET /api/limits")
    print("  - GET /api/graph/emergency-status")
