import json, sys, subprocess, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PY = str(ROOT / '.venv_hexa' / 'Scripts' / 'python.exe')
ORCH = str(ROOT / 'multi_agent_orchestrator.py')
OUT_DIR = ROOT / 'reports'
OUT_DIR.mkdir(exist_ok=True)


def run_cmd(args):
    cp = subprocess.run(args, capture_output=True, text=True)
    return cp.returncode, cp.stdout, cp.stderr


def write(path: Path, text: str):
    path.write_text(text, encoding='utf-8')


def consensus_task(task: str, file_stub: str):
    code, out, err = run_cmd([PY, ORCH, '--consensus', task])
    if code != 0:
        return {'ok': False, 'err': err}
    # Try JSON parse; if fails, save raw
    try:
        data = json.loads(out)
        write(OUT_DIR / f'{file_stub}.json', json.dumps(data, ensure_ascii=False, indent=2))
        return {'ok': True, 'json': True, 'path': str(OUT_DIR / f'{file_stub}.json')}
    except Exception:
        write(OUT_DIR / f'{file_stub}.txt', out)
        return {'ok': True, 'json': False, 'path': str(OUT_DIR / f'{file_stub}.txt')}


def main():
    status_code, status_out, _ = run_cmd([PY, ORCH, '--status'])
    write(OUT_DIR / 'orchestrator_status.txt', status_out)

    r1 = consensus_task('Kurze Architektur-Zusammenfassung von HAK_GAL', 'consensus_architecture')
    r2 = consensus_task('Analysiere KB-Anomalien und schlage valide Tools vor', 'consensus_kb_anomalies')

    summary = {
        'status_file': str(OUT_DIR / 'orchestrator_status.txt'),
        'architecture': r1,
        'kb_anomalies': r2
    }
    write(OUT_DIR / 'consensus_summary.json', json.dumps(summary, ensure_ascii=False, indent=2))
    print('Consensus reports written to', str(OUT_DIR))

if __name__ == '__main__':
    main()
