# Analytics and Monitoring for YYS-SQR

import json
import sqlite3
from datetime import datetime, timedelta
import hashlib
from collections import defaultdict

class AnalyticsManager:
    """Track usage analytics and system performance"""
    
    def __init__(self, db_path="analytics.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                watermark_id TEXT,
                user_hash TEXT,
                metadata TEXT,
                success BOOLEAN,
                error_message TEXT
            )
        ''')
        
        # Performance metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                operation TEXT NOT NULL,
                duration_ms INTEGER,
                file_size_bytes INTEGER,
                success BOOLEAN
            )
        ''')
        
        # System stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage_percent REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_event(self, event_type, watermark_id=None, metadata=None, success=True, error_message=None):
        """Log an application event"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create anonymous user hash (privacy-preserving)
        user_hash = hashlib.sha256(f"user_{datetime.now().date()}".encode()).hexdigest()[:16]
        
        cursor.execute('''
            INSERT INTO events (event_type, watermark_id, user_hash, metadata, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (event_type, watermark_id, user_hash, json.dumps(metadata) if metadata else None, success, error_message))
        
        conn.commit()
        conn.close()
    
    def log_performance(self, operation, duration_ms, file_size_bytes=None, success=True):
        """Log performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO performance (operation, duration_ms, file_size_bytes, success)
            VALUES (?, ?, ?, ?)
        ''', (operation, duration_ms, file_size_bytes, success))
        
        conn.commit()
        conn.close()
    
    def get_usage_stats(self, days=30):
        """Get usage statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        # Event counts by type
        cursor.execute('''
            SELECT event_type, COUNT(*) as count, 
                   SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful
            FROM events 
            WHERE timestamp > ?
            GROUP BY event_type
        ''', (since_date,))
        
        event_stats = cursor.fetchall()
        
        # Performance averages
        cursor.execute('''
            SELECT operation, AVG(duration_ms) as avg_duration, COUNT(*) as count
            FROM performance 
            WHERE timestamp > ? AND success = 1
            GROUP BY operation
        ''', (since_date,))
        
        performance_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'events': event_stats,
            'performance': performance_stats,
            'period_days': days
        }
    
    def get_error_report(self, days=7):
        """Get error report for troubleshooting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since_date = datetime.now() - timedelta(days=days)
        
        cursor.execute('''
            SELECT event_type, error_message, COUNT(*) as count, MAX(timestamp) as last_occurrence
            FROM events 
            WHERE timestamp > ? AND success = 0
            GROUP BY event_type, error_message
            ORDER BY count DESC
        ''', (since_date,))
        
        errors = cursor.fetchall()
        conn.close()
        
        return errors
    
    def export_analytics(self, output_file="analytics_export.json"):
        """Export analytics data for analysis"""
        stats = self.get_usage_stats(90)  # 90 days
        errors = self.get_error_report(30)  # 30 days
        
        export_data = {
            'export_date': datetime.now().isoformat(),
            'usage_stats': stats,
            'error_report': errors
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        return output_file

class BlockchainMonitor:
    """Monitor blockchain transactions and contract events"""
    
    def __init__(self, web3_instance, contract_address):
        self.w3 = web3_instance
        self.contract_address = contract_address
        self.monitored_events = []
    
    def start_monitoring(self):
        """Start monitoring blockchain events"""
        # Implementation for event monitoring
        pass
    
    def get_transaction_status(self, tx_hash):
        """Get detailed transaction status"""
        try:
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            tx = self.w3.eth.get_transaction(tx_hash)
            
            return {
                'hash': tx_hash,
                'status': 'success' if tx_receipt.status == 1 else 'failed',
                'block_number': tx_receipt.blockNumber,
                'gas_used': tx_receipt.gasUsed,
                'gas_price': tx.gasPrice,
                'cost_eth': self.w3.from_wei(tx_receipt.gasUsed * tx.gasPrice, 'ether')
            }
        except Exception as e:
            return {'hash': tx_hash, 'status': 'error', 'error': str(e)}
    
    def get_contract_stats(self):
        """Get contract usage statistics"""
        # Implementation for contract statistics
        pass

class PerformanceProfiler:
    """Profile application performance"""
    
    def __init__(self):
        self.profiles = {}
    
    def start_profile(self, operation_name):
        """Start profiling an operation"""
        self.profiles[operation_name] = {
            'start_time': datetime.now(),
            'memory_start': self._get_memory_usage()
        }
    
    def end_profile(self, operation_name):
        """End profiling and return metrics"""
        if operation_name not in self.profiles:
            return None
        
        profile = self.profiles[operation_name]
        end_time = datetime.now()
        memory_end = self._get_memory_usage()
        
        duration_ms = (end_time - profile['start_time']).total_seconds() * 1000
        memory_delta = memory_end - profile['memory_start']
        
        del self.profiles[operation_name]
        
        return {
            'operation': operation_name,
            'duration_ms': duration_ms,
            'memory_delta_mb': memory_delta,
            'start_time': profile['start_time'],
            'end_time': end_time
        }
    
    def _get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            return 0  # psutil not available