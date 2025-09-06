"""
GPU VRAM Monitor & Cleaner for Ollama
"""
import subprocess
import psutil
import time
import requests
import sys

def get_gpu_memory():
    """Get current GPU memory usage"""
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            used, total = map(int, result.stdout.strip().split(','))
            percent = (used / total) * 100
            return {'used_mb': used, 'total_mb': total, 'percent': percent}
    except:
        return None

def unload_ollama_model():
    """Unload current Ollama model from VRAM"""
    try:
        # Send empty generate request with keep_alive=0
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': '',
                'prompt': '',
                'keep_alive': 0
            },
            timeout=5
        )
        print("✓ Model unload signal sent")
        return True
    except:
        print("⚠ Could not unload via API")
        return False

def kill_ollama():
    """Kill all Ollama processes"""
    killed = False
    for proc in psutil.process_iter(['pid', 'name']):
        if 'ollama' in proc.info['name'].lower():
            try:
                proc.terminate()
                print(f"✓ Killed {proc.info['name']} (PID: {proc.info['pid']})")
                killed = True
            except:
                pass
    return killed

def main():
    print("=" * 60)
    print("GPU VRAM MONITOR & CLEANER")
    print("=" * 60)
    
    # Show current status
    gpu = get_gpu_memory()
    if gpu:
        print(f"\nCurrent GPU Memory: {gpu['used_mb']}MB / {gpu['total_mb']}MB ({gpu['percent']:.1f}%)")
        
        if gpu['percent'] > 80:
            print("⚠ HIGH VRAM USAGE DETECTED!")
    
    print("\nOptions:")
    print("1. Monitor VRAM (real-time)")
    print("2. Unload Ollama model")
    print("3. Kill Ollama completely")
    print("4. Auto-cleanup when VRAM > 80%")
    print("0. Exit")
    
    choice = input("\nSelect [0-4]: ")
    
    if choice == "1":
        print("\nMonitoring GPU (Ctrl+C to stop)...")
        try:
            while True:
                gpu = get_gpu_memory()
                if gpu:
                    bar_length = 50
                    filled = int(bar_length * gpu['percent'] / 100)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    sys.stdout.write(f"\r[{bar}] {gpu['used_mb']}MB / {gpu['total_mb']}MB ({gpu['percent']:.1f}%)")
                    sys.stdout.flush()
                
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
    
    elif choice == "2":
        unload_ollama_model()
        time.sleep(3)
        gpu_after = get_gpu_memory()
        if gpu_after and gpu:
            freed = gpu['used_mb'] - gpu_after['used_mb']
            print(f"Freed {freed}MB of VRAM")
    
    elif choice == "3":
        if kill_ollama():
            print("✓ Ollama processes killed")
        else:
            print("No Ollama processes found")
    
    elif choice == "4":
        print("\nAuto-cleanup enabled (Ctrl+C to stop)...")
        try:
            while True:
                gpu = get_gpu_memory()
                if gpu and gpu['percent'] > 80:
                    print(f"\n⚠ VRAM at {gpu['percent']:.1f}% - Cleaning...")
                    unload_ollama_model()
                    time.sleep(5)
                time.sleep(10)
        except KeyboardInterrupt:
            print("\nAuto-cleanup stopped.")

if __name__ == "__main__":
    main()
