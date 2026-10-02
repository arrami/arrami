# Procédure de Conversion d'Images avec Docling

Ce document sert d'aide-mémoire pour réactiver l'environnement et lancer la conversion en lot des images du dossier `aide-memoire` en fichiers textuels structurés (Markdown).

## 1. Réactivation de l'environnement virtuel

À chaque réouverture du terminal (PowerShell), exécuter les commandes suivantes pour se repositionner dans le projet et activer Docling :

```powershell
# Se déplacer dans le dossier du projet
cd C:\Users\User\Projets\Docling

# Activer l'environnement virtuel
.\venv\Scripts\activate
```
*Note : Le préfixe `(venv)` doit apparaître au début de la ligne de commande.*

## 2. Commande de conversion en lot (Bulk)

Pour analyser toutes les images du Bureau et extraire leur texte dans un dossier de résultats dédié :

```powershell
docling C:\Users\User\Desktop\aide-memoire --to md --output C:\Users\User\Desktop\aide-memoire-resultats
```

### Fonctionnement :
- Les images d'origine restent inchangées dans `aide-memoire`.
- Un dossier `aide-memoire-resultats` est automatiquement créé sur le Bureau.
- Chaque image génère un fichier texte `.md` individuel portant le même nom.

## 3. Vérification du nombre de fichiers

Une fois que Docling a terminé son exécution et rendu la main au terminal, exécuter cette commande pour s'assurer que les **105 fichiers** ont correctement été générés :

```powershell
(Get-ChildItem C:\Users\User\Desktop\aide-memoire-resultats -Filter *.md).Count
```

## 4. Quitter l'environnement (Optionnel)

Pour désactiver l'environnement virtuel sans fermer la fenêtre du terminal :

```powershell
deactivate
```