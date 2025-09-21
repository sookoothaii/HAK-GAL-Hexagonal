import json, os, sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def check_env():
    keys = [
        'DEEPSEEK_API_KEY','GEMINI_API_KEY','ANTHROPIC_API_KEY',
        'DEEPSEEK_MODEL','GEMINI_MODEL','ANTHROPIC_MODEL'
    ]
    env = {}
    for k in keys:
        env[k] = '<set>' if os.environ.get(k) else '<missing>'
    return env

def check_files():
    files = [
        'ssot.md',
        # bevorzugte Kontextdateien
        'gemini_context.md','claude_context.md','deepseek_context.md',
        # Fallbacks (Großschreibung)
        'GEMINI.md','CLAUDE.md','DEEPSEEK.md'
    ]
    out = {}
    for f in files:
        p = ROOT / f
        out[f] = {'exists': p.exists(), 'size': p.stat().st_size if p.exists() else 0}
    # Hinweis, welche Fallbacks genutzt würden
    out['context_fallbacks'] = {
        'Gemini': 'GEMINI.md' if not (ROOT / 'gemini_context.md').exists() and (ROOT / 'GEMINI.md').exists() else None,
        'Claude': 'CLAUDE.md' if not (ROOT / 'claude_context.md').exists() and (ROOT / 'CLAUDE.md').exists() else None,
        'Deepseek': 'DEEPSEEK.md' if not (ROOT / 'deepseek_context.md').exists() and (ROOT / 'DEEPSEEK.md').exists() else None,
    }
    return out

def main():
    report = {
        'env': check_env(),
        'files': check_files(),
        'notes': 'Ensure ultimate_mcp/.env is loaded before running for accurate env status.'
    }

    # Optional: Archimedes-Output-Validierung, wenn Validator vorhanden ist
    try:
        validator = ROOT / 'validate_archimedes_outputs.py'
        result = {'available': validator.exists()}
        if validator.exists():
            proc = subprocess.run(
                [sys.executable, str(validator)],
                cwd=str(ROOT),
                capture_output=True,
                text=True,
                timeout=90
            )
            result.update({
                'exit_code': proc.returncode,
                'stdout': (proc.stdout or '')[-1000:],
                'stderr': (proc.stderr or '')[-1000:]
            })
        report['archimedes_validation'] = result
    except Exception as e:
        report['archimedes_validation'] = {'error': str(e)}
    out_dir = ROOT / 'reports'
    out_dir.mkdir(exist_ok=True)
    (out_dir / 'self_check_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()


