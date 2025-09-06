import os
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]

    # Ensure consistent UTF-8 stdout/stderr to avoid Windows cp1252 issues
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('PYTHONUTF8', '1')
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]
    except Exception:
        pass

    # Ensure Mojo native module and src on path
    mojo_pyd_dir = root / 'native' / 'mojo_kernels' / 'build' / 'Release'
    if mojo_pyd_dir.exists():
        sys.path.insert(0, str(mojo_pyd_dir))
    sys.path.insert(0, str(root / 'src_hexagonal'))

    # Read-only DB and Mojo flags (local to this process)
    os.environ.setdefault('MOJO_ENABLED', 'true')
    os.environ.setdefault('MOJO_VALIDATE_ENABLED', 'true')
    os.environ.setdefault('MOJO_DUPES_ENABLED', 'false')
    os.environ.setdefault(
        'HAKGAL_SQLITE_DB_PATH',
        'file:D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db?mode=ro&cache=shared',
    )
    os.environ.setdefault('HAKGAL_SQLITE_READONLY', 'true')

    # Start app on 5003
    import hexagonal_api_enhanced as m  # noqa: WPS433

    api = m.create_app(use_legacy=False, enable_all=True)
    api.run(host='127.0.0.1', port=5003, debug=False)


if __name__ == '__main__':
    main()


