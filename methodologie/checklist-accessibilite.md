# ♿ Checklist d'Accessibilité Numérique (RGAA 4.1 / WCAG 2.1 AA)

Cette grille d'audit opérationnelle est conçue pour être utilisée lors des revues de code, des tests de maquettes Figma ou des recettes avant mise en production. Elle se concentre sur les critères les plus critiques et les plus fréquemment échoués.

> **Règle d'or** : L'accessibilité se teste au clavier (Tab, Shift+Tab, Entrée, Espace, Flèches) ET avec un lecteur d'écran (NVDA sur Windows, VoiceOver sur macOS).

---

## 🖼️ 1. Images et Multimédia

- [ ] **Images porteuses d'information** : Possèdent un attribut `alt` pertinent et concis décrivant le contenu ou la fonction.
- [ ] **Images décoratives** : Possèdent un attribut `alt=""` (vide) ou sont définies via CSS (`background-image`).
- [ ] **Images complexes** (graphiques, cartes) : Disposent d'une description longue accessible (via `longdesc`, un lien adjacent ou un tableau de données équivalent).
- [ ] **Vidéos** : Disposent de sous-titres synchronisés et d'une transcription textuelle complète.
- [ ] **Animations** : Respectent la requête média `@media (prefers-reduced-motion: reduce)` (pas de mouvement automatique > 5 secondes ou clignotement).

---

## 🎨 2. Couleurs et Contrastes

- [ ] **Contraste texte/fond** : Ratio d'au moins **4.5:1** pour le texte normal et **3:1** pour le texte en gros caractères (≥ 18pt ou 14pt gras).
- [ ] **Contraste des composants UI** : Les éléments d'interface (champs de formulaire, boutons, icônes informatives) ont un contraste d'au moins **3:1** par rapport aux couleurs adjacentes.
- [ ] **Non-dépendance à la couleur** : L'information n'est jamais véhiculée *uniquement* par la couleur (ex: un champ d'erreur a une icône ou un texte "Erreur", pas juste une bordure rouge).
- [ ] **Focus visible** : L'indicateur de focus clavier est clairement visible et contraste avec l'arrière-plan (ne jamais utiliser `outline: none` sans alternative).

---

## ⌨️ 3. Navigation et Clavier

- [ ] **Navigation au clavier** : Tous les éléments interactifs (liens, boutons, formulaires, menus) sont atteignables et utilisables uniquement au clavier.
- [ ] **Ordre de tabulation** : L'ordre de navigation (Tab) est logique, intuitif et suit l'ordre visuel de la page.
- [ ] **Piège au clavier** : Aucun élément (ex: modale, menu déroulant) ne piège le focus. La touche `Échap` ferme les modales et les menus.
- [ ] **Liens d'évitement** : Un lien "Aller au contenu principal" est présent en début de page et devient visible au focus.
- [ ] **Titres de pages** : Chaque page a un `<title>` unique et descriptif dans le `<head>`.

---

## 📝 4. Formulaires

- [ ] **Étiquettes (Labels)** : Chaque champ de formulaire est associé à une étiquette via l'attribut `for` (HTML) correspondant à l'`id` du champ, ou via `aria-labelledby`.
- [ ] **Champs obligatoires** : Indiqués clairement dans le `label` (ex: "Nom (obligatoire)") et/ou via `aria-required="true"`.
- [ ] **Messages d'erreur** : Sont explicites, indiquent comment corriger l'erreur, et sont annoncés par le lecteur d'écran (via `aria-live="polite"` ou `role="alert"`).
- [ ] **Regroupement** : Les ensembles de champs liés (ex: coordonnées, radio buttons) sont regroupés dans un `<fieldset>` avec un `<legend>`.

---

## 🏗️ 5. Structure et Code (HTML/ARIA)

- [ ] **Hiérarchie des titres** : Les balises `<h1>` à `<h6>` sont utilisées dans un ordre logique, sans saut de niveau (ex: pas de `<h3>` directement après un `<h1>`).
- [ ] **Langue de la page** : L'attribut `lang="fr"` (ou autre) est présent sur la balise `<html>`.
- [ ] **Usage d'ARIA** : Les attributs ARIA sont utilisés *uniquement* lorsque le HTML sémantique natif ne suffit pas. (Règle n°1 d'ARIA : ne pas utiliser ARIA si un élément HTML natif existe).
- [ ] **Redimensionnement** : Le contenu reste lisible et fonctionnel lorsque le zoom du navigateur est augmenté jusqu'à 200 %.
- [ ] **Responsive** : Pas de défilement horizontal à 320px de largeur de viewport (sauf pour les tableaux de données complexes).

---

## 🧰 Outils de test recommandés

1. **Automatisés (Détection de ~30% des erreurs)** :
   - Extension navigateur : **axe DevTools** (Deque) ou **WAVE**.
   - CLI : `@axe-core/playwright` ou `pa11y` dans la CI/CD.
2. **Manuels (Indispensables)** :
   - Navigation 100 % clavier (sans souris).
   - Test avec un lecteur d'écran : **NVDA** (Windows, gratuit) ou **VoiceOver** (macOS/iOS, natif).
   - Outil de vérification de contraste : **Contrast Checker** ou l'inspecteur de couleurs de Firefox/Chrome.

---

> **Note méthodologique** : Cette checklist est un point de départ. Pour un audit de conformité officiel (ex: déclaration d'accessibilité RGAA), un audit complet par un expert certifié est requis.