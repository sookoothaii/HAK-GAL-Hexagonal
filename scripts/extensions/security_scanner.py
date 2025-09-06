import argparse
import subprocess


def run_bandit(target: str) -> int:
    return subprocess.call(["bandit", "-q", "-r", target])


def main():
    ap = argparse.ArgumentParser(description="Run basic security scans")
    ap.add_argument("--path", default=".", help="Target path (default: .)")
    args = ap.parse_args()
    code = run_bandit(args.path)
    print(f"Bandit exit code: {code}")


if __name__ == "__main__":
    main()


