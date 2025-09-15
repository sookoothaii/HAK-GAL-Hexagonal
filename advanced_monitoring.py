#!/usr/bin/env python3
"""
HAK/GAL Advanced Monitoring Features
Enhanced monitoring with real-time alerts, anomaly detection, and predictive analytics
"""

import time
import json
import threading
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from hakgal_performance_monitor import HAKGALPerformanceMonitor
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Alert:
    timestamp: str
    severity: str  # 'info', 'warning', 'critical'
    category: str  # 'performance', 'security', 'system', 'ml'
    message: str
    metric_name: str
    current_value: float
    threshold_value: float
    recommendation: str
    resolved: bool = False

@dataclass
class Anomaly:
    timestamp: str
    metric_name: str
    value: float
    expected_value: float
    deviation: float
    confidence: float
    description: str

class AdvancedMonitoringSystem:
    def __init__(self, base_monitor: HAKGALPerformanceMonitor):
        self.base_monitor = base_monitor
        self.alerts: List[Alert] = []
        self.anomalies: List[Anomaly] = []
        self.alert_rules: Dict[str, Dict] = {}
        self.notification_config: Dict[str, Any] = {}
        self.running = False
        self.monitor_thread: Optional[threading.Thread] = None
        
        # Initialize default alert rules
        self._setup_default_alert_rules()
        
        # Initialize notification config
        self._setup_notification_config()
    
    def _setup_default_alert_rules(self):
        """Setup default alert rules"""
        self.alert_rules = {
            'high_cpu': {
                'metric': 'system_cpu_percent',
                'threshold': 80.0,
                'severity': 'warning',
                'message': 'High CPU usage detected',
                'recommendation': 'Consider scaling up resources or optimizing queries'
            },
            'critical_cpu': {
                'metric': 'system_cpu_percent',
                'threshold': 95.0,
                'severity': 'critical',
                'message': 'Critical CPU usage detected',
                'recommendation': 'Immediate action required - system may become unresponsive'
            },
            'high_memory': {
                'metric': 'system_memory_percent',
                'threshold': 85.0,
                'severity': 'warning',
                'message': 'High memory usage detected',
                'recommendation': 'Consider increasing memory or optimizing memory usage'
            },
            'critical_memory': {
                'metric': 'system_memory_percent',
                'threshold': 95.0,
                'severity': 'critical',
                'message': 'Critical memory usage detected',
                'recommendation': 'Immediate action required - system may crash'
            },
            'slow_queries': {
                'metric': 'avg_query_time',
                'threshold': 0.1,
                'severity': 'warning',
                'message': 'Slow query execution detected',
                'recommendation': 'Optimize queries or add database indexes'
            },
            'very_slow_queries': {
                'metric': 'avg_query_time',
                'threshold': 0.5,
                'severity': 'critical',
                'message': 'Very slow query execution detected',
                'recommendation': 'Immediate query optimization required'
            },
            'low_cache_hit_rate': {
                'metric': 'cache_hit_rate',
                'threshold': 0.7,
                'severity': 'warning',
                'message': 'Low cache hit rate detected',
                'recommendation': 'Consider increasing cache size or optimizing cache strategy'
            },
            'very_low_cache_hit_rate': {
                'metric': 'cache_hit_rate',
                'threshold': 0.5,
                'severity': 'critical',
                'message': 'Very low cache hit rate detected',
                'recommendation': 'Cache system may be failing - immediate investigation required'
            }
        }
    
    def _setup_notification_config(self):
        """Setup notification configuration"""
        self.notification_config = {
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': '',
                'password': '',
                'recipients': []
            },
            'slack': {
                'enabled': False,
                'webhook_url': '',
                'channel': '#hakgal-alerts'
            },
            'webhook': {
                'enabled': False,
                'url': '',
                'headers': {}
            }
        }
    
    def start_advanced_monitoring(self):
        """Start advanced monitoring"""
        if self.running:
            logger.warning("Advanced monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Advanced monitoring started")
    
    def stop_advanced_monitoring(self):
        """Stop advanced monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Advanced monitoring stopped")
    
    def _monitoring_loop(self):
        """Main advanced monitoring loop"""
        while self.running:
            try:
                # Get current metrics
                current_metrics = self.base_monitor.get_current_metrics_dict()
                
                # Check alert rules
                self._check_alert_rules(current_metrics)
                
                # Detect anomalies
                self._detect_anomalies(current_metrics)
                
                # Update alert status
                self._update_alert_status()
                
                time.sleep(5.0)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in advanced monitoring loop: {e}")
                time.sleep(1.0)
    
    def _check_alert_rules(self, metrics: Dict[str, Any]):
        """Check all alert rules against current metrics"""
        for rule_name, rule in self.alert_rules.items():
            metric_name = rule['metric']
            threshold = rule['threshold']
            
            if metric_name in metrics:
                current_value = metrics[metric_name]
                
                # Calculate cache hit rate if needed
                if metric_name == 'cache_hit_rate':
                    hits = metrics.get('cache_hits', 0)
                    misses = metrics.get('cache_misses', 0)
                    if hits + misses > 0:
                        current_value = hits / (hits + misses)
                    else:
                        current_value = 0.0
                
                # Check if threshold is exceeded
                if current_value > threshold:
                    # Check if alert already exists and is not resolved
                    existing_alert = self._find_existing_alert(rule_name, metric_name)
                    
                    if not existing_alert:
                        # Create new alert
                        alert = Alert(
                            timestamp=datetime.now().isoformat(),
                            severity=rule['severity'],
                            category='performance',
                            message=rule['message'],
                            metric_name=metric_name,
                            current_value=current_value,
                            threshold_value=threshold,
                            recommendation=rule['recommendation']
                        )
                        
                        self.alerts.append(alert)
                        logger.warning(f"ALERT: {alert.message} - {current_value:.2f} > {threshold:.2f}")
                        
                        # Send notifications
                        self._send_notifications(alert)
    
    def _find_existing_alert(self, rule_name: str, metric_name: str) -> Optional[Alert]:
        """Find existing unresolved alert for the same rule"""
        for alert in reversed(self.alerts):  # Check most recent first
            if (alert.metric_name == metric_name and 
                not alert.resolved and 
                alert.timestamp > (datetime.now() - timedelta(minutes=5)).isoformat()):
                return alert
        return None
    
    def _detect_anomalies(self, metrics: Dict[str, Any]):
        """Detect anomalies using statistical methods"""
        if len(self.base_monitor.metrics_history) < 10:
            return  # Need at least 10 data points
        
        # Get recent metrics for comparison
        recent_metrics = self.base_monitor.metrics_history[-10:]
        
        for metric_name in ['system_cpu_percent', 'system_memory_percent', 'avg_query_time']:
            if metric_name in metrics:
                current_value = metrics[metric_name]
                
                # Get historical values
                historical_values = [getattr(m, metric_name) for m in recent_metrics]
                
                if len(historical_values) > 0:
                    # Calculate statistics
                    mean_value = np.mean(historical_values)
                    std_value = np.std(historical_values)
                    
                    # Detect anomaly (3-sigma rule)
                    if std_value > 0:
                        z_score = abs(current_value - mean_value) / std_value
                        
                        if z_score > 3.0:  # 3-sigma anomaly
                            anomaly = Anomaly(
                                timestamp=datetime.now().isoformat(),
                                metric_name=metric_name,
                                value=current_value,
                                expected_value=mean_value,
                                deviation=z_score,
                                confidence=min(0.99, z_score / 5.0),  # Cap at 99%
                                description=f"Anomaly detected: {current_value:.2f} vs expected {mean_value:.2f} (z-score: {z_score:.2f})"
                            )
                            
                            self.anomalies.append(anomaly)
                            logger.warning(f"ANOMALY: {anomaly.description}")
    
    def _update_alert_status(self):
        """Update alert resolution status"""
        current_metrics = self.base_monitor.get_current_metrics_dict()
        
        for alert in self.alerts:
            if not alert.resolved:
                metric_name = alert.metric_name
                threshold = alert.threshold_value
                
                if metric_name in current_metrics:
                    current_value = current_metrics[metric_name]
                    
                    # Calculate cache hit rate if needed
                    if metric_name == 'cache_hit_rate':
                        hits = current_metrics.get('cache_hits', 0)
                        misses = current_metrics.get('cache_misses', 0)
                        if hits + misses > 0:
                            current_value = hits / (hits + misses)
                        else:
                            current_value = 0.0
                    
                    # Check if alert should be resolved
                    if current_value <= threshold * 0.9:  # 10% buffer
                        alert.resolved = True
                        logger.info(f"ALERT RESOLVED: {alert.message}")
    
    def _send_notifications(self, alert: Alert):
        """Send notifications for critical alerts"""
        if alert.severity == 'critical':
            # Send email notification
            if self.notification_config['email']['enabled']:
                self._send_email_notification(alert)
            
            # Send Slack notification
            if self.notification_config['slack']['enabled']:
                self._send_slack_notification(alert)
            
            # Send webhook notification
            if self.notification_config['webhook']['enabled']:
                self._send_webhook_notification(alert)
    
    def _send_email_notification(self, alert: Alert):
        """Send email notification"""
        try:
            config = self.notification_config['email']
            
            msg = MIMEMultipart()
            msg['From'] = config['username']
            msg['To'] = ', '.join(config['recipients'])
            msg['Subject'] = f"HAK/GAL Alert: {alert.message}"
            
            body = f"""
