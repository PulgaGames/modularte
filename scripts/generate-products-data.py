#!/usr/bin/env python3
"""Genera products-data.js desde catalog-manifest.json (solo fotos propias)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "public" / "images" / "catalog-manifest.json"
OUT = ROOT / "js" / "products-data.js"

SKIP_NOTES = ("obra en progreso", "desenfoque", "fotógrafo", "fotografo", "herramientas visibles", "fondo con obra")
SKIP_SOURCE = ("referencia", "render")

LOCATIONS = [
    "Punta Pacífica", "Costa del Este", "San Francisco", "El Cangrejo",
    "Clayton", "Bella Vista", "Obarrio", "Arraiján",
]

MATERIALS = [
    "Madera natural · Melamina premium",
    "Nogal · Herrajes soft-close",
    "Roble · Barniz satinado",
    "Cedro · Acabado mate",
    "MDF lacado · Melamina texturada",
    "Teca tratada · Herrajes premium",
]


def is_eligible(img: dict) -> bool:
    if img.get("source_type") in SKIP_SOURCE:
        return False
    if any(n in img.get("notes", "").lower() for n in SKIP_NOTES):
        return False
    if img.get("duplicate_of") and not img.get("primary", True):
        return False
    return True


def pool_for_category(images, category):
    """Solo imágenes reales de la categoría — sin repetir ni mezclar otras carpetas."""
    seen = set()
    result = []
    for img in images:
        if img["category"] != category:
            continue
        if not is_eligible(img):
            continue
        path = img["path"]
        if path in seen:
            continue
        seen.add(path)
        result.append(img)
    result.sort(key=lambda img: (not img.get("primary", True), img.get("id", "")))
    return result


def build_catalog(category, images):
    """Un producto por cada imagen única de la categoría."""
    pool = pool_for_category(images, category)
    items = []
    for i, img in enumerate(pool):
        loc = LOCATIONS[i % len(LOCATIONS)]
        items.append({
            "title": f"{img['title']} — {loc}",
            "description": f"Proyecto realizado por ModulArt en {loc}. {img['title']}.",
            "material": MATERIALS[i % len(MATERIALS)],
            "src": img["path"],
            "alt": img["title"],
        })
    return items


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    images = manifest["images"]

    meta = {
        "closets": {
            "title": "Closets",
            "metaDescription": "Catálogo de closets en madera a medida en Ciudad de Panamá. Proyectos realizados por ModulArt.",
            "description": "Explora nuestro catálogo de closets fabricados e instalados en hogares de Ciudad de Panamá. Cada proyecto se diseña a medida según el espacio, estilo y necesidades de almacenamiento del cliente.",
        },
        "puertas": {
            "title": "Puertas",
            "metaDescription": "Catálogo de puertas en madera a medida en Panamá. Proyectos de ModulArt.",
            "description": "Puertas interiores y principales fabricadas a medida. Revisa proyectos instalados en residencias y oficinas de la capital panameña.",
        },
        "cocinas-integrales": {
            "title": "Cocinas integrales",
            "metaDescription": "Catálogo de cocinas integrales en madera en Panamá. Proyectos realizados por ModulArt.",
            "description": "Cocinas integrales diseñadas, fabricadas e instaladas por nuestro equipo. Cada proyecto combina funcionalidad, estética y materiales de alta durabilidad.",
        },
        "comedores": {
            "title": "Comedores",
            "metaDescription": "Catálogo de comedores en madera a medida en Panamá. Proyectos de ModulArt.",
            "description": "Mesas, sillas, buffets y vitrinas fabricados para crear comedores únicos. Conoce proyectos entregados a clientes en toda la ciudad.",
        },
        "salas": {
            "title": "Salas",
            "metaDescription": "Catálogo de mobiliario de sala en madera en Panamá. Proyectos de ModulArt.",
            "description": "Muebles TV, libreros, repisas y centros de entretenimiento integrados al diseño de cada sala. Proyectos reales entregados por ModulArt.",
        },
        "alcobas": {
            "title": "Alcobas",
            "metaDescription": "Catálogo de mobiliario de alcoba en madera en Panamá. Proyectos de ModulArt.",
            "description": "Cabeceras, mesitas, cómodas y módulos de almacenamiento diseñados para crear alcobas completas y armoniosas.",
        },
        "banos": {
            "title": "Baños",
            "metaDescription": "Catálogo de muebles de baño en madera en Panamá. Proyectos de ModulArt.",
            "description": "Vanities, espejos y módulos de almacenamiento con tratamiento para ambientes húmedos. Proyectos instalados en residencias de Panamá.",
        },
        "pisos-escalas-pasamanos": {
            "title": "Pisos, escalas y pasamanos",
            "metaDescription": "Catálogo de pisos, escaleras y pasamanos en madera en Panamá. Proyectos de ModulArt.",
            "description": "Instalación de pisos, construcción de escaleras y pasamanos con precisión estructural. Revisa trabajos completados en hogares y locales comerciales.",
        },
    }

    order = [
        "closets", "puertas", "cocinas-integrales", "comedores",
        "salas", "alcobas", "banos", "pisos-escalas-pasamanos",
    ]

    lines = ["window.MODULART_PRODUCTS = {"]
    for slug in order:
        pool = pool_for_category(images, slug)
        catalog = build_catalog(slug, images)
        hero = pool[0] if pool else None
        info = meta[slug]
        lines.append(f"  '{slug}': {{")
        lines.append(f"    slug: '{slug}',")
        lines.append(f"    title: '{info['title']}',")
        lines.append(f"    metaDescription: '{info['metaDescription']}',")
        if hero:
            lines.append(f"    heroImage: '{hero['path']}',")
            lines.append(f"    heroAlt: '{hero['title'].replace(chr(39), chr(92)+chr(39))}',")
        lines.append(f"    description: '{info['description']}',")
        lines.append("    catalog: [")
        for item in catalog:
            lines.append("      {")
            lines.append(f"        title: '{item['title'].replace(chr(39), chr(92)+chr(39))}',")
            lines.append(f"        description: '{item['description'].replace(chr(39), chr(92)+chr(39))}',")
            lines.append(f"        material: '{item['material']}',")
            lines.append(f"        src: '{item['src']}',")
            lines.append(f"        alt: '{item['alt'].replace(chr(39), chr(92)+chr(39))}'")
            lines.append("      },")
        lines.append("    ]")
        lines.append("  },")
    lines.append("};")
    lines.append("")
    lines.append("window.MODULART_PRODUCT_ORDER = [")
    for slug in order:
        lines.append(f"  '{slug}',")
    lines.append("];")
    lines.append("")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    for slug in order:
        n = len(build_catalog(slug, images))
        print(f"  {slug}: {n} proyecto(s)")


if __name__ == "__main__":
    main()
