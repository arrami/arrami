# Audit E-E-A-T en lot pour un blog WordPress

Ce script Python analyse en lot les articles publiés d'un blog WordPress et produit un classeur Excel pré-rempli qui reprend la grille E-E-A-T pondérée. Les notes proposées restent **des suggestions** : la note finale est humaine, à relire et corriger dans les cellules jaunes du classeur. Il reprend les règles de la page interactive et exporte un classeur au même format que le tableur.

## Installation (une fois)

```bash
pip install openpyxl
```

Python 3.9 ou plus récent est requis.

## Utilisation

```bash
python audit_eeat_wordpress.py https://votreblog.fr
python audit_eeat_wordpress.py https://votreblog.fr --max 50 --out rapport.xlsx
python audit_eeat_wordpress.py --json articles.json
```

La troisième commande sert si l'API du site est bloquée : vous exportez les articles en JSON d'une autre façon, puis vous lancez l'analyse hors ligne.

### Options

| Option   | Description                                                          | Défaut                       |
|----------|----------------------------------------------------------------------|------------------------------|
| `site`   | URL du site WordPress (positionnel, ex. `https://monblog.fr`)        | —                            |
| `--json` | Fichier JSON d'articles (format de l'API WordPress) au lieu du site  | —                            |
| `--max`  | Nombre maximum d'articles à récupérer                                | `50`                         |
| `--out`  | Nom du fichier Excel de sortie                                       | `audit-eeat-AAAA-MM-JJ.xlsx` |

Si ni `site` ni `--json` ne sont fournis, le script s'arrête avec un message.

## Ce qu'il fait

- Il récupère les articles publiés via l'API REST de WordPress (`/wp-json/wp/v2/posts`), page par page, avec une courte pause entre les appels.
- Il analyse le **HTML** de chaque article, ce qui lui permet de voir les vrais liens et les vrais titres.
- Il applique les contrôles automatiques de la grille pondérée : preuve d'expérience (témoignages à la première personne, outils nommés, résultats chiffrés), traçabilité des sources (chiffres liés ou non, formules d'auto-protection), cohérence temporelle (années postérieures à la publication, données « annuelles » sur une année non terminée, études de l'année en cours), intégrité de la structure (sections trop courtes, promesses de listes non tenues, texte tronqué), densité et valeur ajoutée (formules creuses, phrases répétées) et signaux auteur et site (non détectables automatiquement).
- Il crée un fichier Excel avec **quatre onglets** : **Audit** (notes suggérées pour les cinq premiers critères, « Date impossible » pré-rempli, score, verdict et trois alertes principales ; chaque note porte un commentaire qui explique pourquoi elle a été suggérée), **Synthèse** (rapport de conformité), **Signaux** (chaque phrase repérée, filtrable par article ou par critère) et **Paramètres** (poids et seuils).
- Dans le terminal, il affiche les cinq articles les plus faibles.

## Ce que le script ne peut pas juger

Trois éléments demandent une vérification humaine et ne sont **pas** remplis automatiquement : **Auteur / site** (bio, profil, mentions légales, page « À propos »…), **Stat introuvable** (chiffre présent mais impossible à sourcer) et **Faux témoignage** (expérience inventée ou invérifiable). Tant que vous ne les avez pas remplis, la ligne reste marquée « **Provisoire** », et la note « Auteur / site » vaut **1** par défaut. Vous pouvez modifier cette valeur par défaut dans l'onglet **Paramètres**.

## Limites pratiques

- **API REST bloquée** : certains sites désactivent l'API REST ou la protègent derrière un pare-feu. Dans ce cas, le script affiche l'erreur HTTP correspondante. L'option `--json` sert alors de solution de repli.
- **Langue** : les règles de détection sont écrites pour des textes en **français**. Sur un blog anglophone ou multilingue, les heuristiques (formules creuses, hedges, mois, etc.) seront moins pertinentes.

## Format attendu du fichier JSON (`--json`)

Le fichier doit contenir une **liste** d'objets au format de l'API WordPress :

```json
[
  {
    "link": "https://monblog.fr/article-1",
    "title": { "rendered": "Titre de l'article" },
    "date": "2024-03-12T10:00:00",
    "modified": "2024-04-02T09:30:00",
    "content": { "rendered": "<p>Contenu HTML…</p>" },
    "_embedded": { "author": [ { "name": "Prénom Nom" } ] }
  }
]
```

Les champs `author_name` et `content` en chaîne simple sont également acceptés si vous produisez le JSON à la main.

## Licence

Usage interne / audit éditorial. Adaptez les listes (`PLUGINS`, `BRANDS`, `HEDGES`, `CLICHES`) à votre secteur avant de lancer un audit de masse.