"""Check the scope and slide assets of the approved baseline release."""
from pathlib import Path

book = Path("_book")
expected = {"index.html", "chapters/introduction.html", "chapters/risk.html", "search.json"}
expected.update(f"assets/images/slide-{i:03}.png" for i in range(1, 33))
actual = set()
for path in book.rglob("*"):
    if path.is_symlink():
        raise SystemExit(f"Unexpected link: {path}")
    if path.is_file() and path.relative_to(book).parts[0] != "site_libs":
        actual.add(path.relative_to(book).as_posix())
if actual != expected:
    raise SystemExit(f"Unexpected or missing release files: {sorted(actual ^ expected)}")
