# 📚 Guide Complet du Code Frontend — PortNet Réclamations

> **Pour qui ?** Ce guide est écrit pour quelqu'un qui a des bases en HTML et CSS, un peu de JavaScript, mais qui a du mal à comprendre ce code seul. Chaque concept est expliqué simplement, ligne par ligne, avec des analogies du monde réel.

---

## 🗺️ Table des Matières

1. [Vue d'ensemble : Comment fonctionne le projet ?](#1-vue-densemble)
2. [La structure des fichiers](#2-structure-des-fichiers)
3. [index.html — Le squelette de la page](#3-indexhtml--le-squelette-de-la-page)
4. [css/styles.css — L'apparence visuelle](#4-cssstylesscss--lapparence-visuelle)
5. [js/data.js — La base de données simulée](#5-jsdatajs--la-base-de-données-simulée)
6. [js/api.js — La couche de communication](#6-jsapijs--la-couche-de-communication)
7. [js/reclamations-list.js — La liste des réclamations](#7-jsreclamations-listjs--la-liste-des-réclamations)
8. [js/reclamation-detail.js — Le modal de détails](#8-jsreclamation-detailjs--le-modal-de-détails)
9. [js/new-reclamation.js — Le formulaire en 3 étapes](#9-jsnew-reclamationjs--le-formulaire-en-3-étapes)
10. [js/app.js — Le chef d'orchestre](#10-jsappjs--le-chef-dorchestre)
11. [Comment tout se connecte : le cycle de vie](#11-comment-tout-se-connecte-le-cycle-de-vie)
12. [Concepts JavaScript expliqués simplement](#12-concepts-javascript-expliqués-simplement)

---

## 1. Vue d'ensemble

Imagine que tu construis une **application web pour gérer les plaintes des clients de PortNet**. Cette application fonctionne entièrement dans le navigateur (Firefox, Chrome…), sans rechargement de page. C'est ce qu'on appelle une **SPA (Single Page Application)**.

### Comment ça marche en gros ?

```
L'utilisateur ouvre index.html dans le navigateur
        ↓
Le navigateur charge les styles (CSS) et les scripts (JS)
        ↓
Le code JS s'active et rend la page interactive
        ↓
L'utilisateur clique → le JS réagit → la page se met à jour sans se recharger
```

### Les "briques" du projet :

| Fichier | Rôle | Analogie |
|---|---|---|
| `index.html` | Structure de la page | Le plan d'un appartement |
| `css/styles.css` | L'apparence visuelle | La décoration et la peinture |
| `js/data.js` | Les données simulées | Un cahier avec des informations écrites |
| `js/api.js` | La communication avec les données | Le bibliothécaire qui cherche dans le cahier |
| `js/reclamations-list.js` | L'affichage de la liste | L'écran qui montre les résultats |
| `js/reclamation-detail.js` | L'affichage du détail d'une réclamation | La fiche détaillée d'un dossier |
| `js/new-reclamation.js` | Le formulaire de création | Le formulaire qu'on remplit au guichet |
| `js/app.js` | Le contrôleur principal | Le directeur qui coordonne tout |

---

## 2. Structure des Fichiers

```
frontend/
│
├── index.html                ← La seule page HTML du projet
│
├── public/
│   └── portnetLogo.jpg       ← Le logo officiel de PortNet
│
├── css/
│   └── styles.css            ← Tous les styles visuels
│
└── js/
    ├── data.js               ← Les données (réclamations, statuts, services...)
    ├── api.js                ← Les fonctions pour lire/écrire les données
    ├── reclamations-list.js  ← Affiche la liste des réclamations
    ├── reclamation-detail.js ← Affiche le détail d'une réclamation
    ├── new-reclamation.js    ← Gère le formulaire de création
    └── app.js                ← Démarre et coordonne tout
```

> **Important** : L'ordre de chargement des scripts dans `index.html` est crucial. `data.js` doit être chargé **avant** `api.js`, qui doit être chargé **avant** les autres modules.

---

## 3. index.html — Le Squelette de la Page

### 3.1 L'en-tête `<head>`

```html
<!DOCTYPE html>
<html lang="fr">
```
- `<!DOCTYPE html>` : Dit au navigateur "ce fichier est du HTML5 moderne".
- `lang="fr"` : Indique que la langue est le français (important pour l'accessibilité et le SEO).

```html
<meta charset="UTF-8">
```
- Permet d'utiliser les caractères français : é, è, ê, ç, etc. Sans ça, ces lettres s'afficheraient en symboles étranges.

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```
- Rend la page responsive (adaptée aux téléphones mobiles). Sans ça, la page s'afficherait toute petite sur un smartphone.

```html
<meta name="description" content="Portail Marocain...">
```
- Le texte qui apparaît dans les résultats Google sous le titre de la page.

```html
<title>Portail Marocain des Procédures du Commerce Extérieur — PortNet</title>
```
- Le texte affiché dans l'onglet du navigateur.

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/.../bootstrap.min.css">
```
- Charge Bootstrap depuis Internet. Bootstrap est une bibliothèque CSS qui fournit des composants visuels prêts à l'emploi (grilles, boutons, etc.). `cdn.jsdelivr.net` est un serveur qui héberge ces fichiers.

```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/.../all.min.css">
```
- Charge Font Awesome depuis Internet. Font Awesome fournit des milliers d'icônes (la loupe, le crayon, l'icône de téléchargement, etc.).

```html
<link rel="icon" type="image/jpeg" href="public/portnetLogo.jpg">
```
- Définit le **favicon** : la petite icône qui apparaît dans l'onglet du navigateur à côté du titre.

```html
<link rel="stylesheet" href="css/styles.css">
```
- Charge notre propre fichier CSS. Doit être chargé **après** Bootstrap pour que nos styles puissent le surcharger si nécessaire.

---

### 3.2 La Barre de Navigation

```html
<nav class="dashboard-nav" id="dashboardNav">
    <a href="#" class="nav-logo" title="PortNet S.A.">
        <img src="public/portnetLogo.jpg" alt="PortNet Logo" class="nav-logo-img">
    </a>
    <div class="nav-user">
        Bienvenue : <strong id="navUserName">Demo Importateur</strong>
    </div>
</nav>
```

- `<nav>` : Balise HTML5 sémantique pour une zone de navigation. Le navigateur et les lecteurs d'écran comprennent que c'est un menu.
- `class="dashboard-nav"` : Relie cet élément aux styles CSS correspondants dans `styles.css`.
- `id="dashboardNav"` : Un identifiant unique pour que JavaScript puisse trouver cet élément.
- L'image `portnetLogo.jpg` affiche le logo officiel de PortNet.
- `alt="PortNet Logo"` : Texte affiché si l'image ne se charge pas, et lu par les lecteurs d'écran (accessibilité).
- `id="navUserName"` : JavaScript va remplacer "Demo Importateur" par le vrai nom de l'utilisateur connecté.

---

### 3.3 Le Panneau Latéral (Sidebar)

```html
<aside class="dashboard-sidebar">
    <a href="#" class="sidebar-link active">
        <i class="fas fa-chart-line"></i> Tableau de bord
    </a>
    ...
</aside>
```

- `<aside>` : Balise HTML5 pour un contenu secondaire (ici le menu latéral).
- `class="sidebar-link active"` : La classe `active` ajoute une bordure bleue à gauche pour indiquer la page courante.
- `<i class="fas fa-chart-line">` : Affiche l'icône "graphique en ligne" de Font Awesome. `fas` = Font Awesome Solid, `fa-chart-line` = le nom de l'icône.

> **Astuce Font Awesome** : Pour trouver une icône, va sur [fontawesome.com/icons](https://fontawesome.com/icons), cherche par mot-clé, et copie le code `<i class="fas fa-...">`.

---

### 3.4 Le Bouton Flottant "Besoin d'aide ?"

```html
<button id="helpFloatingBtn" class="help-floating-btn" type="button" title="Ouvrir le centre d'aide">
    <i class="fas fa-question-circle"></i>
    Besoin d'aide ?
</button>
```

- Ce bouton est **fixé sur le bord droit** de l'écran (le CSS utilise `position: fixed`).
- `id="helpFloatingBtn"` : JavaScript utilise cet ID pour détecter le clic et ouvrir le panneau d'aide.
- `type="button"` : Bonne pratique. Sans ça, un bouton dans un `<form>` soumet automatiquement le formulaire.

---

### 3.5 Le Panneau du Centre d'Aide

```html
<div id="centreAideOverlay" class="centre-aide-overlay"></div>

<div id="centreAidePanel" class="centre-aide-panel">
```

- Il y a **deux éléments** qui travaillent ensemble :
  1. L'**overlay** (`centreAideOverlay`) : Un fond semi-transparent gris qui couvre tout l'écran pour "bloquer" le reste.
  2. Le **panel** (`centreAidePanel`) : Le vrai panneau blanc qui glisse depuis la droite.
- Au départ, les deux sont invisibles (CSS). Quand on clique sur "Besoin d'aide ?", JavaScript leur ajoute la classe `active`, et le CSS les rend visibles avec une animation.

```html
<div class="panel-menu">
    <button class="panel-menu-item" data-action="faq" type="button">...</button>
    <button class="panel-menu-item" data-action="mes-reclamations" ...>...</button>
    <button class="panel-menu-item" data-action="nouvelle-reclamation" ...>...</button>
```

- `data-action="faq"` : C'est un **attribut de données personnalisé** (`data-*`). Il permet de stocker une information dans le HTML que JavaScript peut lire. Ici, c'est l'action à déclencher quand on clique ce bouton.

---

### 3.6 Le Modal de Détails d'une Réclamation

```html
<div id="detailModalOverlay" class="detail-modal-overlay">
    <div class="detail-modal" id="detailModal">
        <!-- Header -->
        <div class="detail-header">...</div>
        <!-- Scrollable body -->
        <div class="detail-body" id="detailBody">
            <!-- Dynamically filled by reclamation-detail.js -->
        </div>
        <!-- Footer -->
        <div class="detail-footer">
            <button id="detailCloseBtn" class="btn-fermer" type="button">Fermer</button>
        </div>
    </div>
</div>
```

- Ce modal est **vide** au départ. Le commentaire "Dynamically filled by reclamation-detail.js" explique que JavaScript va y injecter du contenu quand on ouvre une réclamation.
- `id="detailBody"` : JavaScript cible cet élément pour y écrire le HTML du détail.

---

### 3.7 Le Formulaire Multi-étapes (Wizard)

```html
<div id="newRecOverlay" class="new-rec-overlay">
    <div class="new-rec-modal" id="newRecModal">

        <!-- Barre de progression -->
        <div class="new-rec-progress">
            <div class="new-rec-progress-fill" id="progressFill" style="width: 33.33%;"></div>
        </div>

        <!-- Stepper (les cercles 1, 2, 3) -->
        <div class="new-rec-stepper" id="stepper">
            <div class="stepper-step active" data-step="1">
                <div class="stepper-circle active" id="stepperCircle1">1</div>
                <span class="stepper-label">Type de demande</span>
            </div>
            <div class="stepper-line" id="stepperLine1"></div>
            <div class="stepper-step" data-step="2">...
```

- `style="width: 33.33%;"` : La barre de progression commence à 33% (l'étape 1 sur 3). JavaScript la met à jour à 66% puis 100% quand on avance.
- `id="stepperCircle1"` : JavaScript change le contenu de ce cercle (remplace "1" par une coche ✓ quand l'étape est complétée).
- `id="stepperLine1"` : La ligne entre les cercles. JavaScript lui ajoute la classe `completed` ou `active` pour changer sa couleur.

---

### 3.8 Le Chargement des Scripts

```html
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.jsdelivr.net/.../bootstrap.bundle.min.js"></script>
<script src="js/data.js"></script>
<script src="js/api.js"></script>
<script src="js/reclamations-list.js"></script>
<script src="js/reclamation-detail.js"></script>
<script src="js/new-reclamation.js"></script>
<script src="js/app.js"></script>
```

> **Pourquoi à la fin du `<body>` et pas dans `<head>` ?**
> Si on mettait les scripts dans `<head>`, ils se chargeraient **avant** que le HTML soit créé. JavaScript essaierait de trouver des éléments qui n'existent pas encore et planterait. En les mettant à la fin du `<body>`, tout le HTML est déjà construit.

> **L'ordre est crucial** :
> - jQuery doit être premier (les autres en ont besoin).
> - `data.js` doit être avant `api.js` (api.js lit les données de data.js).
> - `app.js` doit être dernier (il utilise tous les autres modules).

---

## 4. css/styles.css — L'Apparence Visuelle

### 4.1 Les Variables CSS (Design Tokens)

```css
:root {
    --primary-navy:     #2D3660;
    --primary-blue:     #3B4B94;
    --accent-blue:      #4A5FC1;
    --bg-page:          #EEF0F6;
    --bg-card:          #FFFFFF;
    --text-primary:     #1E293B;
    --text-secondary:   #64748B;
    --radius-md:        10px;
    --shadow-sm:        0 1px 3px rgba(0,0,0,0.06);
    --transition-med:   0.3s ease;
    --panel-width:      420px;
}
```

- `:root` signifie "la racine du document", c'est-à-dire tout le document.
- `--primary-navy: #2D3660;` définit une **variable CSS**. Les variables CSS sont comme des constantes : on les définit une fois et on les utilise partout.
- Pour utiliser une variable : `color: var(--primary-navy);`
- **Avantage** : Pour changer toutes les couleurs du projet, il suffit de modifier ce bloc. Sans variables, il faudrait chercher et remplacer la couleur dans tout le fichier CSS.
- `rgba(0,0,0,0.06)` = noir (`0,0,0`) avec 6% d'opacité (très transparent).

---

### 4.2 Le Reset CSS

```css
*,
*::before,
*::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}
```

- `*` = "tous les éléments HTML".
- `::before` et `::after` = les pseudo-éléments (éléments virtuels créés par CSS).
- `box-sizing: border-box` : Très important ! Par défaut, si un élément a `width: 200px` et `padding: 20px`, il fait en réalité 240px. Avec `border-box`, il reste à 200px et le padding est à l'intérieur.
- `margin: 0; padding: 0;` : Les navigateurs ajoutent des espaces par défaut sur certains éléments. Ce "reset" supprime ces espaces pour avoir un point de départ propre.

---

### 4.3 La Barre de Navigation

```css
.dashboard-nav {
    display: flex;                    /* Active Flexbox */
    align-items: center;              /* Centre verticalement */
    justify-content: space-between;   /* Pousse les éléments aux extrémités */
    height: 60px;
    background: var(--bg-card);       /* Fond blanc */
    border-bottom: 1px solid var(--border-color);  /* Ligne grise en bas */
    padding: 0 24px;
    position: sticky;                 /* Reste collé en haut lors du scroll */
    top: 0;
    z-index: 100;                     /* Au-dessus des autres éléments */
    box-shadow: var(--shadow-sm);     /* Légère ombre en bas */
}
```

- **Flexbox** (`display: flex`) : Un système de mise en page moderne. Avec `justify-content: space-between`, le logo va à gauche et le nom utilisateur à droite automatiquement.
- `position: sticky; top: 0;` : La barre reste visible même quand on fait défiler la page. C'est la barre de navigation fixe.
- `z-index: 100` : Les éléments avec un `z-index` plus élevé apparaissent au-dessus. La barre doit être au-dessus du contenu qui défile dessous.

---

### 4.4 Le Bouton Flottant

```css
.help-floating-btn {
    position: fixed;             /* Fixé par rapport à l'écran (pas à la page) */
    right: 0;                    /* Collé au bord droit */
    top: 50%;                    /* À 50% du haut de l'écran */
    transform: translateY(-50%); /* Remonte de 50% de sa propre hauteur → centrage vertical parfait */
    z-index: 500;
    background: linear-gradient(180deg, var(--primary-navy), var(--primary-blue));
    writing-mode: vertical-rl;   /* Texte vertical (de haut en bas) */
    text-orientation: mixed;
    border-radius: 10px 0 0 10px; /* Arrondi seulement à gauche (collé à droite) */
    transition: all var(--transition-med); /* Animation fluide au hover */
}

.help-floating-btn.hidden {
    transform: translateY(-50%) translateX(100%); /* Sort de l'écran vers la droite */
    pointer-events: none; /* Désactive les clics quand caché */
}
```

- `position: fixed` vs `position: sticky` : `fixed` est relatif à l'écran (ne bouge jamais). `sticky` est relatif à la page (bouge avec le scroll jusqu'à un point).
- `top: 50%; transform: translateY(-50%)` : Cette technique est le moyen classique de centrer verticalement un élément. `top: 50%` place le haut de l'élément au milieu, puis `translateY(-50%)` remonte l'élément de la moitié de sa propre hauteur.
- `writing-mode: vertical-rl` : Fait pivoter le texte pour qu'il soit vertical.
- `translateX(100%)` : Déplace l'élément vers la droite de 100% de sa propre largeur → il sort de l'écran.

---

### 4.5 Le Panneau d'Aide (Animation de glissement)

```css
.centre-aide-panel {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: var(--panel-width);     /* 420px */
    transform: translateX(100%);   /* Caché à droite hors de l'écran */
    transition: transform var(--transition-slow); /* Animation lente et fluide */
    display: flex;
    flex-direction: column;        /* Les enfants s'empilent verticalement */
}

.centre-aide-panel.active {
    transform: translateX(0);      /* Revient à sa position normale → glisse vers la gauche */
}
```

- **Le secret de l'animation** : Le panneau est toujours dans le HTML, mais hors de l'écran (`translateX(100%)`). Quand JavaScript lui ajoute la classe `active`, `transform` passe à `translateX(0)`, et `transition` anime ce changement automatiquement.
- C'est la même technique pour tous les modals et overlays du projet.

---

### 4.6 Les Badges de Statut

```css
.status-badge.affectee {
    color: var(--status-affectee-color);
    background: var(--status-affectee-bg);
    border: 1px solid var(--status-affectee-border);
}
.status-badge.repondue {
    color: var(--status-repondue-color);   /* Vert */
    background: var(--status-repondue-bg);
    border: 1px solid var(--status-repondue-border);
}
```

- Un badge de statut est un `<span>` avec la classe `status-badge`. JavaScript lui ajoute une deuxième classe (`affectee`, `repondue`, `cloturee`, `reouverte`) selon le statut de la réclamation.
- Cette combinaison de classes applique automatiquement les bonnes couleurs.

---

## 5. js/data.js — La Base de Données Simulée

### 5.1 Pourquoi ce fichier existe ?

Ce projet est en cours de développement. Le vrai backend (FastAPI + Odoo + base Oracle) n'est pas encore connecté. `data.js` simule la base de données directement dans le navigateur, avec de vraies données copiées depuis la plateforme PortNet.

### 5.2 Le Namespace `PortnetApp`

```javascript
window.PortnetApp = window.PortnetApp || {};
```

- **C'est la ligne la plus importante du projet**, elle apparaît dans chaque fichier JS.
- `window` = l'objet global du navigateur. Tout ce qu'on met dans `window` est accessible partout.
- `PortnetApp` = un "espace de noms" (namespace). Tous les modules du projet y sont rangés : `PortnetApp.API`, `PortnetApp.ReclamationsList`, etc.
- `|| {}` = "ou un objet vide si PortnetApp n'existe pas encore". Cela évite d'écraser le `PortnetApp` déjà créé par un autre fichier JS.

**Analogie** : Imagine un placard (`PortnetApp`). Chaque fichier JS pose ses affaires dedans (`PortnetApp.API`, `PortnetApp.STATUTS`...). La ligne dit "si le placard n'existe pas encore, crée-le ; sinon, utilise l'existant."

---

### 5.3 Les Statuts

```javascript
PortnetApp.STATUTS = {
    1: { id: 1, key: 'affectee',  label: 'Affectée',  color: '#64748B', bgColor: '#F1F5F9', borderColor: '#CBD5E1' },
    2: { id: 2, key: 'repondue',  label: 'Répondue',  color: '#059669', bgColor: '#ECFDF5', borderColor: '#A7F3D0' },
    3: { id: 3, key: 'cloturee',  label: 'Clôturée',  color: '#64748B', bgColor: '#F1F5F9', borderColor: '#CBD5E1' },
    4: { id: 4, key: 'reouverte', label: 'Réouverte', color: '#DC2626', bgColor: '#FEF2F2', borderColor: '#FECACA' }
};
```

- C'est un **objet JavaScript** dont les clés sont des nombres (1, 2, 3, 4).
- Chaque valeur est lui-même un objet avec plusieurs propriétés.
- `key: 'affectee'` : C'est le nom de la classe CSS qui sera appliquée au badge de statut.
- `label: 'Affectée'` : C'est le texte affiché à l'utilisateur.

**Comment on l'utilise ?**
```javascript
var statut = PortnetApp.STATUTS[1]; // { id: 1, key: 'affectee', label: 'Affectée', ... }
console.log(statut.label); // → "Affectée"
console.log(statut.key);   // → "affectee"
```

---

### 5.4 Les Services

```javascript
PortnetApp.SERVICES = [
    { id: 1,  label: 'Certificats de conformité' },
    { id: 2,  label: "Titres d'import" },
    // ...
    { id: 15, label: 'Import — Sources radioactives' }
];
```

- C'est un **tableau** (array) d'objets. Contrairement aux STATUTS (objet avec clés numériques), ici on utilise un tableau car l'ordre et l'itération sont importants (pour remplir la liste déroulante).

---

### 5.5 L'Utilisateur Courant

```javascript
PortnetApp.USERS = {
    1001: { id: 1001, name: 'imp rachidi',      role: 'client' },
    3001: { id: 3001, name: 'Service Odoo',     role: 'system' },
    4001: { id: 4001, name: 'Demo Importateur', role: 'client' }
};

PortnetApp.CURRENT_USER = PortnetApp.USERS[4001];
```

- `PortnetApp.USERS[4001]` lit l'objet avec la clé `4001` dans `USERS`.
- `PortnetApp.CURRENT_USER` sera donc `{ id: 4001, name: 'Demo Importateur', role: 'client' }`.
- C'est cette valeur que `app.js` utilisera pour afficher "Demo Importateur" dans la navbar.

---

### 5.6 Les Réclamations (mockReclamations)

```javascript
PortnetApp.mockReclamations = [
    {
        id: 20920,
        date_creation: '2026-06-23T12:03:00',  // Format ISO 8601
        id_statut_reclamation: 3,               // → 3 = 'Clôturée'
        id_service_reclamation: 1,              // → 1 = 'Certificats de conformité'
        objet: 'test',
        description: 'Test de réclamation...',
        created_by: 4001,                       // → l'utilisateur 4001 (Demo Importateur)
        response: 'Votre demande a été traitée.',
        id_type_reclamation: 2,                 // → 2 = 'Réclamation'
        reference: '20920',
        id_odoo: 50920                          // Identifiant dans le système Odoo
    },
    // ... 9 autres réclamations
];
```

- Chaque réclamation utilise des **identifiants** (`id_statut_reclamation: 3`) plutôt que les valeurs directes. C'est le principe des **clés étrangères** (comme en SQL).
- Pour afficher le vrai label du statut, on utilise `api.js` qui fait le lien : `PortnetApp.API.getStatut(3)` retourne l'objet `{ label: 'Clôturée', key: 'cloturee', ... }`.

---

### 5.7 L'Historique des Statuts

```javascript
PortnetApp.mockStatusHistory = [
    {
        id: 1,
        id_reclamation: 20914,
        id_statut_avant: null,  // null = c'est la création (pas de statut avant)
        id_statut_apres: 1,     // Statut initial = Affectée
        commentaire: 'DEUXIEME',
        date_changement: '2026-06-22T16:40:00',
        changed_by: 2001,
        reponse: null
    },
    {
        id: 2,
        id_reclamation: 20914,
        id_statut_avant: 1,     // Avant = Affectée
        id_statut_apres: 2,     // Après = Répondue
        commentaire: null,
        date_changement: '2026-06-22T16:41:00',
        changed_by: 3001,       // Fait par 'Service Odoo' (système)
        reponse: 'ok'
    },
    // ...
```

- C'est la **frise chronologique** de chaque réclamation.
- `id_statut_avant: null` → C'est la première entrée (création).
- `id_statut_avant: 1, id_statut_apres: 2` → Changement "Affectée → Répondue".
- `changed_by: 3001` → Effectué par le système Odoo (pas un humain).

---

## 6. js/api.js — La Couche de Communication

### 6.1 Le Pattern Module (IIFE)

Tous les fichiers JS du projet utilisent ce pattern. Voici comment le comprendre :

```javascript
PortnetApp.API = (function () {

    // Variables et fonctions PRIVÉES (inaccessibles depuis l'extérieur)
    var BASE_URL = '';

    function formatDate(isoString) { ... }
    function delay(ms) { ... }

    // Fonctions PUBLIQUES (accessibles depuis l'extérieur)
    async function getReclamations(searchTerm) { ... }

    // Ce qu'on "expose" au monde extérieur
    return {
        formatDate: formatDate,
        getReclamations: getReclamations,
        // ...
    };

})(); // ← Les parenthèses finales exécutent immédiatement la fonction
```

- `(function() { ... })()` = une fonction qui s'exécute immédiatement. C'est ce qu'on appelle une **IIFE** (Immediately Invoked Function Expression).
- Tout ce qui est à l'intérieur est **privé** (invisible depuis l'extérieur).
- Le `return { ... }` expose seulement les fonctions qu'on veut rendre **publiques**.
- **Pourquoi ?** Pour éviter que des variables internes (`BASE_URL`, `formatDate`) ne polluent ou ne soient modifiées accidentellement depuis d'autres fichiers.

**Analogie** : C'est comme une voiture. Tu vois le volant, la pédale et les boutons (fonctions publiques). Tu ne vois pas le moteur interne (variables et fonctions privées). Mais les deux fonctionnent ensemble.

---

### 6.2 La Fonction `formatDate`

```javascript
function formatDate(isoString) {
    if (!isoString) return '';          // Si la date est vide, retourne une chaîne vide
    var d = new Date(isoString);        // Crée un objet Date depuis la chaîne ISO
    var day   = String(d.getDate()).padStart(2, '0');       // Jour sur 2 chiffres (ex: "03")
    var month = String(d.getMonth() + 1).padStart(2, '0'); // Mois sur 2 chiffres (getMonth() commence à 0 !)
    var year  = d.getFullYear();                            // Année sur 4 chiffres
    var hours = String(d.getHours()).padStart(2, '0');
    var mins  = String(d.getMinutes()).padStart(2, '0');
    return day + '/' + month + '/' + year + ' ' + hours + ':' + mins;
    // Résultat : "23/06/2026 12:03"
}
```

- `new Date('2026-06-23T12:03:00')` : Transforme une chaîne de texte en objet Date, qui offre des méthodes pour extraire le jour, mois, année, etc.
- `.padStart(2, '0')` : Ajoute des zéros à gauche si le nombre est inférieur à 2 chiffres. `'3'` → `'03'`, mais `'23'` reste `'23'`.
- `getMonth() + 1` : Les mois en JavaScript vont de 0 (janvier) à 11 (décembre). On ajoute 1 pour avoir 1-12.

---

### 6.3 La Fonction `delay` (Simulation de réseau)

```javascript
function delay(ms) {
    return new Promise(function (resolve) { setTimeout(resolve, ms || 100); });
}
```

- Crée un délai artificiel de 100ms (ou le nombre de ms passé en paramètre).
- Simule le temps qu'une vraie requête réseau prendrait pour répondre.
- `ms || 100` : "ms s'il est défini, sinon 100". C'est la valeur par défaut.

---

### 6.4 `async/await` et les Promesses

```javascript
async function getReclamations(searchTerm) {
    await delay();   // Attend 100ms (simule le réseau)
    var results = PortnetApp.mockReclamations.slice(); // Copie le tableau

    if (searchTerm && searchTerm.trim() !== '') {
        var term = searchTerm.trim().toLowerCase();
        results = results.filter(function (r) {
            return r.reference.toLowerCase().indexOf(term) !== -1 ||
                   r.objet.toLowerCase().indexOf(term) !== -1;
        });
    }

    results.sort(function (a, b) {
        return new Date(b.date_creation) - new Date(a.date_creation); // Plus récent en premier
    });

    return results;
}
```

- `async` : Ce mot-clé devant `function` dit que cette fonction est **asynchrone**. Elle retourne une Promesse.
- `await` : Ce mot-clé **pause** l'exécution jusqu'à ce que la Promesse soit résolue. Ici, il attend 100ms.
- **Pourquoi asynchrone ?** Quand tu feras une vraie requête réseau (`fetch()`), le navigateur doit continuer à fonctionner pendant l'attente. Sans `async/await`, la page se figerait.
- `.slice()` : Copie le tableau. On travaille sur la copie pour ne pas modifier le tableau original.
- `.filter()` : Retourne un nouveau tableau ne contenant que les éléments qui satisfont la condition.
- `.indexOf(term) !== -1` : "Le terme est trouvé quelque part dans la chaîne" (indexOf retourne -1 si non trouvé).
- `.sort()` : Trie le tableau. `new Date(b) - new Date(a)` donne un nombre positif si b est plus récent que a, donc les plus récents viennent en premier.

---

### 6.5 La Fonction `createReclamation`

```javascript
async function createReclamation(data) {
    await delay(300); // Délai plus long pour simuler une vraie écriture en base

    // Génère un nouvel ID (max existant + 1)
    var maxId = Math.max.apply(null, PortnetApp.mockReclamations.map(function (r) { return r.id; }));
    var newId = maxId + 1;

    var newRec = {
        id: newId,
        date_creation: new Date().toISOString(), // Date et heure actuelles
        id_statut_reclamation: 1,                // Toujours commence en "Affectée"
        id_service_reclamation: data.id_service_reclamation,
        objet: data.objet,
        description: data.description,
        created_by: PortnetApp.CURRENT_USER.id,
        response: null,
        id_type_reclamation: data.id_type_reclamation,
        reference: String(newId),                // La référence = l'ID en texte
        id_odoo: 50000 + newId
    };

    PortnetApp.mockReclamations.unshift(newRec); // Ajoute au DÉBUT du tableau (plus récent en premier)

    return newRec;
}
```

- `Math.max.apply(null, tableau)` : Trouver le maximum dans un tableau. C'est équivalent à `Math.max(...tableau)` en ES6 moderne.
- `.map(function(r) { return r.id; })` : Transforme un tableau d'objets en tableau d'IDs. `[{id:20920,...},{id:20919,...}]` → `[20920,20919,...]`.
- `new Date().toISOString()` : La date et heure actuelles au format ISO (`2026-07-01T16:10:32.000Z`).
- `.unshift()` : Ajoute un élément au **début** d'un tableau (contrairement à `.push()` qui ajoute à la fin).

---

### 6.6 Les Fonctions de Lookup (Recherche)

```javascript
function getStatut(id) {
    return PortnetApp.STATUTS[id] || { label: 'Inconnu', color: '#999', ... };
}

function getService(id) {
    return PortnetApp.SERVICES.find(function (s) { return s.id === id; }) || { label: 'Inconnu' };
}
```

- `PortnetApp.STATUTS[id]` : Accès direct par clé (très rapide). Retourne `undefined` si non trouvé.
- `|| { label: 'Inconnu' }` : Valeur par défaut si l'ID n'existe pas. Évite un crash.
- `.find()` : Parcourt le tableau et retourne le **premier** élément qui correspond. Différent de `.filter()` qui retourne un tableau de tous les éléments correspondants.
- `s.id === id` : Comparaison **stricte** (=== vérifie aussi le type). Préférable à == qui peut faire des conversions inattendues.

---

## 7. js/reclamations-list.js — La Liste des Réclamations

### 7.1 Initialisation

```javascript
PortnetApp.ReclamationsList = (function () {

    var $list        = null; // Référence vers le conteneur de la liste
    var $count       = null; // Référence vers le compteur "X réclamation(s)"
    var $searchInput = null; // Référence vers le champ de recherche
    var currentData  = [];   // Les données actuellement affichées

    function init() {
        $list        = $('#reclamationsList');
        $count       = $('#reclamationsCount');
        $searchInput = $('#searchInput');

        // Recherche au clic sur le bouton loupe
        $('#searchBtn').on('click', function () {
            performSearch();
        });

        // Recherche en appuyant sur Entrée
        $searchInput.on('keypress', function (e) {
            if (e.key === 'Enter') {
                performSearch();
            }
        });
    }
```

- `var $list = null;` : On déclare les variables en haut du module. Le `$` devant les noms est une convention jQuery pour indiquer que la variable contient un élément jQuery.
- `$('#reclamationsList')` : **Sélecteur jQuery**. Le `#` signifie "l'élément avec l'ID `reclamationsList`". C'est équivalent à `document.getElementById('reclamationsList')` en JavaScript pur, mais plus court et plus puissant.
- `.on('click', function() { ... })` : Attache un écouteur d'événement. Quand l'élément est cliqué, la fonction s'exécute.
- `e.key === 'Enter'` : `e` est l'objet événement. `e.key` contient le nom de la touche pressée.

---

### 7.2 Chargement et Rendu

```javascript
async function load() {
    $list.html('<div class="spinner"></div>'); // Affiche un spinner pendant le chargement

    var data = await PortnetApp.API.getReclamations();
    currentData = data;
    render(data);
}

function render(reclamations) {
    $count.text(reclamations.length + ' réclamation(s)');

    if (reclamations.length === 0) {
        $list.html(
            '<div class="empty-state">' +
                '<i class="fas fa-inbox"></i>' +
                '<p>Aucune réclamation trouvée</p>' +
            '</div>'
        );
        return; // Arrête la fonction ici
    }

    var html = '';
    reclamations.forEach(function (rec) {
        var statut        = PortnetApp.API.getStatut(rec.id_statut_reclamation);
        var dateFormatted = PortnetApp.API.formatDate(rec.date_creation);

        html += '<div class="reclamation-card" data-id="' + rec.id + '">';
        html +=   '<div class="card-top-row">';
        html +=     '<span class="card-reference" data-id="' + rec.id + '">' + rec.reference + '</span>';
        html +=     '<span class="status-badge ' + statut.key + '">' + statut.label + '</span>';
        html +=   '</div>';
        html +=   '<div class="card-objet">' + escapeHtml(rec.objet) + '</div>';
        html +=   '<div class="card-bottom-row">';
        html +=     '<span class="card-date">' + dateFormatted + '</span>';
        html +=     '<span class="card-details-link" data-id="' + rec.id + '">Voir détails <i class="fas fa-eye"></i></span>';
        html +=   '</div>';
        html += '</div>';
    });

    $list.html(html);

    // Bind les clics sur les cartes après les avoir ajoutées au DOM
    $list.find('.card-details-link, .card-reference').on('click', function () {
        var id = parseInt($(this).data('id'));
        PortnetApp.ReclamationDetail.open(id);
    });
}
```

- `$list.html('<div class="spinner">...')` : **Injection de HTML**. Remplace le contenu de `$list` par ce HTML. C'est ainsi qu'on "crée" des éléments dynamiquement.
- **Construction de HTML par concaténation** : Le pattern `html += '...'` construit une longue chaîne de texte HTML, puis l'injecte en une seule fois avec `$list.html(html)`. C'est plus efficace que d'ajouter un élément à la fois.
- `'">' + rec.reference + '<'` : On intercale les données dynamiques entre les parties HTML statiques.
- `'status-badge ' + statut.key` → si `statut.key = 'affectee'`, ça donne `'status-badge affectee'`. Le CSS sait alors quelle couleur appliquer.
- `escapeHtml(rec.objet)` : **Sécurité !** Si l'objet contient `<script>alert('hack')</script>`, sans escapeHtml ça s'exécuterait. La fonction transforme `<` en `&lt;` pour l'afficher comme texte.
- `$(this).data('id')` : Lit la valeur de `data-id="20920"` sur l'élément cliqué.
- `parseInt(...)` : Convertit la chaîne `"20920"` en nombre entier `20920`.

---

## 8. js/reclamation-detail.js — Le Modal de Détails

### 8.1 Ouverture du Modal

```javascript
async function open(id) {
    $body.html('<div class="spinner"></div>'); // Spinner pendant le chargement
    $ref.text('');
    $badge.text('').attr('class', 'status-badge'); // Remet à zéro le badge

    $overlay.addClass('active'); // Ouvre le modal (CSS animate depuis la droite)

    // Fetch les données en PARALLÈLE (plus rapide qu'en séquentiel)
    var recPromise     = PortnetApp.API.getReclamationById(id);
    var historyPromise = PortnetApp.API.getStatusHistory(id);
    var docsPromise    = PortnetApp.API.getDocuments(id);

    var rec     = await recPromise;     // Attend la réclamation
    var history = await historyPromise; // Attend l'historique
    var docs    = await docsPromise;    // Attend les documents
```

- **Appels parallèles** : Au lieu de `await` chaque appel séquentiellement (attendre 1, puis attendre 2, puis attendre 3 = 300ms total), on lance les 3 en même temps et on attend les 3. Résultat : ~100ms au lieu de ~300ms.
- `$overlay.addClass('active')` : Ajoute la classe CSS `active` à l'overlay. Le CSS fait le reste (animation de glissement).
- `.attr('class', 'status-badge')` : Réinitialise toutes les classes à juste `status-badge` (sans `affectee`, `repondue`, etc. d'une ouverture précédente).

---

### 8.2 Construction de la Timeline

```javascript
async function buildTimelineEntry(entry, isFirst) {
    var statutApres = PortnetApp.API.getStatut(entry.id_statut_apres);
    var statusClass = 'status-' + statutApres.key; // ex: 'status-affectee'

    var labelHtml = '';
    if (isFirst || entry.id_statut_avant === null) {
        // Première entrée : juste le statut initial
        labelHtml = '<i class="fas fa-clipboard-list"></i> ' + statutApres.label;
    } else {
        // Transition : "Affectée → Répondue"
        var statutAvant = PortnetApp.API.getStatut(entry.id_statut_avant);
        labelHtml = '<i class="fas fa-clipboard-list"></i> ' +
                    statutAvant.label + ' → ' + statutApres.label;
    }

    var html = '<div class="timeline-entry ' + statusClass + '">';
    html += '<div class="timeline-dot"></div>'; // Le rond de la timeline
    html += '<div class="timeline-status-label">' + labelHtml + '</div>';
    html += '<div class="timeline-meta">' + userName + ' · ' + dateFormatted + '</div>';

    if (entry.commentaire) {
        html += '<div class="timeline-message-box">' + escapeHtml(entry.commentaire) + '</div>';
    }

    if (entry.reponse) {
        html += '<div class="timeline-response-box">';
        html +=   '<div class="timeline-response-label"><i class="fas fa-comment-dots"></i> Réponse</div>';
        html +=   '<div class="timeline-response-text">' + escapeHtml(entry.reponse) + '</div>';
        html += '</div>';
    }

    return html;
}
```

- `if (entry.commentaire)` : En JavaScript, une chaîne vide, `null`, ou `undefined` est "falsy" (évalue à faux). Donc `if (entry.commentaire)` est `true` seulement si le commentaire existe et n'est pas vide.
- `isFirst` : Un paramètre booléen. Si c'est la première entrée, on affiche juste "Affectée", pas "null → Affectée".

---

## 9. js/new-reclamation.js — Le Formulaire en 3 Étapes

### 9.1 L'état du formulaire

```javascript
var currentStep = 1; // Étape actuelle (1, 2, ou 3)
var totalSteps  = 3;
var formData = {     // Les données collectées par le formulaire
    id_type_reclamation: null,
    id_service_reclamation: null,
    objet: '',
    description: '',
    files: []
};
```

- Ces variables sont déclarées en dehors des fonctions mais à l'intérieur du module (IIFE). Elles sont donc "partagées" entre toutes les fonctions du module mais invisibles depuis l'extérieur.

---

### 9.2 Les Dropdowns Personnalisés

```javascript
function initTypeDropdown() {
    var $trigger = $('#typeTrigger'); // Le bouton qui ouvre le dropdown
    var $options = $('#typeOptions'); // Le div qui contient les options

    // Remplir les options depuis les données
    var types = PortnetApp.API.getAllTypes();
    var html = '';
    types.forEach(function (t) {
        html += '<div class="custom-dropdown-option" data-value="' + t.id + '">' + t.label + '</div>';
    });
    $options.html(html);

    // Ouvrir/fermer en cliquant sur le trigger
    $trigger.on('click', function (e) {
        e.stopPropagation(); // Empêche le clic de "remonter" jusqu'au document
        var isOpen = $options.hasClass('open');
        closeAllDropdowns();
        if (!isOpen) {
            $options.addClass('open');
            $trigger.addClass('open');
        }
    });

    // Sélectionner une option
    $options.on('click', '.custom-dropdown-option', function () {
        var value = parseInt($(this).data('value'));
        var label = $(this).text();

        formData.id_type_reclamation = value; // Sauvegarde la valeur

        $trigger.removeClass('placeholder').find('span').text(label); // Met à jour le bouton
        closeAllDropdowns();
        validateCurrentStep(); // Vérifie si on peut activer "Suivant"
    });
}
```

- `e.stopPropagation()` : Un clic "remonte" naturellement dans le DOM (du bouton → à son parent → à son grand-parent → ... → au document). On appelle ça le "bubbling". Si on ne bloque pas ce remontée, le clic atteindrait le `document` qui ferme tous les dropdowns. `stopPropagation()` bloque ce remontée.
- `$options.hasClass('open')` : Vérifie si le dropdown est déjà ouvert. Permet le toggle (cliquer une fois ouvre, cliquer à nouveau ferme).
- `$options.on('click', '.custom-dropdown-option', function() {...})` : Au lieu d'attacher un écouteur à chaque option (ce qui ne fonctionnerait pas car les options sont créées dynamiquement), on attache un seul écouteur au conteneur `$options` et on filtre par `.custom-dropdown-option`. C'est la **délégation d'événements**.

---

### 9.3 Le Drag & Drop de Fichiers

```javascript
function initFileUpload() {
    var $zone  = $('#fileUploadZone');
    var $input = $('#fileInput');

    // Glisser un fichier sur la zone
    $zone.on('dragover', function (e) {
        e.preventDefault(); // Empêche le comportement par défaut (ouvrir le fichier dans le navigateur)
        $(this).addClass('dragover'); // Applique un style visuel
    }).on('dragleave drop', function (e) {
        e.preventDefault();
        $(this).removeClass('dragover'); // Retire le style
    }).on('drop', function (e) {
        var files = e.originalEvent.dataTransfer.files; // Récupère les fichiers déposés
        addFiles(files);
    });

    // Choisir un fichier via le dialogue de fichiers
    $input.on('change', function () {
        addFiles(this.files);
        this.value = ''; // Réinitialise pour permettre de re-sélectionner le même fichier
    });
}
```

- `e.preventDefault()` sur `dragover` : Sans ça, le navigateur essaierait d'ouvrir le fichier qu'on glisse dessus (afficher le PDF dans le navigateur, par exemple).
- `e.originalEvent.dataTransfer.files` : jQuery enveloppe l'événement natif dans `originalEvent`. Les fichiers glissés sont accessibles via `dataTransfer.files`.

---

### 9.4 Navigation entre les Étapes

```javascript
function updateUI() {
    // 1. Affiche seulement l'étape courante
    $('.step-container').removeClass('active');
    $('#step' + currentStep).addClass('active');

    // 2. Met à jour la barre de progression
    var progress = (currentStep / totalSteps) * 100; // 33.33%, 66.66%, 100%
    $progressFill.css('width', progress + '%');

    // 3. Met à jour les cercles du stepper
    for (var i = 1; i <= totalSteps; i++) {
        var $circle = $('#stepperCircle' + i);
        $circle.removeClass('active inactive completed');

        if (i < currentStep) {
            $circle.addClass('completed').html('<i class="fas fa-check"></i>'); // Coche ✓
        } else if (i === currentStep) {
            $circle.addClass('active').text(i); // Chiffre actif
        } else {
            $circle.addClass('inactive').text(i); // Chiffre grisé
        }
    }

    // 4. Adapte les boutons du footer
    if (currentStep === 1) {
        $btnRetour.css('visibility', 'hidden'); // Invisible mais prend de la place (pas de saut de layout)
    } else {
        $btnRetour.css('visibility', 'visible');
    }

    if (currentStep === totalSteps) {
        $btnSuivant.hide();    // Complètement masqué
        $btnSoumettre.show();  // Apparaît
    } else {
        $btnSuivant.show();
        $btnSoumettre.hide();
    }
}
```

- `$('#step' + currentStep)` : Construit dynamiquement l'ID. Si `currentStep = 2`, ça donne `$('#step2')`.
- `visibility: hidden` vs `display: none` : `visibility: hidden` cache l'élément mais il prend toujours sa place dans le layout (pas de "saut"). `display: none` (`.hide()`) cache l'élément ET le retire du flux (la place est libérée).

---

### 9.5 Validation

```javascript
function isStepValid(step) {
    switch (step) {
        case 1: return formData.id_type_reclamation !== null;    // Une option choisie ?
        case 2: return formData.id_service_reclamation !== null; // Un service choisi ?
        case 3:
            formData.objet       = $('#inputObjet').val().trim(); // Lit et nettoie le texte
            formData.description = $('#inputSujet').val().trim();
            return formData.objet !== '' && formData.description !== ''; // Les deux remplis ?
        default: return false;
    }
}
```

- `.val()` : jQuery - lit la valeur d'un `<input>` ou `<textarea>`.
- `.trim()` : Supprime les espaces au début et à la fin. `"  hello  "` → `"hello"`.
- `!== null` vs `!== ''` : `null` pour les IDs (numérique, absence de valeur), `''` pour les chaînes de texte.

---

### 9.6 Soumission du Formulaire

```javascript
async function submitForm() {
    if (!isStepValid(currentStep)) return; // Sécurité : ne soumet pas si invalide

    $btnSoumettre.addClass('disabled').html('<i class="fas fa-spinner fa-spin"></i> Envoi...');

    formData.objet       = $('#inputObjet').val().trim();
    formData.description = $('#inputSujet').val().trim();

    try {
        var newRec = await PortnetApp.API.createReclamation(formData);

        // Succès
        $('.step-container').removeClass('active');
        $('#stepSuccess').addClass('active'); // Affiche l'écran de succès
        $('#successRef').text('Référence : ' + newRec.reference);
        $footer.hide();

        PortnetApp.ReclamationsList.load(); // Rafraîchit la liste
        PortnetApp.App.showToast('Réclamation #' + newRec.reference + ' créée !');

    } catch (err) {
        // En cas d'erreur
        $btnSoumettre.removeClass('disabled').html('<i class="fas fa-check"></i> Soumettre');
        PortnetApp.App.showToast('Erreur lors de la soumission. Réessayez.');
    }
}
```

- `try { ... } catch (err) { ... }` : Gestion d'erreurs. Si quelque chose plante dans le `try`, on atterrit dans le `catch`. Indispensable pour les opérations asynchrones (réseau, etc.).
- `fa-spin` : Une classe Font Awesome qui ajoute une rotation CSS à l'icône. Donne l'effet de chargement.

---

## 10. js/app.js — Le Chef d'Orchestre

### 10.1 Initialisation globale

```javascript
PortnetApp.App = (function () {

    function init() {
        // 1. Affiche le nom de l'utilisateur dans la navbar
        $('#navUserName').text(PortnetApp.CURRENT_USER.name);

        // 2. Initialise tous les modules
        PortnetApp.ReclamationsList.init();
        PortnetApp.ReclamationDetail.init();
        PortnetApp.NewReclamation.init();

        // 3. Bind les événements globaux
        bindPanelEvents();
        bindMenuEvents();
    }

    // ...

})();

// Démarre l'app quand le HTML est complètement chargé
$(document).ready(function () {
    PortnetApp.App.init();
});
```

- `$(document).ready(...)` : C'est le point de départ de toute l'application. jQuery exécute cette fonction seulement quand tout le HTML est prêt dans le navigateur.
- Sans ça, `$('#navUserName')` trouverait un élément qui n'existe pas encore et ne ferait rien.
- Les `.init()` de chaque module configurent les écouteurs d'événements.

---

### 10.2 Gestion des Panneaux et de l'Overlay

```javascript
function openPanel() {
    $('#centreAidePanel').addClass('active');   // Slide-in du panneau (CSS)
    $('#centreAideOverlay').addClass('active'); // Fond semi-transparent (CSS)
    $('#helpFloatingBtn').addClass('hidden');   // Cache le bouton flottant
}

function closePanel() {
    $('#centreAidePanel').removeClass('active');
    $('#centreAideOverlay').removeClass('active');
    $('#helpFloatingBtn').removeClass('hidden');
    $('#mesReclamationsSection').removeClass('active'); // Ferme aussi la sous-section
}
```

- Le code est simple car le CSS fait tout le travail visuel. JavaScript n'ajoute/retire que des classes CSS, et le CSS gère les animations.

---

### 10.3 Navigation dans le Menu

```javascript
function bindMenuEvents() {
    $('.panel-menu-item').on('click', function () {
        var action = $(this).data('action'); // Lit le data-action du bouton cliqué

        switch (action) {
            case 'mes-reclamations':
                openMesReclamations();
                break;
            case 'nouvelle-reclamation':
                PortnetApp.NewReclamation.open();
                break;
            case 'faq':
                showToast('Foires aux questions — bientôt disponible');
                break;
            // ...
        }
    });
}
```

- `switch (action)` : Alternative au `if/else if/else if/...`. Plus lisible quand on a plusieurs cas.
- `break` : Arrête le switch. Sans `break`, JavaScript continuerait à exécuter les cases suivants.
- `PortnetApp.NewReclamation.open()` : Appel d'une fonction **publique** d'un autre module. C'est ainsi que les modules communiquent entre eux.

---

### 10.4 Toast Notification

```javascript
function showToast(message) {
    var $toast = $('#toast');
    $toast.text(message).addClass('show'); // Affiche la notification
    setTimeout(function () {
        $toast.removeClass('show'); // La cache après 3 secondes
    }, 3000); // 3000 millisecondes = 3 secondes
}
```

- `setTimeout(function() { ... }, 3000)` : Exécute la fonction **une seule fois** après 3000ms de délai. C'est de l'asynchrone non-bloquant : le reste du code continue pendant ce délai.
- La notification apparaît, le code continue, et 3 secondes plus tard elle disparaît.

---

## 11. Comment Tout se Connecte : Le Cycle de Vie

### Scénario : L'utilisateur soumet une nouvelle réclamation

```
1. Navigateur charge index.html
         ↓
2. $(document).ready() → PortnetApp.App.init()
   - Met le nom de l'utilisateur dans la navbar
   - Attache tous les écouteurs d'événements
         ↓
3. L'utilisateur clique "Besoin d'aide ?"
   - app.js : openPanel() → ajoute 'active' au panel et overlay
         ↓
4. L'utilisateur clique "Nouvelle réclamation" (data-action="nouvelle-reclamation")
   - app.js : bindMenuEvents détecte le clic, lit l'action, appelle NewReclamation.open()
   - new-reclamation.js : reset() remet le formulaire à zéro, overlay s'affiche
         ↓
5. L'utilisateur remplit les 3 étapes
   - Étape 1 : Choisit le type → formData.id_type_reclamation = 2
   - Étape 2 : Choisit le service → formData.id_service_reclamation = 7
   - Étape 3 : Écrit l'objet et la description → formData.objet = '...', formData.description = '...'
   - À chaque choix : validateCurrentStep() active/désactive le bouton "Suivant"
         ↓
6. L'utilisateur clique "Soumettre"
   - new-reclamation.js : submitForm() appelle PortnetApp.API.createReclamation(formData)
   - api.js : createReclamation() crée un nouvel objet, l'ajoute à mockReclamations, retourne le nouvel objet
   - new-reclamation.js : Affiche l'écran de succès
   - new-reclamation.js : Appelle PortnetApp.ReclamationsList.load() (rafraîchit la liste)
   - new-reclamation.js : Appelle PortnetApp.App.showToast('Réclamation créée !')
```

---

## 12. Concepts JavaScript Expliqués Simplement

### `$` (jQuery)

jQuery est une bibliothèque qui simplifie JavaScript. Le `$` est son point d'entrée :

| Code jQuery | Ce que ça fait |
|---|---|
| `$('#id')` | Trouver un élément par ID |
| `$('.class')` | Trouver tous les éléments par classe |
| `$('#id').text('hello')` | Changer le texte |
| `$('#id').html('<b>hello</b>')` | Changer le HTML intérieur |
| `$('#id').addClass('active')` | Ajouter une classe CSS |
| `$('#id').removeClass('active')` | Retirer une classe CSS |
| `$('#id').hasClass('active')` | Vérifier si une classe est présente |
| `$('#id').on('click', fn)` | Écouter un événement clic |
| `$('#id').val()` | Lire la valeur d'un input |
| `$('#id').hide()` / `.show()` | Cacher / afficher |
| `$('#id').find('.child')` | Chercher un enfant dans l'élément |

---

### `async/await`

Sans async/await, le code asynchrone ressemble à ça (callbacks — difficile à lire) :
```javascript
getReclamations(function(data) {
    getStatut(data.id, function(statut) {
        afficher(data, statut); // "Callback hell"
    });
});
```

Avec async/await, c'est linéaire et lisible :
```javascript
async function charger() {
    var data   = await getReclamations();
    var statut = await getStatut(data.id);
    afficher(data, statut);
}
```

---

### Les Classes CSS dynamiques

Le principe fondamental de ce projet : **JavaScript ne crée pas de styles, il ajoute/retire des classes CSS**.

| Action JS | Effet CSS |
|---|---|
| `.addClass('active')` | Le panneau glisse depuis la droite |
| `.removeClass('active')` | Le panneau repart vers la droite |
| `.addClass('completed')` | Le cercle devient vert avec une coche |
| `.addClass('disabled')` | Le bouton devient gris et ne répond pas |

---

### Attributs `data-*`

Permet de stocker des données dans le HTML pour que JavaScript puisse les lire :
```html
<div data-id="20920" data-action="voir-detail">...</div>
```
```javascript
$(element).data('id')     // → 20920
$(element).data('action') // → "voir-detail"
```

---

### Truthy / Falsy (Vrai / Faux en JavaScript)

En JavaScript, ces valeurs sont considérées comme "fausses" (falsy) :
- `false`
- `0` (zéro)
- `''` (chaîne vide)
- `null`
- `undefined`

Donc `if (entry.commentaire)` est faux si commentaire est `null`, `undefined` ou `''`.

---

## 🔌 Pour Connecter un Vrai Backend

Quand le backend FastAPI sera prêt, il suffit de modifier **seulement `api.js`** :

```javascript
// AVANT (données mockées) :
async function getReclamations(searchTerm) {
    await delay();
    return PortnetApp.mockReclamations; // Données locales
}

// APRÈS (vraie API) :
async function getReclamations(searchTerm) {
    var url = BASE_URL + '/reclamations';
    if (searchTerm) url += '?search=' + encodeURIComponent(searchTerm);

    var response = await fetch(url, {
        headers: { 'Authorization': 'Bearer ' + getToken() }
    });

    if (!response.ok) throw new Error('Erreur réseau');
    return await response.json(); // Parse le JSON retourné par le serveur
}
```

Aucun autre fichier n'a besoin d'être modifié. C'est la puissance de l'isolation par module.

---

*Document créé le 01/07/2026 — Projet AI Réclamations Assistant — PortNet S.A.*