HAK/GAL System Alert

Severity: {alert.severity.upper()}
Time: {alert.timestamp}
Metric: {alert.metric_name}
Current Value: {alert.current_value:.2f}
Threshold: {alert.threshold_value:.2f}

Message: {alert.message}
Recommendation: {alert.recommendation}

Please investigate immediately.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email notification sent for alert: {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
    
    def _send_slack_notification(self, alert: Alert):
        """Send Slack notification"""
        try:
            config = self.notification_config['slack']
            
            payload = {
                'channel': config['channel'],
                'text': f"🚨 HAK/GAL Alert: {alert.message}",
                'attachments': [{
                    'color': 'danger' if alert.severity == 'critical' else 'warning',
                    'fields': [
                        {'title': 'Severity', 'value': alert.severity.upper(), 'short': True},
                        {'title': 'Metric', 'value': alert.metric_name, 'short': True},
                        {'title': 'Current Value', 'value': f"{alert.current_value:.2f}", 'short': True},
                        {'title': 'Threshold', 'value': f"{alert.threshold_value:.2f}", 'short': True},
                        {'title': 'Recommendation', 'value': alert.recommendation, 'short': False}
                    ]
                }]
            }
            
            response = requests.post(config['webhook_url'], json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack notification sent for alert: {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
    
    def _send_webhook_notification(self, alert: Alert):
        """Send webhook notification"""
        try:
            config = self.notification_config['webhook']
            
            payload = {
                'timestamp': alert.timestamp,
                'severity': alert.severity,
                'category': alert.category,
                'message': alert.message,
                'metric_name': alert.metric_name,
                'current_value': alert.current_value,
                'threshold_value': alert.threshold_value,
                'recommendation': alert.recommendation
            }
            
            response = requests.post(
                config['url'], 
                json=payload, 
                headers=config['headers']
            )
            response.raise_for_status()
            
            logger.info(f"Webhook notification sent for alert: {alert.message}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
    
    def get_alerts_summary(self) -> Dict[str, Any]:
        """Get alerts summary"""
        total_alerts = len(self.alerts)
        unresolved_alerts = len([a for a in self.alerts if not a.resolved])
        critical_alerts = len([a for a in self.alerts if a.severity == 'critical' and not a.resolved])
        warning_alerts = len([a for a in self.alerts if a.severity == 'warning' and not a.resolved])
        
        return {
            'total_alerts': total_alerts,
            'unresolved_alerts': unresolved_alerts,
            'critical_alerts': critical_alerts,
            'warning_alerts': warning_alerts,
            'recent_alerts': [asdict(a) for a in self.alerts[-10:]]  # Last 10 alerts
        }
    
    def get_anomalies_summary(self) -> Dict[str, Any]:
        """Get anomalies summary"""
        total_anomalies = len(self.anomalies)
        recent_anomalies = [a for a in self.anomalies if 
                           datetime.fromisoformat(a.timestamp) > datetime.now() - timedelta(hours=1)]
        
        return {
            'total_anomalies': total_anomalies,
            'recent_anomalies': len(recent_anomalies),
            'anomaly_details': [asdict(a) for a in recent_anomalies[-10:]]  # Last 10 anomalies
        }
    
    def configure_alert_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Configure or update an alert rule"""
        self.alert_rules[rule_name] = rule_config
        logger.info(f"Alert rule configured: {rule_name}")
    
    def configure_notifications(self, notification_type: str, config: Dict[str, Any]):
        """Configure notification settings"""
        if notification_type in self.notification_config:
            self.notification_config[notification_type].update(config)
            logger.info(f"Notification configuration updated: {notification_type}")
        else:
            logger.error(f"Unknown notification type: {notification_type}")
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'operational' if len([a for a in self.alerts if not a.resolved and a.severity == 'critical']) == 0 else 'degraded',
            'alerts': self.get_alerts_summary(),
            'anomalies': self.get_anomalies_summary(),
            'alert_rules': len(self.alert_rules),
            'notification_configs': {k: v['enabled'] for k, v in self.notification_config.items()},
            'monitoring_uptime': time.time() - getattr(self, 'start_time', time.time())
        }

def main():
    """Main execution function"""
    # Create base monitor
    config = {
        'database_path': 'data/advanced_monitoring.db',
        'monitoring_interval': 1.0,
        'max_history_size': 1000,
        'max_query_samples': 1000
    }
    
    base_monitor = HAKGALPerformanceMonitor(config)
    base_monitor.start_monitoring()
    
    # Create advanced monitoring system
    advanced_monitor = AdvancedMonitoringSystem(base_monitor)
    advanced_monitor.start_advanced_monitoring()
    
    try:
        print("🚀 Advanced Monitoring System Started")
        print("📊 Monitoring alerts, anomalies, and system health")
        print("⏹️  Press Ctrl+C to stop")
        
        # Simulate some activity
        import random
        while True:
            # Simulate varying system load
            query_time = random.uniform(0.01, 0.2)
            base_monitor.record_query_time(query_time)
            
            # Simulate cache events
            if random.random() > 0.3:
                base_monitor.record_cache_event(hit=True)
            else:
                base_monitor.record_cache_event(hit=False)
            
            # Print status every 30 seconds
            if int(time.time()) % 30 == 0:
                alerts_summary = advanced_monitor.get_alerts_summary()
                print(f"📊 Status: {alerts_summary['unresolved_alerts']} unresolved alerts, {alerts_summary['critical_alerts']} critical")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        advanced_monitor.stop_advanced_monitoring()
        base_monitor.stop_monitoring()
        print("✅ Advanced monitoring stopped")

if __name__ == "__main__":
    main()