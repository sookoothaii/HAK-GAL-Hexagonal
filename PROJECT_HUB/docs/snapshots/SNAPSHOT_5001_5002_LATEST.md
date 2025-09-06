# System Snapshot — 5001 / 5002 (LATEST)

## 5001
- Health: operational, port=5001, repo=SQLiteFactRepository
- Facts count: 3879 (ttl 30s)

## 5002 (Mojo)
- Health: operational, port=5002, repo=SQLiteFactRepository
- Mojo: available=true, backend=mojo_kernels, flag_enabled=true, present=true
- Bench(1000, 0.95): validate 0.0 ms (1000/0), duplicates ~191.17 ms, pairs=52

## Notes
- 5002 läuft read-only mit aktivem Mojo-Adapter
- Flags (enabled/validate/dupes) sind aktiv
