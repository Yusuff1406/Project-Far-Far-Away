"""Create ignored output folders for focused native fixtures."""
import re

def prepare_workspace(root):
    for path in (root / "tests").glob("*.cpp"):
        for name in set(re.findall(r'"(scratch[0-9]+)/', path.read_text())):
            (root / name).mkdir(exist_ok=True)
