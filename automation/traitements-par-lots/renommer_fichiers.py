#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Renomme les fichiers :
  1. retire les accents (é -> e, à -> a, ç -> c, œ -> oe...)
  2. remplace les espaces et apostrophes par des tirets (-)

Exemples :
  "Bienvenue Rencontre ODTE.jpeg"        -> "Bienvenue-Rencontre-ODTE.jpeg"
  "Décor artisanat traditionnel .jpeg"   -> "Decor-artisanat-traditionnel.jpeg"
  "Diaspora-Europe-veillée.jpeg"         -> "Diaspora-Europe-veillee.jpeg"
  "Atelier-Tifinagh Rencontre-ODTE 08 2026.jpeg" -> "Atelier-Tifinagh-Rencontre-ODTE-08-2026.jpeg"

Utilisation :
  python renommer_espaces.py                   -> dossier courant, aperçu puis confirmation
  python renommer_espaces.py "C:\\mes photos"  -> dossier précis
  python renommer_espaces.py dossier -r        -> inclut les sous-dossiers
  python renommer_espaces.py dossier -y        -> renomme sans demander confirmation
"""

import argparse
import re
import sys
import unicodedata
from pathlib import Path


LIGATURES = {"œ": "oe", "Œ": "OE", "æ": "ae", "Æ": "AE", "ß": "ss"}


def sans_accents(texte: str) -> str:
    """Retire les accents : "Décor veillée" -> "Decor veillee"."""
    for k, v in LIGATURES.items():
        texte = texte.replace(k, v)
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def nouveau_nom(nom: str) -> str:
    """Calcule le nom corrigé d'un fichier."""
    p = Path(sans_accents(unicodedata.normalize("NFC", nom)))
    base, ext = p.stem, p.suffix

    # Espaces (y compris insécables) et apostrophes -> tiret
    base = re.sub(r"[\s\u00A0'’]+", "-", base.strip())
    # Plusieurs tirets d'affilée -> un seul ("ODTE - 2026" -> "ODTE-2026")
    base = re.sub(r"-{2,}", "-", base)
    # Pas de tiret au début ni à la fin du nom
    base = base.strip("-")

    ext = ext.replace(" ", "")
    return (base or "fichier") + ext


def nom_disponible(dossier: Path, nom: str) -> str:
    """Évite d'écraser un fichier existant en ajoutant -1, -2, ..."""
    cible = dossier / nom
    if not cible.exists():
        return nom
    p = Path(nom)
    i = 1
    while (dossier / f"{p.stem}-{i}{p.suffix}").exists():
        i += 1
    return f"{p.stem}-{i}{p.suffix}"


def main():
    parser = argparse.ArgumentParser(description="Retire les accents et remplace les espaces par des tirets dans les noms de fichiers.")
    parser.add_argument("dossier", nargs="?", default=".", help="Dossier à traiter (par défaut : dossier courant)")
    parser.add_argument("-r", "--recursif", action="store_true", help="Traiter aussi les sous-dossiers")
    parser.add_argument("-y", "--oui", action="store_true", help="Renommer sans demander confirmation")
    args = parser.parse_args()

    dossier = Path(args.dossier).expanduser().resolve()
    if not dossier.is_dir():
        print(f"Dossier introuvable : {dossier}")
        sys.exit(1)

    fichiers = dossier.rglob("*") if args.recursif else dossier.iterdir()
    a_renommer = []
    for f in sorted(fichiers):
        if f.is_file() and not f.name.startswith("."):
            nouveau = nouveau_nom(f.name)
            if nouveau != f.name and unicodedata.normalize("NFC", nouveau) != unicodedata.normalize("NFC", f.name):
                a_renommer.append((f, nouveau))

    if not a_renommer:
        print("Aucun fichier à renommer.")
        return

    print(f"{len(a_renommer)} fichier(s) à renommer dans {dossier} :\n")
    for f, nouveau in a_renommer:
        print(f"  {f.name}\n    -> {nouveau}")

    if not args.oui:
        rep = input("\nConfirmer le renommage ? (o/n) : ").strip().lower()
        if rep not in ("o", "oui", "y", "yes"):
            print("Annulé, rien n'a été modifié.")
            return

    ok = 0
    for f, nouveau in a_renommer:
        nouveau = nom_disponible(f.parent, nouveau)
        try:
            f.rename(f.parent / nouveau)
            ok += 1
        except OSError as e:
            print(f"Erreur sur « {f.name} » : {e}")

    print(f"\nTerminé : {ok}/{len(a_renommer)} fichier(s) renommé(s).")


if __name__ == "__main__":
    main()