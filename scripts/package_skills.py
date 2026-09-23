"""Build repeatable, self-contained skill ZIPs using only the standard library."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "downloads"
EXCLUDED = {"__pycache__", "node_modules"}


def add_file(archive, name, data):
    info = ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
    info.compress_type = ZIP_DEFLATED
    info.external_attr = 0o100644 << 16
    archive.writestr(info, data)


def main():
    OUT.mkdir(exist_ok=True)
    skills = sorted(p.parent for p in ROOT.glob("*/SKILL.md"))
    if not skills:
        raise SystemExit("No top-level skill folders found.")
    for skill in skills:
        target = OUT / f"{skill.name}.zip"
        with ZipFile(target, "w") as archive:
            for path in sorted(skill.rglob("*")):
                parts = path.relative_to(skill).parts
                if any(p.startswith(".") or p in EXCLUDED for p in parts):
                    continue
                if path.is_file() and not path.is_symlink():
                    add_file(archive, f"{skill.name}/{path.relative_to(skill)}", path.read_bytes())
            if not (skill / "LICENSE").exists():
                add_file(archive, f"{skill.name}/LICENSE", (ROOT / "LICENSE").read_bytes())
        print(f"Built {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
