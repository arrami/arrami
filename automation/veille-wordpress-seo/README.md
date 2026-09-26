# 🤖 Veille Technologique & SEO Automatisée avec n8n

Ce dépôt présente un workflow d'automatisation sous **n8n** conçu pour collecter des flux RSS, les structurer et générer un rapport de veille quotidien au format Markdown sur un serveur distant, en suivant une architecture de configuration découplée.

## 🏗️ Architecture & Sécurité

* **Séparation Code / Données :** Le workflow n8n est public, mais les sources de veille réelles sont isolées dans un fichier de configuration local non versionné (`veille-wordpress-seo.json`).
* **Optimisation Stockage :** Le système génère un unique fichier récapitulatif par jour (`veille-AAAA-MM-JJ.md`), évitant toute saturation du serveur.
* **Double Déclencheur :** Automatisation planifiée (Schedule) et déclenchement manuel pour les phases de test.

## ⚙️ Déploiement

1. Importez le fichier `workflow.json` dans votre instance n8n.
2. Dupliquez le modèle de configuration :
   ```bash
   cp veille-wordpress-seo.example.json veille-wordpress-seo.json