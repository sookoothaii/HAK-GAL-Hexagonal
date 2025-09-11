import requests
import time
import concurrent.futures

print("PERFORMANCE TEST VOR/NACH OPTIMIERUNG")
print("=" * 60)

def test_performance(label):
    def make_request(i):
        try:
            r = requests.get("http://localhost:5002/api/facts/count", timeout=0.5)
            return r.status_code == 200
        except:
            return False
    
    # Test mit 50 parallelen Requests
    start = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, i) for i in range(50)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    duration = time.time() - start
    success = sum(results)
    rps = success / duration if duration > 0 else 0
    
    print(f"\n{label}:")
    print(f"  Erfolgreiche Requests: {success}/50")
    print(f"  Zeit: {duration:.2f}s")
    print(f"  Performance: {rps:.1f} req/s")
    
    return rps

# Test jetzt
current_rps = test_performance("AKTUELLE PERFORMANCE")

print("\n" + "=" * 60)
print("Führen Sie jetzt 'python optimize_db_real.py' aus")
print("und testen Sie dann nochmal mit diesem Script!")
print("=" * 60)
