---
title: "Template de Fiche Définition - Architecture IA & Web"
date: 2026-09-25
category: "Templates & Prompts"
tags: ["prompt", "template", "fiche-definition", "architecture", "IA", "web"]
description: "Prompt template pour générer des fiches définition techniques complètes sur les architectures IA et web."
---

# Prompt Template : Fiche Définition Architecture IA & Web

Agis comme un expert en architecture de l'information, en structuration des connaissances numériques et en accessibilité web (RGAA/WCAG).

Ta tâche est de rédiger une fiche définition technique et opérationnelle complète sur le sujet suivant : "[INSÉRER LE SUJET ICI]".

## Contraintes de format STRICTES

1. Fournis la réponse dans un SEUL bloc de code Markdown, en utilisant 4 backticks (````markdown ... ````) pour l'enveloppe externe, afin d'éviter toute coupure avec les 3 backticks du bloc Mermaid interne.
2. Ne coupe jamais le texte. Fournis l'intégralité du document d'un seul tenant, de la première à la dernière ligne.
3. Remplace le mot "paradigme" par des termes plus accessibles comme "mode d'interaction", "nouvelle façon de concevoir" ou "approche".
4. Le nom du fichier généré doit suivre le format : `sujet-en-kebab-case.md` (ex: `generative-ui.md`, `agentic-ux-chat-first.md`).

## Structure obligatoire du document

1. **En-tête YAML (Frontmatter)** avec : title, date (2026-09-25), category: "Architecture IA & Web", tags (5-7 tags pertinents), description.

2. **Section 1 : Définition courte (Opérationnelle)** + une citation "Synthèse" en blocquote.

3. **Section 2 : Définition longue (Contextuelle et Méthodologique)** avec 4 sous-parties :
   - Fonctionnement architectural
   - Enjeux d'accessibilité (RGAA/WCAG)
   - Enjeux d'Architecture de l'Information et SEO
   - IA Responsable et Éthique

4. **Section 3 : Architecture Technique et Stack**. Inclure un diagramme Mermaid (flowchart TD) avec des `subgraph` pour chaque couche. La stack technique (outils et rôles) doit être écrite DIRECTEMENT dans les nœuds du diagramme Mermaid pour éviter toute redondance avec un tableau. Utilise des `classDef` pour le style (layer, component, data, security).

5. **Section 4 : Flux d'exécution typique** (exemple concret en 5-6 étapes numérotées).

6. **Section 5 : Points de Vigilance Méthodologiques** (6 points numérotés : Sécurité, Gestion des erreurs, Coûts, Accessibilité non négociable, Transparence, Tests et évaluation).

7. **Section 6 : Recommandations de Démarrage** (sous-sections "Pour un MVP" et "Pour une mise en production").

8. **Note de bas de page** en italique soulignant que la fiche est un "artefact d'architecture de l'information vivant".

## Ton et style

Professionnel, précis, structuré, orienté action et maintenabilité. Pas de jargon académique inutile. Privilégier la clarté et l'opérationalité.