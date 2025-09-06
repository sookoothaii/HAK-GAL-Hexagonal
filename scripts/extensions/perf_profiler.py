import argparse
import cProfile
import pstats


def main():
    ap = argparse.ArgumentParser(description="Profile a Python module entrypoint")
    ap.add_argument("module", help="Python module path, e.g. scripts.slack.post_kb_status")
    ap.add_argument("--func", default="main", help="Entrypoint function name")
    ap.add_argument("--out", default="perf_profile.stats", help="Profile output file")
    args = ap.parse_args()

    pr = cProfile.Profile()
    pr.enable()
    mod = __import__(args.module, fromlist=[args.func])
    getattr(mod, args.func)()
    pr.disable()
    pr.dump_stats(args.out)
    p = pstats.Stats(args.out)
    p.sort_stats("cumulative").print_stats(30)


if __name__ == "__main__":
    main()


