# 📊 Module `plot` - Matrice 4D GSC × Crawl

**CLI local pour générer une bulle chart 4D** croisant Search Console et données de crawl structurel.

Visualise en un graphique:
- **Axe X:** Position moyenne SERP
- **Axe Y:** Clics GSC  
- **Taille:** Impressions GSC
- **Couleur:** Profondeur de crawl

---

## 📋 Prérequis

```bash
pip install -r requirements.txt
```

Dépendances:
- `pandas` ≥ 1.3.0
- `matplotlib` ≥ 3.4.0
- `numpy` ≥ 1.21.0

Python ≥ 3.8 requis.

---

## 🚀 Utilisation

### Mode autonome (GSC seul)
```bash
python plot-seo.py data/sample-gsc.csv
```
Génère: `sample-gsc-matrix.png`  
Profondeur estimée via slashes URL.

### Mode croisé (GSC + Crawl)
```bash
python plot-seo.py data/sample-gsc.csv --crawl data/sample-crawl.csv
```
Génère: `sample-gsc-crawl-matrix.png`  
Profondeur réelle du crawler.

### Options
```bash
# Output custom
python plot-seo.py data.csv -o my-viz.png

# Format SVG (vecteur)
python plot-seo.py data.csv --format svg

# Limiter à 500 URLs
python plot-seo.py data.csv --limit 500

# Seuil impressions minimum (défaut: 10)
python plot-seo.py data.csv --min-impressions 5

# Logs détaillés
python plot-seo.py data.csv --verbose
```

---

## 📊 Formats supportés

### Google Search Console
En-têtes attendus:
- `Top pages` → URLs
- `Clicks` → Clics organiques
- `Impressions` → Impressions SERP
- `Average position` → Position moyenne

**Format natif GSC:**
```csv
Top pages,Clicks,Impressions,Average position
/,45,1200,2.3
/blog/post-1,30,800,5.2
```

### Crawl data
En-têtes supportés:
- URL: `Address`, `URL`, `url`, `path`
- Profondeur: `Depth`, `depth`, `level`, `distance`

**Exemple:**
```csv
Address,Depth
https://example.com/,0
https://example.com/blog/2024/post,3
```

---

## 🧪 Données test

Fichiers d'exemple inclus:
- `data/sample-gsc.csv` - Export GSC (250 lignes)
- `data/sample-crawl.csv` - Crawl données (5000 lignes)
- `data/expected-output.png` - Résultat attendu

```bash
# Tester immédiatement
python plot-seo.py data/sample-gsc.csv
python plot-seo.py data/sample-gsc.csv --crawl data/sample-crawl.csv
```

---

## 🔍 Troubleshooting

**Erreur `ModuleNotFoundError`:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Fusion crawl/GSC → 0 URLs:**
- Vérifier normalisation URLs (http/https, www, trailing slash)
- Utiliser `--verbose` pour debug

**Output vide:**
- Vérifier seuil impressions minimum
- Données peut-être filtrées entièrement
- Utiliser `--min-impressions 1` pour inclure tout

---

## 📈 Lecture des résultats

| Position | Clics | Bulles |
|---|---|---|
| Gauche (position ≤10) | Haut (clics élevés) | ✅ Jackpot |
| Gauche | Bas | 💡 Opportunité (bien exposé, mal ranké) |
| Droite (position >10) | Bas | ⚠️ Problème ranking |
| Foncé (depth 4+) | N/A | 🔴 Structurellement lointain |

---

## 📁 Structure

```
plot/
├── README.md               # Ce fichier
├── requirements.txt        # Dépendances
├── plot-seo.py            # Entry point CLI
├── utils.py               # Parsing & normalisation
├── visualizer.py          # Engine matplotlib
└── data/
    ├── sample-gsc.csv
    ├── sample-crawl.csv
    └── expected-output.png
```

---

## 🔧 Développement

### Tests
```bash
python -m pytest tests/
```

### Format code
```bash
black plot-seo.py utils.py visualizer.py
```

---

## 📝 Notes

- **Normalisation URLs:** strip() + suppression trailing slash
- **Fusion:** Inner join sur URL normalisée
- **Filtrage:** Min 10 impressions (configurable), top 300 URLs
- **Export:** PNG (défaut) ou SVG

---

**Version:** 1.0.0  
**Status:** ✅ Production-ready
