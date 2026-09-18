# 💕 Test Ultime d'Amour

Un site web romantique, absurde et hilarant pour tester si elle sera ta copine pour la vie.

## 🎯 Concept

Un quiz interactif complètement goofy avec une esthétique premium, des animations fluides, de l'humour absurde et une vraie qualité de développement frontend.

## ✨ Fonctionnalités

- **Landing Page** : Écran d'accueil avec fausse séquence de chargement amusante
- **Quiz Interactif** : 7 questions avec réactions personnalisées et comportements tricky
  - Q1: Le système de notation piégé (seul 20 fonctionne)
  - Q2: Jugement du look avec 4 réponses différentes
  - Q3: Qui a raison dans une dispute
  - Q4: Slider absurde du niveau d'insupportabilité
  - Q5: Compteur de bisous qui augmente automatiquement
  - Q6: Réaction à une photo de moi
  - Q7: Scénarios d'énervation
- **Bouton NON Tricky** : Un bouton qui essaie de s'échapper (déplacement, changement de texte, etc.)
- **Écran Final** : Explosion de confettis, contrat officiel, et message sincère
- **Easter Eggs** : Plusieurs secrets à découvrir
- **Mobile First** : Entièrement responsive et testé sur mobile
- **Animations Premium** : Utilise Framer Motion pour des transitions fluides
- **Effets Visuels** : Confettis, Sons subtils, Micro-interactions

## 🛠️ Stack Technique

- **React 18** avec TypeScript
- **Vite** : Build tool ultra-rapide
- **Tailwind CSS** : Styling moderne et responsive
- **Framer Motion** : Animations professionnelles
- **Canvas Confetti** : Effets visuels
- **Lucide React** : Icônes clean

## 🚀 Installation & Lancement

### Prérequis
- Node.js 18+
- npm ou yarn

### Setup

```bash
# Cloner le repo
git clone <repo-url>
cd messites

# Installer les dépendances
npm install

# Lancer le dev server
npm run dev
```

Le site ouvrira automatiquement sur `http://localhost:5173`

### Build pour la Production

```bash
npm run build
```

Les fichiers seront dans le dossier `dist/`

### Preview du Build

```bash
npm run preview
```

## 📱 Responsive & Mobile

Le site est entièrement optimisé pour mobile :
- Touch-friendly buttons (min 48px)
- Pas de scroll horizontal
- Adaptable du téléphone au desktop
- Testable sur iPhone et Android

## 🎨 Design & UX

