#!/usr/bin/env python3
"""Elimina imágenes y archivos que no usa el sitio en producción."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "public" / "images"


def collect_used() -> set[str]:
    used: set[str] = set()

    def add_url(url: str) -> None:
        url = url.split("?")[0]
        if "/public/images/" in url:
            rel = url.split("/public/images/", 1)[1]
            used.add(rel)

    for html in [
        ROOT / "index.html",
        ROOT / "cotizacion" / "index.html",
    ]:
        if html.exists():
            for match in re.findall(r"/public/images/[^\s\"')>]+", html.read_text(encoding="utf-8")):
                add_url(match)

    products = ROOT / "js" / "products-data.js"
    if products.exists():
        for match in re.findall(r"'/public/images/[^']+'", products.read_text(encoding="utf-8")):
            add_url(match.strip("'"))

    for name in ("logo.png", "og-image.png"):
        used.add(name)

    for i in range(1, 5):
        used.add(f"hero/slide-{i}.jpg")

    return used


def rebuild_manifest(used: set[str]) -> None:
    manifest_path = IMG / "catalog-manifest.json"
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    kept = []
    for entry in manifest.get("images", []):
        rel = entry["path"].replace("/public/images/", "")
        if rel in used:
            kept.append(entry)
    manifest["images"] = kept
    manifest["hero_slides"] = [
        s for s in manifest.get("hero_slides", [])
        if s.get("file", "").replace("/public/images/", "") in used
    ]
    cats = manifest.get("categories", {})
    for cat in cats:
        if isinstance(cats[cat], dict):
            cats[cat]["count"] = sum(1 for i in kept if i.get("category") == cat)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    used = collect_used()
    deleted_files = 0
    deleted_dirs = 0

    for path in sorted(IMG.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if not path.exists():
            continue
        if path.is_file():
            rel = path.relative_to(IMG).as_posix()
            if rel not in used:
                path.unlink()
                deleted_files += 1
        elif path.is_dir():
            try:
                path.rmdir()
                deleted_dirs += 1
            except OSError:
                pass

    pycache = ROOT / "scripts" / "__pycache__"
    if pycache.exists():
        shutil.rmtree(pycache)

    # WhatsApp / legacy junk at images root
    legacy_root = IMG.parent  # public/images parent is public - actually junk in images/
    cocinas = IMG / "çocinasintegrales"
    if cocinas.exists():
        shutil.rmtree(cocinas)
        deleted_dirs += 1

    rebuild_manifest(used)

    print(f"Kept {len(used)} image files")
    print(f"Deleted {deleted_files} files, {deleted_dirs} empty folders")
    for rel in sorted(used):
        print(f"  keep: {rel}")


if __name__ == "__main__":
    main()
