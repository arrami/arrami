# 📊 dataviz-seo

**Suite d'outils CLI _local-first_ en Python pur** pour l'analyse SEO, la visualisation et le diagnostic de visibilité organique.

Ensemble de modules indépendants, chacun conçu pour résoudre un problème SEO spécifique. Combinez-les pour des audits complets ou utilisez-les isolément selon vos besoins.

---

## 🎯 Vision

Fournir aux SEO et développeurs une **boîte à outils modulaire**, sans dépendance cloud, sans authentification Google complexe, prête pour l'**audit terrain**, la **pédagogie** et le **diagnostic rapide**.

---

## 🏗️ Architecture

```text
dataviz-seo/
│
├── README.md                  # Ce fichier (overview global)
├── requirements.txt           # Dépendances globales (optionnel)
├── LICENSE
│
├── plot/                      # Module: Matrice 4D GSC × Crawl
│   ├── README.md              # Documentation module
│   ├── requirements.txt        # Dépendances spécifiques
│   ├── plot-seo.py            # Script principal CLI
│   ├── utils.py               # Fonctions utilitaires
│   ├── visualizer.py          # Engine matplotlib
│   │
│   └── data/
│       ├── sample-gsc.csv     # Données test GSC
│       ├── sample-crawl.csv   # Données test crawl
│       └── expected-output.png
│
├── export/                    # Module: Export & normalisation GSC (futur)
│   ├── README.md
│   └── export-gsc.py
│
├── depth-analyzer/            # Module: Analyse profondeur structurelle (futur)
│   ├── README.md
│   └── analyze-depth.py
│
└── docs/                      # Documentation générale
    ├── ARCHITECTURE.md
    ├── CONTRIBUTING.md
    └── CHANGELOG.md
```

---

## 📦 Modules disponibles

### ✅ Matrice 4D (`plot/`)

**Status:** Production-ready

Visualize 4 dimensions SEO en une bulle chart interactive:

- **X:** Position moyenne SERP
- **Y:** Clics GSC
- **Taille:** Impressions
- **Couleur:** Profondeur de crawl

**Utilisation:**

```bash
cd plot
python plot-seo.py data/sample-gsc.csv
# ou avec crawl:
python plot-seo.py data/sample-gsc.csv --crawl data/sample-crawl.csv
```

👉 **Documentation complète:** [`plot/README.md`](plot/README.md)

---

### 🔜 Export GSC (futur)

Normalisation et export structuré des données Google Search Console.

### 🔜 Depth Analyzer (futur)

Analyse de profondeur structurelle et impact sur l'indexation.

---

## 🚀 Quick Start

### Installation

```bash
# 1. Cloner le repo
git clone https://github.com/username/dataviz-seo.git
cd dataviz-seo

# 2. Installer module spécifique
cd plot
pip install -r requirements.txt

# 3. Exécuter
python plot-seo.py data/sample-gsc.csv
```

### Premiers pas

```bash
# Mode autonome (GSC seul)
python plot/plot-seo.py plot/data/sample-gsc.csv

# Mode complet (GSC + Crawl)
python plot/plot-seo.py plot/data/sample-gsc.csv --crawl plot/data/sample-crawl.csv

# Généré: plot/sample-gsc-matrix.png
```

---

## 🎓 Guide modules

| Module             | Objective                | Input                 | Output             | Durée |
| ------------------ | ------------------------ | --------------------- | ------------------ | ----- |
| **plot**           | Matrice 4D visualisation | CSV GSC + (CSV Crawl) | PNG/SVG            | 2-5s  |
| **export**         | Normalisation GSC        | GSC natif             | CSV/JSON structuré | <1s   |
| **depth-analyzer** | Impact profondeur        | CSV Crawl             | Rapport + viz      | 5-10s |

---

## 💡 Cas d'usage

### Diagnostic rapide site e-commerce

```bash
cd plot
python plot-seo.py /path/to/ecommerce-gsc.csv
→ Identifie produits invisibles malgré potentiel élevé
```

### Audit structure blog + GSC

```bash
cd plot
python plot-seo.py blog-gsc.csv --crawl blog-crawl.csv
→ Révèle orphelins, impact architecture, profondeur excessive
```

### Formation/Pédagogie

```bash
cd plot
python plot-seo.py student-case.csv
→ Montre relation position/clics/impressions de façon visuelle
```

---

## 🔧 Configuration globale

### Python requis

- Python ≥ 3.8
- pip

### Structure de données

Chaque module documente ses formats spécifiques. Voir [`plot/README.md`](plot/README.md#📊-formats-supportés--normalisation) pour la matrice.

---

## 📚 Documentation

- **[Plot Module](plot/README.md)** - Matrice 4D détails
- **[Architecture](docs/ARCHITECTURE.md)** - Vue technique globale
- **[Contributing](docs/CONTRIBUTING.md)** - Comment contribuer
- **[Changelog](docs/CHANGELOG.md)** - Historique versions

---

## 🛣️ Roadmap

### v1.0.0 (Actuel)

- ✅ Module plot (matrice 4D)
- ✅ Support GSC natif + crawl générique
- ✅ CLI standalone

### v1.1.0 (Prochain)

- 🔜 Module export (normalisation GSC)
- 🔜 Rapports markdown auto-générés
- 🔜 Support API GSC native (optionnel)

### v2.0.0 (Futur)

- 🔜 Interface web Streamlit
- 🔜 Visualisations interactives Plotly
- 🔜 Module depth-analyzer
- 🔜 Intégration multi-crawlers
- 🔜 Recommandations IA

---

## 🤝 Contribution

Les contributions sont bienvenues! Voir [CONTRIBUTING.md](docs/CONTRIBUTING.md) pour:

- Code style guide
- Pull request process
- Reporting bugs

Processus rapide:

```bash
git checkout -b feature/my-feature
# ... make changes ...
git commit -m "Add my feature"
git push origin feature/my-feature
# → Open PR
```

---

## 📄 Licence

MIT License - voir [LICENSE](LICENSE)

---

## 👨‍💻 Auteur

**[Stéphane ARRAMI]**

- 🐦 [@twitter](https://twitter.com/stephanearrami)
- 💼 [LinkedIn](https://linkedin.com/in/stephane-arrami)
- 🌐 [Site](https://stephane-arrami.com)
- 🌐 [Studio](https://citywizz.com)

---

## 💬 Support

- **GitHub Issues** - Bug reports & feature requests
- **GitHub Discussions** - Questions & idées
- **Email** - contact@citywizz.com

---

**Dernière mise à jour:** Septembre 2026
**Status:** ✅ Production-ready (v1.0.0)
