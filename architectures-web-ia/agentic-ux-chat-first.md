---
title: "Agentic UX & Chat-First"
date: 2026-09-25
category: "Architecture IA & Web"
tags: ["IA", "UX", "Agentique", "Chat-First", "LLM", "Architecture", "Tool Calling", "RAG"]
description: "Fiche définition et stack technique de l'Agentic UX et des interfaces conversationnelles en premier lieu."
---

# Fiche Définition : Agentic UX & Chat-First

## 1. Définition courte (Opérationnelle)

L'**Agentic UX** désigne un mode d'interaction où le système numérique agit comme un agent (semi-)autonome capable de planifier, d'utiliser des outils et d'exécuter des tâches complexes pour atteindre un objectif défini par l'utilisateur, sans nécessiter de micro-gestion.

L'approche **Chat-First** place l'interface conversationnelle (texte ou voix) comme point d'entrée principal ou unique de cette interaction, remplaçant la navigation hiérarchique traditionnelle (menus, arborescence) par l'expression directe d'une intention.

> **Synthèse** : L'utilisateur ne *navigue* plus pour trouver un outil ; il *énonce* un but, et l'agent conversationnel orchestre les actions pour l'atteindre.

---

## 2. Définition longue (Contextuelle et Méthodologique)

Cette nouvelle façon de concevoir les interfaces marque une transition du **GUI** (Graphical User Interface) vers le **CUI** (Conversational User Interface) enrichi de capacités d'agent autonome (parfois appelé **AUI** - Agentic User Interface).

### Fonctionnement architectural
Le système repose sur une boucle de raisonnement (ex : pattern *ReAct* : Reasoning + Acting).
1. **Compréhension** : Le LLM analyse l'intention et le contexte.
2. **Planification** : L'agent décompose la demande et sélectionne les outils disponibles (APIs, BDD, composants UI).
3. **Exécution et Feedback** : L'agent exécute, observe les résultats, et informe l'utilisateur, en demandant une validation humaine (*Human-in-the-loop*) pour les actions critiques.

### Enjeux d'accessibilité (RGAA / WCAG)
- *Opportunité* : Une interface de chat bien conçue est nativement linéaire, compatible avec les lecteurs d'écran.
- *Risque* : Syndrome de la "page blanche", surcharge cognitive, difficulté pour les utilisateurs en situation de handicap moteur ou cognitif.
- *Exigence* : Fournir des suggestions de prompts, garantir la navigation clavier, proposer des alternatives multimodales (boutons, voix, bascule vers une interface graphique).

### Enjeux d'Architecture de l'Information et SEO
Une interface purement "Chat-First" (SPA qui ne charge du contenu que via API après requête) est invisible pour les moteurs de recherche. Une architecture hybride est nécessaire : le contenu doit rester exposé en HTML sémantique, le chat venant en surcouche interactive.

### IA Responsable et Éthique
Le principe de *transparence* est crucial. L'utilisateur doit savoir qu'il interagit avec un agent, comprendre quelles actions l'agent s'apprête à effectuer, et avoir un moyen simple d'interrompre le processus.

---

## 3. Architecture Technique et Stack

```mermaid
flowchart TD
    classDef layer fill:#f9f9f9,stroke:#333,stroke-width:2px,rx:5,ry:5
    classDef component fill:#e1f5fe,stroke:#01579b,stroke-width:1px
    classDef data fill:#fff3e0,stroke:#e65100,stroke-width:1px,stroke-dasharray: 5 5
    classDef security fill:#ffebee,stroke:#b71c1c,stroke-width:2px

    subgraph UI ["Couche 6 : Interface Utilisateur (Frontend)"]
        direction TB
        ChatUI["Interface Chat\nNext.js + Vercel AI SDK\nStreaming + Historique"]:::component
        Widgets["Widgets Dynamiques\nshadcn/ui + Radix UI\nGenerative UI"]:::component
        A11y["Accessibilité\nWAI-ARIA + Navigation clavier\nTests NVDA/VoiceOver"]:::component
    end

    subgraph ORCH ["Couche 5 : Orchestration d'Agents"]
        LangGraph["LangGraph / CrewAI\nBoucle ReAct + Planification\nValidation humaine (HITL)"]:::component
        smolagents["smolagents (HuggingFace)\nPrototypage rapide\nCode-first"]:::component
    end

    subgraph LLM ["Couche 4 : Modèles de Langage (LLM)"]
        Router["Model Router\nLéger (classification) vs Lourd (raisonnement)\nRéduction coûts 60-80%"]:::component
        GPT4["GPT-4o / Claude 3.5 Sonnet\nRaisonnement complexe\nTool calling avancé"]:::component
        Mistral["Mistral Large / Llama 3\nAlternative souveraine\nDéploiement on-premise"]:::component
    end

    subgraph TOOLS ["Couche 3 : Outils & Intégrations (Tool Calling)"]
        direction TB
        API["APIs Métier\nCRM, ERP, RH\nValidation OpenAPI + Zod/Pydantic"]:::component
        DB["Bases de Données\nPostgreSQL, Snowflake\nRequêtes SQL paramétrées"]:::component
        Web["Navigateur Sandbox\nPlaywright, Browserbase\nDomaines limités"]:::component
        Code["Exécution Code\nE2B, WebAssembly\nSandbox + Timeout strict"]:::component
    end

    subgraph MEM ["Couche 2 : Mémoire & Contexte"]
        VectorDB["Vector DB\nQdrant / Pinecone / pgvector\nRAG (recherche sémantique)"]:::data
        Redis["Cache Session\nRedis / Memcached\nMémoire court-terme"]:::data
        Mem0["Mem0 / LangChain Memory\nProfil utilisateur\nMémoire long-terme"]:::data
    end

    subgraph OBS ["Couche 1 : Observabilité & Gouvernance"]
        Langfuse["Langfuse / LangSmith\nTracing + Coûts + Évaluation\nDebug avancé"]:::security
        Guardrails["Guardrails AI / NeMo\nValidation entrée/sortie\nPrévention hallucinations"]:::security
        Helicone["Helicone\nMonitoring latences\nAlertes coûts"]:::security
    end

    UI -->|"1. Requête utilisateur (Streaming)"| ORCH
    ORCH -->|"2. Planification des tâches"| LLM
    LLM -->|"3. Inférence & Tool Calling"| ORCH
    ORCH <-->|"4. Lecture/Écriture contrôlée"| TOOLS
    ORCH <-->|"5. Récupération contexte (RAG)"| MEM

    OBS -.-|"Audit & Sécurité"| ORCH
    OBS -.-|"Audit & Sécurité"| LLM
    OBS -.-|"Audit & Sécurité"| TOOLS
    OBS -.-|"Audit & Sécurité"| UI

    class UI,ORCH,LLM,TOOLS,MEM,OBS layer
```

