import argparse
import subprocess


def run(cmd: list[str]) -> int:
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print(f"Command not found: {cmd[0]}")
        return 127


def main():
    ap = argparse.ArgumentParser(description="Check Python and Node dependencies")
    ap.add_argument("--pip", action="store_true", help="Run pip check")
    ap.add_argument("--npm", action="store_true", help="Run npm audit --production")
    args = ap.parse_args()

    if args.pip:
        print("== pip check ==")
        run(["python", "-m", "pip", "check"])
    if args.npm:
        print("== npm audit (prod) ==")
        run(["npm", "audit", "--production", "--audit-level=high"])


if __name__ == "__main__":
    main()


