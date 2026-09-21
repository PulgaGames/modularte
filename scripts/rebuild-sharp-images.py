#!/usr/bin/env python3
"""Reexporta imágenes desde originales con más resolución para pantallas retina."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "public" / "images"

spec = importlib.util.spec_from_file_location(
    "process_images",
    ROOT / "scripts" / "process-images.py",
)
process_images = importlib.util.module_from_spec(spec)
sys.modules["process_images"] = process_images
spec.loader.exec_module(process_images)

HERO_SLIDE_ORDER = process_images.HERO_SLIDE_ORDER
crop_hero_16_9 = process_images.crop_hero_16_9
enhance = process_images.enhance
preprocess = process_images.preprocess
save_jpg = process_images.save_jpg

CATALOG_MAX = 1920
HERO_SIZE = (2400, 1350)
HERO_QUALITY = 92
CATALOG_QUALITY = 91


def find_original(entry: dict) -> Path | None:
    original = entry.get("original", "")
    candidates = [
        IMG / "_originals" / "whatsapp" / original,
        IMG / "_originals" / "inbox" / original,
        IMG / original,
        IMG / entry.get("category", "") / original,
    ]
    if "/" in original or "\\" in original:
        candidates.insert(0, IMG / original)
    for path in candidates:
        if path.exists():
            return path
    return None


def resize_catalog(img: Image.Image) -> Image.Image:
    w, h = img.size
    if max(w, h) <= CATALOG_MAX:
        return img
    if w >= h:
        new_w = CATALOG_MAX
        new_h = int(h * (CATALOG_MAX / w))
    else:
        new_h = CATALOG_MAX
        new_w = int(w * (CATALOG_MAX / h))
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def finalize_hero(img: Image.Image) -> Image.Image:
    hero = crop_hero_16_9(img.copy())
    w, h = hero.size
    tw, th = HERO_SIZE
    if w >= int(tw * 0.7):
        return hero.resize(HERO_SIZE, Image.Resampling.LANCZOS)
    scale = min(1.35, tw / w)
    return hero.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)


def rebuild_catalog_image(entry: dict, preprocess_mode: str | None = None) -> bool:
    src = find_original(entry)
    if not src:
        return False

    dest = IMG / entry["path"].replace("/public/images/", "")
    img = Image.open(src)
    img = preprocess(img, preprocess_mode)
    img = enhance(img)
    img = resize_catalog(img)
    save_jpg(img, dest, quality=CATALOG_QUALITY)
    entry["width"] = img.size[0]
    entry["height"] = img.size[1]

    if entry.get("hero_path"):
        hero_img = finalize_hero(img)
        hero_dest = IMG / "hero" / Path(entry["hero_path"]).name
        save_jpg(hero_img, hero_dest, quality=HERO_QUALITY)
        entry["hero_width"] = hero_img.size[0]
        entry["hero_height"] = hero_img.size[1]
    return True


def rebuild_hero_slides(manifest: dict):
    by_id = {i["id"]: i for i in manifest["images"] if i.get("hero") and i.get("hero_path")}
    slides = []
    for i, sid in enumerate(HERO_SLIDE_ORDER, start=1):
        entry = by_id.get(sid)
        if not entry:
            continue
        hero_file = IMG / "hero" / Path(entry["hero_path"]).name
        slide_file = IMG / "hero" / f"slide-{i}.jpg"
        if hero_file.exists():
            save_jpg(Image.open(hero_file), slide_file, quality=HERO_QUALITY)
            slides.append({
                "slide": i,
                "file": f"/public/images/hero/slide-{i}.jpg",
                "source": entry["hero_path"],
                "title": entry["title"],
            })
    manifest["hero_slides"] = slides


def main():
    manifest_path = IMG / "catalog-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    updated = 0

    for entry in manifest["images"]:
        mode = None
        if entry.get("id") == "repisas-madera-bano":
            mode = "crop_top_text"
        if entry.get("id") == "repisas-rusticas-bano-ganchos":
            mode = "crop_letterbox"
        if rebuild_catalog_image(entry, mode):
            updated += 1
            print(f"OK {entry['path']} -> {entry.get('width')}x{entry.get('height')}")

    rebuild_hero_slides(manifest)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nUpdated {updated} images. Hero slides: {len(manifest['hero_slides'])}")


if __name__ == "__main__":
    main()
