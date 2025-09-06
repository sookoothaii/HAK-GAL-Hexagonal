import argparse
from pathlib import Path


TEMPLATE_PY = """"""
def {function_name}(*args, **kwargs):
    """
    TODO: implement {function_name}
    """
    raise NotImplementedError("{function_name} not implemented")
""".lstrip()


def main():
    p = argparse.ArgumentParser(description="Generate boilerplate code")
    p.add_argument("target", help="Output file path (e.g. src/module.py)")
    p.add_argument("--function", dest="func", default="run", help="Function name")
    args = p.parse_args()

    out = Path(args.target)
    out.parent.mkdir(parents=True, exist_ok=True)
    content = TEMPLATE_PY.format(function_name=args.func)
    out.write_text(content, encoding="utf-8")
    print(f"OK: generated {out}")


if __name__ == "__main__":
    main()


