import re
from pathlib import Path

# Dossier où se trouvent vos fichiers .md actuels
dossier_md = Path("C:/Users/User/Desktop/aide-memoire-resultats")
# Dossier où seront créés vos fichiers .txt propres
dossier_txt = Path("C:/Users/User/Desktop/aide-memoire-txt")
dossier_txt.mkdir(exist_ok=True)

# Expression régulière pour détecter et cibler le code des images
pattern_image = r"!\[Image\]\(data:image\/[^)]+\)"

fichiers_md = list(dossier_md.glob("*.md"))
print(f"🧹 Nettoyage de {len(fichiers_md)} fichiers Markdown...")

for fichier in fichiers_md:
    # 1. Lire le contenu du fichier .md
    contenu = fichier.read_text(encoding="utf-8")

    # 2. Supprimer tout le texte d'image bizarre (base64)
    contenu_propre = re.sub(pattern_image, "", contenu)

    # 3. Nettoyer les sauts de lignes en trop qui resteraient (Correction ici)
    contenu_propre = re.sub(r"\n{3,}", "\n\n", contenu_propre).strip()

    # 4. Sauvegarder en .txt
    fichier_sortie = dossier_txt / f"{fichier.stem}.txt"
    fichier_sortie.write_text(contenu_propre, encoding="utf-8")

print("🎉 Terminé ! Vos 105 fichiers textuels propres sont dans le dossier : 'aide-memoire-txt'")
