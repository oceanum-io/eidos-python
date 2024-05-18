import os

ROOTDIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "oceanum", "eidos"
)


def write_init(curdir):
    with open(os.path.join(curdir, "__init__.py"), "w") as f:
        for name in os.listdir(curdir):
            if (
                not name.startswith("_")
                and not name.startswith(".")
                and not name.endswith(".md")
            ):
                f.write(f"from .{name.replace('.py','')} import *\n")


def walk(curdir):
    for name in os.listdir(curdir):
        if name.startswith("_") or name.startswith("."):
            continue
        if os.path.isdir(os.path.join(curdir, name)):
            write_init(os.path.join(curdir, name))
            walk(os.path.join(curdir, name))


if __name__ == "__main__":
    walk(ROOTDIR)
    write_init(ROOTDIR)
