#!/usr/bin/env python3
"""Procesa, mejora y clasifica imágenes reales de ModulArt."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "public" / "images"

REJECTED = {
    "WhatsApp Image 2026-06-16 at 8.20.14 AM (3).jpeg": "duplicado borroso",
    "WhatsApp Image 2026-06-16 at 8.21.22 AM (4).jpeg": "movimiento / desenfoque",
    "WhatsApp Image 2026-06-16 at 8.21.25 AM (4).jpeg": "marca de tercero ASYMETRICO",
    "WhatsApp Image 2026-06-16 at 8.21.26 AM.jpeg": "captura de pantalla con UI",
}

CLASSIFICATION = {
    "WhatsApp Image 2026-06-16 at 8.20.10 AM.jpeg": {"category": "alcobas", "slug": "alcoba-moderna-listones-eucalipto", "title": "Alcoba moderna con listones y mesas de noche", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.10 AM (1).jpeg": {"category": "salas", "slug": "mueble-tv-listones-led-sala", "title": "Centro de entretenimiento con listones e iluminación LED", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.11 AM.jpeg": {"category": "salas", "slug": "mueble-decorativo-repisas-espejo-led", "title": "Mueble decorativo con repisas flotantes e iluminación LED", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.12 AM.jpeg": {"category": "alcobas", "slug": "alcoba-nautica-panel-listones", "title": "Alcoba náutica con panel de listones de madera", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.12 AM (1).jpeg": {"category": "alcobas", "slug": "alcoba-nautica-vista-mar", "title": "Alcoba náutica con vista al mar", "hero": False, "primary": False, "duplicate_of": "alcoba-nautica-panel-listones"},
    "WhatsApp Image 2026-06-16 at 8.20.13 AM.jpeg": {"category": "comedores", "slug": "comedor-buffet-mimbre-led", "title": "Comedor con buffet en madera, mimbre e iluminación LED", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.13 AM (1).jpeg": {"category": "salas", "slug": "mueble-tv-sala-madera-balcon", "title": "Centro de entretenimiento de piso a techo con balcón", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.13 AM (2).jpeg": {"category": "salas", "slug": "sala-paneles-listones-estante-bote", "title": "Sala con revestimiento de listones y estantería decorativa", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.13 AM (3).jpeg": {"category": "alcobas", "slug": "alcoba-panel-listones-azul-marino", "title": "Alcoba con panel listonado y acentos azul marino", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.14 AM.jpeg": {"category": "alcobas", "slug": "habitacion-doble-cabecero-palma", "title": "Habitación doble con cabecero decorativo de palma", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.14 AM (1).jpeg": {"category": "alcobas", "slug": "habitacion-doble-cabecero-palma-angulo", "title": "Habitación doble con cabecero de palma — ángulo alterno", "hero": False, "primary": False, "duplicate_of": "habitacion-doble-cabecero-palma"},
    "WhatsApp Image 2026-06-16 at 8.20.14 AM (2).jpeg": {"category": "alcobas", "slug": "alcoba-cabecero-palma-cama-queen", "title": "Alcoba con cabecero de palma y espejos", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.14 AM (4).jpeg": {"category": "salas", "slug": "sala-tv-integrada-alcoba-listones", "title": "Sala con mueble TV e integración con alcoba", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.15 AM.jpeg": {"category": "alcobas", "slug": "dormitorio-cabecero-palma-listones", "title": "Dormitorio con pared decorativa en madera tallada", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.20.15 AM (1).jpeg": {"category": "salas", "slug": "sala-biombo-hoja-repisas", "title": "Sala con biombo decorativo y repisas flotantes", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.07 AM.jpeg": {"category": "salas", "slug": "mueble-tv-madera-oscura-barra", "title": "Mueble de TV en madera oscura con barra integrada", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.19 AM.jpeg": {"category": "alcobas", "slug": "habitacion-infantil-muro-escalar", "title": "Habitación infantil con muro de escalar y estanterías", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.19 AM (1).jpeg": {"category": "alcobas", "slug": "mueble-infantil-tv-muro-escalar", "title": "Mueble infantil con TV y muro de escalar", "hero": False, "primary": False, "duplicate_of": "habitacion-infantil-muro-escalar"},
    "WhatsApp Image 2026-06-16 at 8.21.20 AM.jpeg": {"category": "alcobas", "slug": "cama-tapizada-panel-listones-instalacion", "title": "Cama tapizada con panel de listones — en instalación", "hero": False, "primary": False, "notes": "obra en progreso, colchón con plástico"},
    "WhatsApp Image 2026-06-16 at 8.21.20 AM (1).jpeg": {"category": "salas", "slug": "credenza-minimalista-madera-clara", "title": "Credenza minimalista en madera clara", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.20 AM (2).jpeg": {"category": "salas", "slug": "mueble-bar-marmol-negro-espejo", "title": "Mueble de bar con mármol negro y espejo", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.20 AM (3).jpeg": {"category": "salas", "slug": "sala-comedor-mueble-tv-vitrina", "title": "Sala y comedor con mueble TV y vitrina de vidrio", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.20 AM (4).jpeg": {"category": "salas", "slug": "bar-moderno-vista-ciudad", "title": "Bar moderno con vista panorámica de la ciudad", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.21 AM.jpeg": {"category": "salas", "slug": "bar-moderno-marmol-negro-angulo", "title": "Mueble de bar con mármol negro — ángulo vertical", "hero": False, "primary": False, "duplicate_of": "mueble-bar-marmol-negro-espejo"},
    "WhatsApp Image 2026-06-16 at 8.21.21 AM (1).jpeg": {"category": "salas", "slug": "mueble-tv-paneles-madera-repisas", "title": "Centro de entretenimiento con paneles de madera y repisas", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.21 AM (2).jpeg": {"category": "salas", "slug": "sala-comedor-mesa-marmol-vitrina", "title": "Sala y comedor con mesa de mármol y vitrina", "hero": False, "primary": False, "duplicate_of": "sala-comedor-mueble-tv-vitrina"},
    "WhatsApp Image 2026-06-16 at 8.21.21 AM (3).jpeg": {"category": "salas", "slug": "sala-comedor-amplia-mueble-tv", "title": "Sala y comedor integrados con mueble de TV", "hero": False, "primary": False, "duplicate_of": "sala-comedor-mueble-tv-vitrina"},
    "WhatsApp Image 2026-06-16 at 8.21.21 AM (4).jpeg": {"category": "salas", "slug": "mueble-tv-listones-escritorio-integrado", "title": "Mueble de TV con listones y escritorio integrado", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.21 AM (5).jpeg": {"category": "salas", "slug": "mueble-tv-listones-escritorio-angulo", "title": "Centro de entretenimiento con listones — ángulo alterno", "hero": False, "primary": False, "duplicate_of": "mueble-tv-listones-escritorio-integrado"},
    "WhatsApp Image 2026-06-16 at 8.21.22 AM.jpeg": {"category": "salas", "slug": "centro-entretenimiento-moderno-repisas", "title": "Centro de entretenimiento moderno con repisas y listones", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.22 AM (1).jpeg": {"category": "alcobas", "slug": "alcoba-panel-madera-mesas-flotantes", "title": "Alcoba con panel de madera y mesas flotantes", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.22 AM (2).jpeg": {"category": "salas", "slug": "mueble-tv-listones-escritorio-frontal", "title": "Mueble de TV con listones y escritorio — vista frontal", "hero": False, "primary": False, "duplicate_of": "mueble-tv-listones-escritorio-integrado"},
    "WhatsApp Image 2026-06-16 at 8.21.22 AM (3).jpeg": {"category": "alcobas", "slug": "alcoba-panel-madera-mesas-flotantes-angulo", "title": "Alcoba con panel de madera — ángulo alterno", "hero": False, "primary": False, "duplicate_of": "alcoba-panel-madera-mesas-flotantes"},
    "WhatsApp Image 2026-06-16 at 8.21.23 AM.jpeg": {"category": "salas", "slug": "mueble-nicho-repisas-led", "title": "Mueble empotrado con repisas e iluminación LED", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.23 AM (1).jpeg": {"category": "salas", "slug": "mueble-sala-marmol-estructura-metalica", "title": "Mueble de sala con repisa de mármol y estructura metálica", "hero": False, "primary": True, "notes": "fondo con obra, recortar al publicar"},
    "WhatsApp Image 2026-06-16 at 8.21.23 AM (2).jpeg": {"category": "salas", "slug": "lobby-olas-madera-led", "title": "Lobby con panel de olas en madera e iluminación LED", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.23 AM (3).jpeg": {"category": "salas", "slug": "credenza-flotante-verde-oliva", "title": "Credenza flotante con textura verde oliva", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.23 AM (4).jpeg": {"category": "alcobas", "slug": "dormitorio-panel-verde-mesa-noche", "title": "Dormitorio con panel verde y mesa de noche en madera", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.24 AM.jpeg": {"category": "salas", "slug": "espejo-organico-repisa-curva", "title": "Espejo orgánico con repisa flotante curva en madera", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.24 AM (1).jpeg": {"category": "salas", "slug": "consola-flotante-curva-panel-pared", "title": "Consola flotante curva con pared panelada", "hero": False, "primary": False, "duplicate_of": "espejo-organico-repisa-curva"},
    "WhatsApp Image 2026-06-16 at 8.21.24 AM (2).jpeg": {"category": "hero", "slug": "sala-moderna-panel-madera-aparador-curvo", "title": "Sala moderna con panel de madera y aparador curvo", "hero": True, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.24 AM (3).jpeg": {"category": "puertas", "slug": "puerta-corrediza-vidrio-comedor", "title": "Puerta corrediza de vidrio con panel de pared iluminado", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.24 AM (4).jpeg": {"category": "salas", "slug": "vitrina-iluminada-credenza-panel-madera", "title": "Vitrina iluminada y credenza con panel de madera", "hero": False, "primary": False, "duplicate_of": "sala-moderna-panel-madera-aparador-curvo"},
    "WhatsApp Image 2026-06-16 at 8.21.24 AM (5).jpeg": {"category": "salas", "slug": "sala-comedor-paneles-madera-amplia", "title": "Sala y comedor con paneles de madera — vista amplia", "hero": False, "primary": False, "duplicate_of": "sala-moderna-panel-madera-aparador-curvo"},
    "WhatsApp Image 2026-06-16 at 8.21.25 AM.jpeg": {"category": "salas", "slug": "mueble-tv-flotante-panel-gris", "title": "Centro de entretenimiento flotante con panel gris", "hero": False, "primary": False, "notes": "ligera desenfoque, uso secundario"},
    "WhatsApp Image 2026-06-16 at 8.21.25 AM (1).jpeg": {"category": "alcobas", "slug": "alcoba-mueble-tv-tocador-iluminado", "title": "Alcoba con mueble TV, tocador y estantería iluminada", "hero": False, "primary": True},
    "WhatsApp Image 2026-06-16 at 8.21.25 AM (2).jpeg": {"category": "salas", "slug": "mueble-pared-listones-repisas-led", "title": "Mueble de pared con listones y repisas iluminadas", "hero": False, "primary": True, "notes": "obra reciente, herramientas visibles"},
    "WhatsApp Image 2026-06-16 at 8.21.25 AM (3).jpeg": {"category": "alcobas", "slug": "alcoba-tv-espejo-retroiluminado", "title": "Alcoba con centro TV y espejo retroiluminado", "hero": False, "primary": True, "notes": "reflejo de fotógrafo en espejo"},
}

LEGACY_COCINAS = {
    "cocina KRION.jpg": {"slug": "cocina-moderna-krion-blanco-madera", "title": "Cocina integral moderna con gabinetes en madera y blanco"},
    "images.jpg": {"slug": "cocina-moderna-nogal-isla", "title": "Cocina integral en nogal con isla central"},
    "images (1).jpg": {"slug": "cocina-moderna-nogal-detalle", "title": "Cocina en nogal — detalle de gabinetes e isla"},
}

INBOX_SKIP = {"logo.png", "catalog-manifest.json", "slide2.webp", "slide3.webp", "slide4.webp"}

STOCK_REJECTED = {
    "aurdal-combinacion-de-armario-blanco__1303236_pe938336_s5.avif": "catálogo IKEA (tercero)",
    "aurdal-combinacion-de-armario-blanco__1303237_pe938338_s5.avif": "catálogo IKEA (tercero)",
    "pax-armario-esquinero-blanco__1046565_pe843036_s5.avif": "catálogo IKEA PAX (tercero)",
    "71wQyAK9HRL._AC_UF894,1000_QL80_.jpg": "imagen de catálogo Amazon (tercero)",
    "Modern-Toilet-Small-Wash-Basin-Cabinet-Designs-Bathroom-Cabinet-Single-Sink-Black-Bathroom-Vanity-with-LED-Lighted-Mirror.avif": "catálogo de producto importado (tercero)",
}

INBOX_CLASSIFICATION = {
    "taller.jpg": {"category": "empresa", "slug": "taller-artesano-lijadora", "title": "Artesano trabajando madera en taller ModulArt", "hero": False, "primary": True},
    "taller2.jpg": {"category": "servicios", "slug": "fabricacion-cepillo-mano", "title": "Fabricación artesanal con cepillo de mano", "hero": False, "primary": True, "also": "servicios/fabricacion.jpg"},
    "taller3.jpg": {"category": "empresa", "slug": "taller-maquinaria-industrial", "title": "Taller de ebanistería con maquinaria profesional", "hero": False, "primary": True},
    "images.jpg": {"category": "closets", "slug": "closet-clasico-caoba-lacado", "title": "Closet clásico en madera caoba con cajones", "hero": False, "primary": True},
    "images (1).jpg": {"category": "closets", "slug": "closet-moderno-gris-corredizo", "title": "Closet moderno en melamina gris con puertas corredizas", "hero": False, "primary": True},
    "images (2).jpg": {"category": "banos", "slug": "repisas-madera-bano", "title": "Repisas de madera para baño", "hero": False, "primary": True, "preprocess": "crop_top_text"},
    "images (3).jpg": {"category": "banos", "slug": "vanity-madera-clara-listones", "title": "Vanity de madera clara con panel de listones", "hero": False, "primary": True},
    "images (4).jpg": {"category": "banos", "slug": "vanity-madera-oscura-repisas", "title": "Vanity en madera oscura con repisas empotradas", "hero": False, "primary": True},
    "images (5).jpg": {"category": "comedores", "slug": "comedor-madera-mesa-maciza", "title": "Comedor con mesa maciza y piso de madera", "hero": False, "primary": True, "source_type": "referencia"},
    "images (6).jpg": {"category": "salas", "slug": "sala-piso-madera-mueble-tv", "title": "Sala con piso de madera y mueble de TV flotante", "hero": False, "primary": True, "source_type": "referencia"},
    "images (7).jpg": {"category": "cocinas-integrales", "slug": "cocina-moderna-piso-roble", "title": "Cocina moderna con piso de roble claro", "hero": False, "primary": True, "source_type": "referencia"},
    "closets_de_melamina.jpg": {"category": "closets", "slug": "walk-in-closet-led-melamina", "title": "Walk-in closet con iluminación LED integrada", "hero": False, "primary": True},
    "7250.jpg": {"category": "closets", "slug": "walk-in-closet-nogal-lujo", "title": "Walk-in closet en nogal con cajones y repisas", "hero": False, "primary": True},
    "sddefault.jpg": {"category": "banos", "slug": "repisas-rusticas-bano-ganchos", "title": "Repisas rústicas de madera para baño con ganchos", "hero": False, "primary": True, "preprocess": "crop_letterbox"},
    "Traditional-Engineered-Wood-Flooring.jpg": {"category": "pisos-escalas-pasamanos", "slug": "piso-madera-engineered-sala", "title": "Piso de madera engineered en sala contemporánea", "hero": False, "primary": True, "source_type": "referencia"},
    "20cc9872abfaaf56118737c0aadffa71.jpg": {"category": "alcobas", "slug": "alcoba-panel-madera-oscura-piso", "title": "Alcoba con panel de madera oscura y piso integrado", "hero": False, "primary": True, "source_type": "referencia"},
    "704_imagenMovil.png": {"category": "banos", "slug": "bano-moderno-repisas-vanity", "title": "Baño moderno con repisas y vanity en madera", "hero": False, "primary": True},
    "IMG_3492_ok_peq.avif": {"category": "banos", "slug": "bano-repisas-divisor-espejo", "title": "Baño con repisas divisoras y acabados premium", "hero": False, "primary": True},
    "135054068-1.webp": {"category": "closets", "slug": "armario-moderno-espejos-cajones", "title": "Armario moderno con espejos y cajones", "hero": False, "primary": True},
    "baño_recibidor_3.avif": {"category": "banos", "slug": "vanity-flotante-render-moderno", "title": "Vanity flotante de madera — diseño contemporáneo", "hero": False, "primary": False, "source_type": "render"},
    "w=3840,q=75.webp": {"category": "closets", "slug": "lavanderia-closets-integrados", "title": "Muebles integrados para lavandería y almacenamiento", "hero": False, "primary": True},
    "w=3840,q=75 (1).webp": {"category": "closets", "slug": "lavanderia-closets-integrados-angulo", "title": "Lavandería con closets integrados — vista lateral", "hero": False, "primary": True},
}


def enhance(img: Image.Image) -> Image.Image:
    img = ImageOps.exif_transpose(img)
    if img.mode != "RGB":
        img = img.convert("RGB")

    img = ImageOps.autocontrast(img, cutoff=0.8)

    stats = img.convert("L")
    avg = sum(stats.getdata()) / (stats.size[0] * stats.size[1])
    if avg < 115:
        img = ImageEnhance.Brightness(img).enhance(1.06)
    elif avg > 200:
        img = ImageEnhance.Brightness(img).enhance(0.97)

    img = ImageEnhance.Color(img).enhance(1.12)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Sharpness(img).enhance(1.35)
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=90, threshold=3))
    return img


def resize(img: Image.Image, is_hero: bool) -> Image.Image:
    w, h = img.size
    max_edge = 2400 if is_hero else 1920
    if max(w, h) <= max_edge:
        return img
    if w >= h:
        new_w = max_edge
        new_h = int(h * (max_edge / w))
    else:
        new_h = max_edge
        new_w = int(w * (max_edge / h))
    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)


def crop_hero_16_9(img: Image.Image) -> Image.Image:
    w, h = img.size
    target = 16 / 9
    current = w / h
    if abs(current - target) < 0.05:
        return img
    if current > target:
        new_w = int(h * target)
        left = (w - new_w) // 2
        return img.crop((left, 0, left + new_w, h))
    new_h = int(w / target)
    top = (h - new_h) // 2
    return img.crop((0, top, w, top + new_h))


def crop_letterbox(img: Image.Image, threshold: int = 28) -> Image.Image:
    gray = img.convert("L")
    w, h = gray.size
    pixels = gray.load()
    min_x, min_y, max_x, max_y = w, h, 0, 0
    for y in range(h):
        for x in range(w):
            if pixels[x, y] > threshold:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    if max_x <= min_x or max_y <= min_y:
        return img
    pad = 4
    return img.crop((
        max(0, min_x - pad),
        max(0, min_y - pad),
        min(w, max_x + pad),
        min(h, max_y + pad),
    ))


def crop_top_text_band(img: Image.Image, ratio: float = 0.12) -> Image.Image:
    w, h = img.size
    top = int(h * ratio)
    return img.crop((0, top, w, h))


def preprocess(img: Image.Image, mode: str | None) -> Image.Image:
    if mode == "crop_letterbox":
        return crop_letterbox(img)
    if mode == "crop_top_text":
        return crop_top_text_band(img)
    return img


def ensure_dirs():
    for name in [
        "_originals/whatsapp",
        "_originals/inbox",
        "_rechazadas",
        "_rechazadas/stock",
        "alcobas",
        "salas",
        "comedores",
        "puertas",
        "cocinas-integrales",
        "hero",
        "closets",
        "banos",
        "pisos-escalas-pasamanos",
        "empresa",
        "servicios",
    ]:
        (IMG / name).mkdir(parents=True, exist_ok=True)


def save_jpg(img: Image.Image, dest: Path, quality: int = 88):
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "JPEG", quality=quality, optimize=True, progressive=True)


def manifest_has_original(manifest: dict, original: str) -> bool:
    return any(i.get("original") == original for i in manifest["images"])


def unique_out_name(category: str, slug: str, used: dict[str, set[str]]) -> str:
    cat_slugs = used.setdefault(category, set())
    out_name = f"{slug}.jpg"
    if out_name in cat_slugs or (IMG / category / out_name).exists():
        i = 2
        while f"{slug}-{i:02d}.jpg" in cat_slugs:
            i += 1
        out_name = f"{slug}-{i:02d}.jpg"
    cat_slugs.add(out_name)
    return out_name


def process_classified_image(
    src: Path,
    filename: str,
    meta: dict,
    manifest: dict,
    used_slugs: dict[str, set[str]],
    archive_dir: Path,
) -> bool:
    if manifest_has_original(manifest, filename):
        print(f"SKIP already in manifest: {filename}")
        return False

    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / filename
    if not archive_path.exists() and src.exists():
        shutil.copy2(src, archive_path)

    category = meta["category"]
    slug = meta["slug"]
    out_name = unique_out_name(category, slug, used_slugs)

    img = Image.open(src)
    img = preprocess(img, meta.get("preprocess"))
    img = enhance(img)
    is_hero = meta.get("hero", False) or category == "hero"
    img = resize(img, is_hero)

    entry = {
        "id": slug,
        "original": filename,
        "category": category,
        "slug": slug,
        "filename": out_name,
        "path": f"/public/images/{category}/{out_name}",
        "title": meta["title"],
        "primary": meta.get("primary", True),
        "hero": is_hero,
        "width": img.size[0],
        "height": img.size[1],
    }
    if meta.get("duplicate_of"):
        entry["duplicate_of"] = meta["duplicate_of"]
    if meta.get("notes"):
        entry["notes"] = meta["notes"]
    if meta.get("source_type"):
        entry["source_type"] = meta["source_type"]

    if is_hero and category == "hero":
        hero_img = crop_hero_16_9(img.copy())
        hero_name = f"{slug}-hero.jpg"
        save_jpg(hero_img, IMG / "hero" / hero_name, quality=90)
        entry["hero_path"] = f"/public/images/hero/{hero_name}"
        entry["hero_width"] = hero_img.size[0]
        entry["hero_height"] = hero_img.size[1]

    save_jpg(img, IMG / category / out_name)

    if meta.get("also"):
        also_path = IMG / meta["also"]
        save_jpg(img.copy(), also_path, quality=90)

    manifest["images"].append(entry)
    print(f"OK {category}/{out_name} ({img.size[0]}x{img.size[1]})")
    return True


def process_whatsapp(manifest: dict, used_slugs: dict[str, set[str]]):
    originals = IMG / "_originals" / "whatsapp"

    for filename, meta in CLASSIFICATION.items():
        src = IMG / filename
        if not src.exists():
            continue

        if filename in REJECTED:
            if not any(r.get("original") == filename for r in manifest["rejected"]):
                shutil.copy2(src, IMG / "_rechazadas" / filename)
                manifest["rejected"].append({"original": filename, "reason": REJECTED[filename]})
            continue

        process_classified_image(src, filename, meta, manifest, used_slugs, originals)


def process_inbox(manifest: dict, used_slugs: dict[str, set[str]]):
    archive = IMG / "_originals" / "inbox"
    for filename, meta in INBOX_CLASSIFICATION.items():
        src = IMG / filename
        if not src.exists():
            continue
        process_classified_image(src, filename, meta, manifest, used_slugs, archive)

    for path in sorted(IMG.iterdir()):
        if not path.is_file():
            continue
        name = path.name
        if name in INBOX_SKIP or name in HERO_INBOX or name in INBOX_CLASSIFICATION or name in STOCK_REJECTED:
            continue
        if name in CLASSIFICATION or name in REJECTED:
            continue
        if name.startswith("WhatsApp"):
            continue
        ext = path.suffix.lower()
        if ext not in {".jpg", ".jpeg", ".png", ".webp", ".avif"}:
            continue
        if manifest_has_original(manifest, name):
            continue
        shutil.copy2(path, IMG / "_rechazadas" / "stock" / name)
        manifest["rejected"].append({"original": name, "reason": "sin clasificar — revisar manualmente"})
        print(f"REJECT unclassified: {name}")


def process_legacy_cocinas(manifest: dict, used_slugs: dict[str, set[str]]):
    legacy_dir = IMG / "çocinasintegrales"
    if not legacy_dir.exists():
        return
    for filename, meta in LEGACY_COCINAS.items():
        original = f"çocinasintegrales/{filename}"
        if manifest_has_original(manifest, original):
            continue
        src = legacy_dir / filename
        if not src.exists():
            continue
        full_meta = {
            "category": "cocinas-integrales",
            "slug": meta["slug"],
            "title": meta["title"],
            "hero": False,
            "primary": True,
        }
        process_classified_image(src, original, full_meta, manifest, used_slugs, IMG / "_originals" / "inbox")


HERO_INBOX = {
    "slide2.webp": {
        "slug": "sala-estanteria-madera-led-terracota",
        "title": "Sala moderna con estantería de madera e iluminación LED",
    },
    "slide3.webp": {
        "slug": "sala-cocina-techo-listones-terraza",
        "title": "Sala y cocina integradas con techo en listones de madera",
    },
    "slide4.webp": {
        "slug": "sala-minimalista-panel-madera-tv",
        "title": "Sala minimalista con panel de madera y mueble TV flotante",
    },
}

RETIRED_HERO_IDS = {
    "mueble-tv-sala-madera-balcon",
    "sala-tv-integrada-alcoba-listones",
    "lobby-olas-madera-led",
    "bar-moderno-vista-ciudad",
    "mueble-tv-listones-led-sala",
}

HERO_SLIDE_ORDER = [
    "sala-moderna-panel-madera-aparador-curvo",
    "sala-estanteria-madera-led-terracota",
    "sala-cocina-techo-listones-terraza",
    "sala-minimalista-panel-madera-tv",
]


def finalize_hero_slide(img: Image.Image, size: tuple[int, int] = (2400, 1350)) -> Image.Image:
    """Recorte 16:9 centrado; sube a 2400px solo si el origen lo permite."""
    hero = crop_hero_16_9(img.copy())
    w, h = hero.size
    tw, th = size
    if w >= int(tw * 0.7):
        if hero.size != size:
            hero = hero.resize(size, Image.Resampling.LANCZOS)
        return hero
    scale = min(1.35, tw / w)
    return hero.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)


def demote_retired_heroes(manifest: dict):
    """Quita del hero las imágenes retiradas y las mueve al catálogo de salas."""
    for entry in manifest["images"]:
        if entry["id"] not in RETIRED_HERO_IDS:
            continue
        entry["hero"] = False
        entry.pop("hero_path", None)
        entry.pop("hero_width", None)
        entry.pop("hero_height", None)
        if entry.get("category") == "hero":
            entry["category"] = "salas"
            old_rel = entry["path"].replace("/public/images/", "")
            old_path = IMG / old_rel
            new_path = IMG / "salas" / entry["filename"]
            if old_path.exists():
                new_path.parent.mkdir(parents=True, exist_ok=True)
                if not new_path.exists():
                    shutil.copy2(old_path, new_path)
            entry["path"] = f"/public/images/salas/{entry['filename']}"
        print(f"DEMOTE hero -> salas: {entry['id']}")


def process_hero_inbox(manifest: dict, used_slugs: dict[str, set[str]]):
    """Procesa slide2/3/4.webp como hero + copia en salas para productos."""
    archive = IMG / "_originals" / "inbox"
    archive.mkdir(parents=True, exist_ok=True)

    for filename, meta in HERO_INBOX.items():
        src = IMG / filename
        if not src.exists():
            continue

        dest_archive = archive / filename
        if not dest_archive.exists():
            shutil.copy2(src, dest_archive)

        slug = meta["slug"]
        out_name = f"{slug}.jpg"
        used_slugs.setdefault("salas", set()).add(out_name)

        img = Image.open(src)
        img = enhance(img)
        catalog_img = resize(img.copy(), is_hero=False)
        save_jpg(catalog_img, IMG / "salas" / out_name, quality=90)

        hero_img = finalize_hero_slide(img)
        hero_name = f"{slug}-hero.jpg"
        save_jpg(hero_img, IMG / "hero" / hero_name, quality=92)

        entry = {
            "id": slug,
            "original": filename,
            "category": "salas",
            "slug": slug,
            "filename": out_name,
            "path": f"/public/images/salas/{out_name}",
            "title": meta["title"],
            "primary": True,
            "hero": True,
            "width": catalog_img.size[0],
            "height": catalog_img.size[1],
            "hero_path": f"/public/images/hero/{hero_name}",
            "hero_width": hero_img.size[0],
            "hero_height": hero_img.size[1],
        }

        existing = next((i for i in manifest["images"] if i["id"] == slug), None)
        if existing:
            existing.update(entry)
        else:
            manifest["images"].append(entry)

        src.unlink(missing_ok=True)
        print(f"OK hero inbox {filename} -> {hero_name} ({hero_img.size[0]}x{hero_img.size[1]})")


def build_hero_slides(manifest: dict):
    by_id = {i["id"]: i for i in manifest["images"] if i.get("hero") and i.get("hero_path")}
    heroes = [by_id[sid] for sid in HERO_SLIDE_ORDER if sid in by_id]
    for i in manifest["images"]:
        if i.get("hero") and i.get("hero_path") and i not in heroes:
            heroes.append(i)
    slides = []
    for i, h in enumerate(heroes[:4], start=1):
        src = IMG / "hero" / Path(h["hero_path"]).name
        slide_name = f"slide-{i}.jpg"
        if src.exists():
            shutil.copy2(src, IMG / "hero" / slide_name)
            slides.append({
                "slide": i,
                "file": f"/public/images/hero/{slide_name}",
                "source": h["hero_path"],
                "title": h["title"],
            })
    manifest["hero_slides"] = slides


def recalc_counts(manifest: dict):
    cats = manifest["categories"]
    defaults = {
        "empresa": {"count": 0, "label": "Empresa / taller"},
        "servicios": {"count": 0, "label": "Servicios"},
    }
    for key, val in defaults.items():
        if key not in cats:
            cats[key] = val.copy()
    for cat in cats:
        if isinstance(cats[cat], dict):
            cats[cat]["count"] = 0
    for img in manifest["images"]:
        cat = img["category"]
        if cat in cats and isinstance(cats[cat], dict):
            cats[cat]["count"] += 1
            cats[cat].pop("status", None)


def load_manifest() -> dict:
    path = IMG / "catalog-manifest.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "version": 2,
        "generated": "2026-06-16",
        "brand": "ModulArt",
        "categories": {
            "alcobas": {"count": 0, "label": "Alcobas"},
            "salas": {"count": 0, "label": "Salas"},
            "comedores": {"count": 0, "label": "Comedores"},
            "puertas": {"count": 0, "label": "Puertas"},
            "cocinas-integrales": {"count": 0, "label": "Cocinas integrales"},
            "closets": {"count": 0, "label": "Closets"},
            "banos": {"count": 0, "label": "Baños"},
            "pisos-escalas-pasamanos": {"count": 0, "label": "Pisos, escalas y pasamanos"},
            "empresa": {"count": 0, "label": "Empresa / taller"},
            "servicios": {"count": 0, "label": "Servicios"},
            "hero": {"count": 0, "label": "Hero / portada"},
        },
        "images": [],
        "rejected": [],
        "hero_slides": [],
        "pending_categories": [],
    }


def archive_stock_rejected(manifest: dict):
    stock_dir = IMG / "_rechazadas" / "stock"
    stock_dir.mkdir(parents=True, exist_ok=True)
    for filename, reason in STOCK_REJECTED.items():
        src = IMG / filename
        if not src.exists():
            continue
        if not any(r.get("original") == filename for r in manifest["rejected"]):
            shutil.copy2(src, stock_dir / filename)
            manifest["rejected"].append({"original": filename, "reason": reason})
            print(f"REJECT stock: {filename}")
        src.unlink(missing_ok=True)


def cleanup_inbox_root():
    archive = IMG / "_originals" / "inbox"
    for filename in list(INBOX_CLASSIFICATION.keys()) + list(STOCK_REJECTED.keys()):
        src = IMG / filename
        if src.exists():
            dest = archive / filename
            if not dest.exists():
                shutil.copy2(src, dest)
            src.unlink(missing_ok=True)
    tmp = IMG / "_tmp_preview"
    if tmp.exists():
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ensure_dirs()
    manifest = load_manifest()
    used_slugs: dict[str, set[str]] = {}
    for img in manifest["images"]:
        used_slugs.setdefault(img["category"], set()).add(img.get("filename", ""))

    process_whatsapp(manifest, used_slugs)
    process_legacy_cocinas(manifest, used_slugs)
    archive_stock_rejected(manifest)
    process_inbox(manifest, used_slugs)
    demote_retired_heroes(manifest)
    process_hero_inbox(manifest, used_slugs)
    build_hero_slides(manifest)
    recalc_counts(manifest)

    pending = []
    for cat, info in manifest["categories"].items():
        if isinstance(info, dict) and info.get("count", 0) == 0 and cat not in {"hero"}:
            pending.append(cat)
    manifest["pending_categories"] = pending
    manifest["version"] = 2

    manifest_path = IMG / "catalog-manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    cleanup_inbox_root()
    print(f"\nManifest: {manifest_path}")
    print("Done.")


if __name__ == "__main__":
    main()
