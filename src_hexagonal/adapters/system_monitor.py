"""
System Monitoring Module for HAK-GAL Hexagonal
==============================================
Provides real-time system metrics via WebSocket
"""

import psutil
import threading
import time
import json
from typing import Dict, Any, Optional

try:
    import GPUtil
    import pynvml
    GPU_AVAILABLE = True
    try:
        pynvml.nvmlInit()
    except:
        GPU_AVAILABLE = False
except ImportError:
    GPU_AVAILABLE = False
    print("[WARN] GPU monitoring not available. Install: pip install gputil nvidia-ml-py")

class SystemMonitor:
    """Monitors system resources and broadcasts metrics via WebSocket"""
    
    def __init__(self, socketio=None):
        self.socketio = socketio
        self.monitoring = False
        self.monitor_thread = None
        self.interval = 5  # seconds
        
    def start_monitoring(self):
        """Start the monitoring thread"""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("[OK] System monitoring started")
        
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("[OK] System monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = self.get_system_metrics()
                
                # Emit via WebSocket if available
                if self.socketio:
                    # Send system load
                    self.socketio.emit('system_load_update', {
                        'cpu': metrics['cpu']['percent'],
                        'memory': metrics['memory']['percent'],
                        'gpu': metrics['gpu']['utilization'] if metrics['gpu'] else 0,
                        'gpu_memory': metrics['gpu']['memory_percent'] if metrics['gpu'] else 0
                    }, to='/')
                    
                    # Send detailed GPU info
                    if metrics['gpu']:
                        self.socketio.emit('gpu_update', {
                            'gpu': metrics['gpu']
                        }, to='/')
                        
                    # Send full system status
                    self.socketio.emit('system_status_update', {
                        'status': 'operational',
                        'metrics': metrics
                    }, to='/')
                    
                time.sleep(self.interval)
                
            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
                time.sleep(self.interval)
                
    def get_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        metrics = {
            'timestamp': time.time(),
            'cpu': self._get_cpu_metrics(),
            'memory': self._get_memory_metrics(),
            'disk': self._get_disk_metrics(),
            'gpu': self._get_gpu_metrics() if GPU_AVAILABLE else None,
            'network': self._get_network_metrics()
        }
        return metrics
        
    def _get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU metrics"""
        return {
            'percent': psutil.cpu_percent(interval=1),
            'count': psutil.cpu_count(),
            'count_logical': psutil.cpu_count(logical=True),
            'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            'per_cpu': psutil.cpu_percent(interval=0, percpu=True)
        }
        
    def _get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory metrics"""
        mem = psutil.virtual_memory()
        return {
            'percent': mem.percent,
            'total': mem.total,
            'available': mem.available,
            'used': mem.used,
            'free': mem.free,
            'total_gb': round(mem.total / (1024**3), 2),
            'used_gb': round(mem.used / (1024**3), 2)
        }
        
    def _get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk metrics"""
        disk = psutil.disk_usage('/')
        return {
            'percent': disk.percent,
            'total': disk.total,
            'used': disk.used,
            'free': disk.free,
            'total_gb': round(disk.total / (1024**3), 2),
            'used_gb': round(disk.used / (1024**3), 2)
        }
        
    def _get_gpu_metrics(self) -> Optional[Dict[str, Any]]:
        """Get GPU metrics using nvidia-ml-py"""
        if not GPU_AVAILABLE:
            return None
            
        try:
            # Try GPUtil first (simpler API)
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]  # Use first GPU
                return {
                    'name': gpu.name,
                    'id': gpu.id,
                    'utilization': gpu.load * 100,  # Convert to percentage
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'memory_free': gpu.memoryFree,
                    'memory_percent': (gpu.memoryUsed / gpu.memoryTotal * 100) if gpu.memoryTotal > 0 else 0,
                    'temperature': gpu.temperature,
                    'driver_version': gpu.driver,
                    'available': True
                }
        except:
            pass
            
        # Fallback to pynvml (more detailed but complex)
        try:
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count > 0:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                
                # Get GPU info
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                
                # Memory info
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Utilization
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                
                # Temperature
                try:
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except:
                    temp = None
                    
                # Power
                try:
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to Watts
                    power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000.0
                except:
                    power = None
                    power_limit = None
                    
                # Clock speeds
                try:
                    clock_graphics = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
                    clock_mem = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
                except:
                    clock_graphics = None
                    clock_mem = None
                    
                # Fan speed
                try:
                    fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
                except:
                    fan_speed = None
                    
                return {
                    'name': name,
                    'utilization': util.gpu,
                    'memory_used': mem_info.used / (1024**2),  # Convert to MB
                    'memory_total': mem_info.total / (1024**2),  # Convert to MB
                    'memory_free': mem_info.free / (1024**2),  # Convert to MB
                    'memory_percent': (mem_info.used / mem_info.total * 100) if mem_info.total > 0 else 0,
                    'temperature': temp,
                    'power_draw': power,
                    'power_limit': power_limit,
                    'clock_graphics': clock_graphics,
                    'clock_mem': clock_mem,
                    'fan_speed': fan_speed,
                    'available': True
                }
        except Exception as e:
            print(f"GPU monitoring error: {e}")
            return None
            
    def _get_network_metrics(self) -> Dict[str, Any]:
        """Get network metrics"""
        net = psutil.net_io_counters()
        return {
            'bytes_sent': net.bytes_sent,
            'bytes_recv': net.bytes_recv,
            'packets_sent': net.packets_sent,
            'packets_recv': net.packets_recv,
            'errin': net.errin,
            'errout': net.errout,
            'dropin': net.dropin,
            'dropout': net.dropout
        }
        
    def get_status(self) -> Dict[str, Any]:
        """Get monitoring status"""
        return {
            'monitoring': self.monitoring,
            'interval': self.interval,
            'gpu_available': GPU_AVAILABLE
        }

# Singleton instance
_monitor_instance = None

def get_system_monitor(socketio=None) -> SystemMonitor:
    """Get or create the system monitor singleton"""
    global _monitor_instance
    if _monitor_instance is None:
        _monitor_instance = SystemMonitor(socketio)
    elif socketio and _monitor_instance.socketio is None:
        _monitor_instance.socketio = socketio
    return _monitor_instance
