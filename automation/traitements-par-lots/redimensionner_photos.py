#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Redimensionne et optimise les photos d'un dossier, en traitant à part
les photos en paysage (plus larges que hautes) et en portrait.

Les originaux ne sont JAMAIS modifiés : les nouvelles images vont dans
un sous-dossier (par ex. "web/").

Ce que fait le script pour chaque photo :
  - remet la photo dans le bon sens (photos de téléphone tournées) ;
  - redimensionne selon le format choisi (sans jamais agrandir) ;
  - retire les métadonnées (position GPS, modèle de téléphone...) ;
  - enregistre en JPEG optimisé (et en WebP si demandé) ;
  - nettoie le nom : sans accents, espaces remplacés par des tirets.

Installation (une seule fois) :
  pip install pillow

Utilisation :
  python redimensionner_photos.py                    -> format "web", dossier courant
  python redimensionner_photos.py "C:\\Photos ODTE"  -> dossier précis
  python redimensionner_photos.py -f email           -> autre format (web, hd, reseaux, email, archive)
  python redimensionner_photos.py -f web --webp      -> ajoute aussi une version WebP
  python redimensionner_photos.py -q 85              -> qualité JPEG personnalisée (1-95)
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    print("La bibliothèque Pillow est nécessaire. Installez-la avec :  pip install pillow")
    sys.exit(1)


# Taille maximale en pixels : (largeur max, hauteur max)
FORMATS = {
    #           paysage        portrait      qualité   usage
    "web":     ((1280, 960),  (720, 1280),  80),   # site web : 1280 de large / 720 de large en portrait
    "hd":      ((1920, 1080), (1080, 1920), 82),   # grand écran, diaporama plein écran
    "reseaux": ((1080, 1080), (1080, 1350), 85),   # Facebook, Instagram, WhatsApp statut
    "email":   ((1024, 768),  (576, 1024),  78),   # pièce jointe, WhatsApp
    "archive": ((3000, 2000), (2000, 3000), 90),   # bonne qualité, tirage A4
}

EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp", ".heic"}
LIGATURES = {"œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE", "ß": "ss"}


def nom_propre(nom: str) -> str:
    """'Décor artisanat .jpeg' -> 'Decor-artisanat'"""
    texte = unicodedata.normalize("NFC", Path(nom).stem)
    for k, v in LIGATURES.items():
        texte = texte.replace(k, v)
    texte = "".join(c for c in unicodedata.normalize("NFD", texte)
                    if unicodedata.category(c) != "Mn")
    texte = re.sub(r"[\s\u00A0'’]+", "-", texte.strip())
    texte = re.sub(r"-{2,}", "-", texte).strip("-")
    return texte or "photo"


def traiter(fichier: Path, sortie: Path, fmt: str, qualite: int, webp: bool):
    (max_paysage, max_portrait, _) = FORMATS[fmt]

    with Image.open(fichier) as img:
        img = ImageOps.exif_transpose(img)          # bon sens de la photo
        largeur, hauteur = img.size
        orientation = "paysage" if largeur >= hauteur else "portrait"
        limite = max_paysage if orientation == "paysage" else max_portrait

        img.thumbnail(limite, Image.LANCZOS)        # garde les proportions, n'agrandit jamais

        if img.mode not in ("RGB", "L"):            # transparence PNG -> fond blanc
            fond = Image.new("RGB", img.size, "white")
            if "A" in img.getbands():
                fond.paste(img, mask=img.getchannel("A"))
            else:
                fond.paste(img.convert("RGB"))
            img = fond

        base = nom_propre(fichier.name)
        cible = sortie / f"{base}.jpg"
        i = 1
        while cible.exists():
            cible = sortie / f"{base}-{i}.jpg"
            i += 1

        # Pas d'exif passé -> métadonnées (GPS...) retirées
        img.save(cible, "JPEG", quality=qualite, optimize=True, progressive=True)
        if webp:
            img.save(cible.with_suffix(".webp"), "WEBP", quality=qualite - 2, method=6)

    return orientation, (largeur, hauteur), img.size, cible


def main():
    parser = argparse.ArgumentParser(description="Redimensionne et optimise les photos (paysage / portrait).")
    parser.add_argument("dossier", nargs="?", default=".", help="Dossier des photos (par défaut : dossier courant)")
    parser.add_argument("-f", "--format", choices=FORMATS.keys(), default="web", help="Format de sortie (défaut : web)")
    parser.add_argument("-q", "--qualite", type=int, help="Qualité JPEG 1-95 (défaut selon le format)")
    parser.add_argument("--webp", action="store_true", help="Créer aussi une version WebP (plus légère, pour le web)")
    parser.add_argument("-o", "--sortie", help="Dossier de sortie (défaut : sous-dossier au nom du format)")
    args = parser.parse_args()

    dossier = Path(args.dossier).expanduser().resolve()
    if not dossier.is_dir():
        print(f"Dossier introuvable : {dossier}")
        sys.exit(1)

    qualite = args.qualite or FORMATS[args.format][2]
    sortie = Path(args.sortie).resolve() if args.sortie else dossier / args.format
    sortie.mkdir(parents=True, exist_ok=True)

    photos = sorted(f for f in dossier.iterdir()
                    if f.is_file() and f.suffix.lower() in EXTENSIONS)
    if not photos:
        print("Aucune photo trouvée.")
        return

    p, l, q = FORMATS[args.format][0], FORMATS[args.format][1], qualite
    print(f"Format « {args.format} » : paysage max {p[0]}x{p[1]}, portrait max {l[0]}x{l[1]}, qualité {q}")
    print(f"{len(photos)} photo(s) -> {sortie}\n")

    avant_total = apres_total = 0
    for f in photos:
        try:
            orient, (w0, h0), (w1, h1), cible = traiter(f, sortie, args.format, qualite, args.webp)
            avant, apres = f.stat().st_size, cible.stat().st_size
            avant_total += avant
            apres_total += apres
            print(f"  [{orient:8}] {f.name}\n             {w0}x{h0} -> {w1}x{h1}   "
                  f"{avant/1e6:.1f} Mo -> {apres/1e6:.2f} Mo   ({cible.name})")
        except Exception as e:
            print(f"  ERREUR sur « {f.name} » : {e}")

    if avant_total:
        gain = 100 * (1 - apres_total / avant_total)
        print(f"\nTerminé : {avant_total/1e6:.1f} Mo -> {apres_total/1e6:.1f} Mo (gain {gain:.0f} %)")


if __name__ == "__main__":
    main()