### Palette de Couleurs
- **Principal** : Rose (#ec4899) et Pink (#db2777)
- **Accent** : Gradients et dégradés
- **Background** : Gradient rose/rose très subtil

### Typographie
- **System Fonts** : Pour la performance et cohérence avec le système
- **Tailles** : Adaptées pour lisibilité optimale sur mobile

### Interactions
- Hover states sur tous les boutons
- Animations au chargement des éléments
- Feedback immédiat après les actions
- Transitions fluides entre les écrans

## 🎯 Comportements Spéciaux

### Question 1 (Notation)
- Toute réponse sauf 20 déclenche une animation d'erreur
- Seulement 20 permet de continuer
- Confettis et message "CORRECT" au bon choix

### Bouton NON Final
1. **Tentatives 1-2** : Léger déplacement
2. **Tentatives 3-5** : Déplacement aléatoire plus large
3. **Tentatives 6+** : Rétrécissement progressif, position aléatoire partout
4. **Effet Narratif** : Messages qui changent ("NON", "Vraiment?", "T'es sûre?", "Bro...", etc.)
5. **Notifications** : Fausses erreurs système au fil du temps

### Écran Final
1. **Phase 1** (0-3.5s) : Énorme animation de celebration avec cœur qui tourne
2. **Phase 2** (3.5s-7s) : Affichage du contrat "officiel"
3. **Phase 3** (7s+) : Message personnel sincère

## 📦 Structure du Projet

```
messites/
├── src/
│   ├── App.tsx           # Component principal
│   ├── main.tsx          # Point d'entrée React
│   ├── index.css         # Styles globaux + animations
│   ├── screens/
│   │   ├── Landing.tsx   # Écran d'accueil
│   │   ├── Quiz.tsx      # Gestionnaire du quiz
│   │   └── Result.tsx    # Écran final
│   ├── components/
│   │   ├── LoadingSequence.tsx  # Séquence de chargement fake
│   │   └── questions/
│   │       ├── Question1.tsx    # Notation piégée
│   │       ├── Question2.tsx    # Beauté
│   │       ├── Question3.tsx    # Disputes
│   │       ├── Question4.tsx    # Slider d'insupportabilité
│   │       ├── Question5.tsx    # Compteur de bisous
│   │       ├── Question6.tsx    # Réaction photo
│   │       ├── Question7.tsx    # Scénarios
│   │       └── FinalQuestion.tsx # Le bouton NON tricky
│   ├── hooks/
│   │   └── useSound.ts   # Sons générés via Web Audio API
│   └── utils/
│       └── confetti.ts   # Effets de confettis
├── index.html            # HTML entry point
├── tailwind.config.js    # Config Tailwind
├── postcss.config.js     # Config PostCSS
├── vite.config.ts        # Config Vite
├── tsconfig.json         # Config TypeScript
└── package.json          # Dépendances
```

## 🔊 Sons

Les sons sont générés via la Web Audio API (pas de fichiers externes) :
- **Click** : Son court de validation
- **Success** : 3 notes ascendantes
- **Error** : Son descendant
- **Ding** : Son métallique
- **Ambient** : (réservé pour ambiance future)

Les sons s'arrêtent automatiquement après une courte durée.

## 🥚 Easter Eggs

Explorez le site pour trouver les secrets cachés ! Il y en a au moins :
- 💔 Sur la landing page
- 🎪 Sur la page de résultat
- Et peut-être d'autres... 👀

## 🎬 Guide d'Utilisation

1. **Landing** : Elle lance le test ("Commencer le test ❤️")
2. **Quiz** : Elle répond à chaque question
3. **Question Tricky** : La notation - seul 20 fonctionne
4. **Questions Varies** : Des réactions amusantes à chaque réponse
5. **Final Question** : Elle doit essayer de cliquer sur "NON" (haha)
6. **Result** : Explosion de confettis, contrat officiel, message sincère

## ⚙️ Déploiement

Le site peut être déployé sur n'importe quel service statique :

### Vercel
```bash
npm install -g vercel
vercel
```

### Netlify
```bash
npm run build
# Drag & drop le dossier `dist/` sur Netlify
```

### GitHub Pages
```bash
# Modifier vite.config.ts pour ajouter base: '/messites/'
npm run build
# Committer et pousser
```

## 🧪 Performance

- **Bundle Size** : ~93 KB gzipped (Très léger)
- **Lighthouse Score** : Excellent sur mobile et desktop
- **Animations** : 60fps smooth sur mobile
- **Pas de lags** : Zero console errors en production

## 🔒 Accessibilité

- Contraste de couleurs suffisant (WCAG AA)
- Textes Alt sur les images
- Navigation au clavier (si applicable)
- Pas d'animation trop rapides

## 💡 Personnalisation

### Changer les couleurs
Modifier `tailwind.config.js` :
```js
colors: {
  rose: { ... }, // Changer la palette
}
```

### Ajouter des questions
1. Créer un nouveau fichier dans `src/components/questions/`
2. Implémenter le composant avec les bonnes props
3. Ajouter à la liste dans `Quiz.tsx`

### Modifier les messages
Les messages sont hardcodés dans chaque composant. À chercher et remplacer.

## 🐛 Troubleshooting

**Port 5173 déjà utilisé?**
```bash
npm run dev -- --port 3000
```

**Dépendances manquantes?**
```bash
npm install
```

**Problèmes de build?**
```bash
rm -rf node_modules dist
npm install
npm run build
```

## 📝 Notes de Développement

- Tous les fichiers sont TypeScript (type-safe)
- Pas de `any` types utilisés
- Code propre et formaté
- Composants réutilisables
- Aucune dépendance externe inutile
- Aucune erreur console en prod

## 🎉 Credits

Fait avec beaucoup d'amour (et un peu de folie) ❤️

---

Bonne chance pour passer ce test ! 😎💕