---

## 4. Flux d'exécution typique

**Étape 1 — Utilisateur** : « Compare les ventes Q1 et Q2, et envoie le rapport à mon manager. »

**Étape 2 — Orchestrateur (LangGraph)** : analyse l'intention et identifie 3 sous-tâches :
- Récupérer les données de ventes
- Générer un rapport comparatif
- Envoyer par email

**Étape 3 — Agent (avec LLM GPT-4o)** :
- Étape a) : appel de l'outil `query_database` avec paramètres validés → récupération des données brutes Q1/Q2
- Étape b) : appel de l'outil `generate_report` → génération du rapport structuré (markdown + graphique)
- Étape c) : demande de validation humaine → « Je vais envoyer ce rapport à manager@entreprise.com. Confirmez-vous ? »

**Étape 4 — Utilisateur** : « Oui, envoie. »

**Étape 5 — Agent** : appel de l'outil `send_email` → « Rapport envoyé avec succès. »

**Étape 6 — Interface** : affiche le rapport dans le chat (Generative UI), confirme l'envoi, propose des actions suivantes.

---

## 5. Points de Vigilance Méthodologiques

### 1. Sécurité (principe du moindre privilège)
- Chaque outil doit avoir des permissions minimales (lecture seule par défaut).
- Les actions d'écriture, suppression ou envoi nécessitent **toujours** une validation humaine.
- Isoler les outils dans des sandboxes (Docker, WebAssembly, E2B).

### 2. Gestion des erreurs et fallback
- Définir des timeouts stricts pour chaque appel d'outil (ex : 10 secondes maximum).
- Prévoir des messages d'erreur clairs et des alternatives (escalade humaine, suggestion de reformulation).
- Ne jamais laisser l'agent boucler indéfiniment (maximum 5 à 10 itérations).

### 3. Coûts maîtrisés
- Mettre en place un cache sémantique (GPTCache, Redis) pour les requêtes similaires.
- Router vers des modèles légers quand c'est possible.
- Monitorer les coûts par utilisateur, session et jour.

### 4. Accessibilité non négociable
- Le chat doit être 100 % navigable au clavier.
- Les réponses doivent être structurées sémantiquement (listes, titres, liens).
- Proposer des alternatives aux suggestions de prompts (boutons, voix).
- Tester systématiquement avec NVDA et VoiceOver.

### 5. Transparence et confiance
- Afficher les étapes de raisonnement de l'agent (« Je consulte la base de données... »).
- Citer les sources quand l'agent s'appuie sur des documents.
- Permettre à l'utilisateur de voir l'historique complet des actions.

### 6. Tests et évaluation
- Créer des batteries de tests (DeepEval, Ragas) pour évaluer la qualité des réponses.
- Tester les cas limites (requêtes ambiguës, hors domaine, tentatives d'injection).
- Mesurer la satisfaction utilisateur et le taux de résolution sans escalade humaine.

---

## 6. Recommandations de Démarrage

### Pour un MVP (Minimum Viable Product)
- **Orchestration** : LangGraph (contrôle, observabilité)
- **LLM** : Claude 3.5 Sonnet ou GPT-4o (bon équilibre qualité/coût)
- **Mémoire** : PostgreSQL + pgvector (simple, tout-en-un)
- **Interface** : Next.js + Vercel AI SDK + shadcn/ui
- **Observabilité** : Langfuse (open-source, gratuit pour démarrer)

### Pour une mise en production
- Ajouter un système de routing de modèles (modèles légers + lourds).
- Mettre en place des guardrails stricts (Guardrails AI).
- Implémenter un cache sémantique agressif.
- Déployer des tests automatisés de qualité et d'accessibilité.
- Prévoir un mécanisme d'escalade humaine robuste.

---

> *Note : Cette fiche est conçue pour être un artefact d'architecture de l'information vivant. Elle est versionnable, modifiable et sert de référence pour l'alignement entre les équipes techniques et les décideurs.*