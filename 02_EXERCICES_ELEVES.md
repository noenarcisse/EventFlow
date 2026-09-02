# Exercices élèves — React Testing avec EventFlow

## Mode d'emploi

Travaillez dans `frontend`. Une tâche correspond à un petit test ou à une petite configuration. Il est normal de ne pas terminer le document.

Difficulté : ★ ultra simple · ★★ simple · ★★★ intermédiaire · ★★★★ bonus avancé.

Réflexe de la journée : **RENDER → FIND → ACT → ASSERT**.

Les premiers exercices indiquent précisément les outils à employer. Ensuite, les consignes décrivent surtout le comportement attendu : à vous de choisir la query et le matcher les plus adaptés. Lorsqu'une notion nouvelle apparaît, une aide plus détaillée est de nouveau fournie.

## A — Setup étudiant

### A1 — Installer les outils ★

Depuis `frontend`, installez les outils de test :

```bash
npm i -D vitest @vitest/coverage-v8 jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

**Notions :** dépendances de développement, runner, DOM simulé.

### A2 — Configurer Vite ★

Dans `vite.config.js`, ajoutez Vitest sans retirer le plugin React ni le proxy existant. La propriété `test` doit contenir `environment: "jsdom"`, `globals: true` et `setupFiles: "./src/test/setup.js"`.

**Notions :** configuration Vitest, jsdom, globals.

### A3 — Créer le fichier de setup ★

Créez `src/test/setup.js` et importez `@testing-library/jest-dom/vitest` afin d'activer les assertions DOM.

**Notions :** setup global, jest-dom.

### A4 — Ajouter les scripts et vérifier ★

Ajoutez dans `package.json` les scripts `test`, `test:run` et `test:coverage` indiqués par le formateur. Créez un test `expect(true).toBe(true)`, puis lancez `npm run test:run`.

**Notions :** scripts npm, premier test vert.

## B — Render et assertions ultra simples

Créez vos fichiers près des composants ou dans `src/test`. Utilisez des imports relatifs simples.

### B1 — Logo : rendre le composant ★

Rendez `<Logo />`. Récupérez le SVG avec `screen.getByLabelText("eventflow")`, puis vérifiez qu'il est présent avec `toBeInTheDocument`.

**Notions :** `render`, `screen.getByLabelText`, `toBeInTheDocument`.

### B2 — Logo : nom accessible ★

Rendez `Logo`, retrouvez l'élément étiqueté `eventflow`, puis vérifiez son attribut `aria-label` avec `toHaveAttribute`.

**Notions :** label accessible, attribut.

### B3 — Logo : largeur par défaut ★

Rendez `<Logo />`, retrouvez-le par son label et vérifiez que son attribut `width` vaut `34`.

**Notions :** valeur par défaut, `toHaveAttribute`.

### B4 — Avatar : initiales du nom ★

Rendez `<Avatar user={{ full_name: "Camille Client" }} />` et vérifiez que les initiales `CC` sont visibles.

**Indice :** cherchez le texte affiché.

### B5 — Avatar : repli sur l'email ★

Rendez `Avatar` avec seulement `email: "client@eventflow.test"`. Vérifiez que le fallback visible est `C`.

### B6 — EventCard : rendre la carte ★

Créez directement un événement contenant `id`, `title`, `city`, `venue`, `starts_at` et `cover_color`. Rendez `EventCard` dans un `MemoryRouter`, puis vérifiez que son titre apparaît.

**Indice :** gardez l'objet événement dans le test.

### B7 — EventCard : titre ★

Avec `title: "Brussels Testing Days"`, vérifiez que la carte affiche exactement ce titre.

### B8 — EventCard : ville ★

Avec `city: "Bruxelles"`, vérifiez que la ville apparaît dans la carte.

### B9 — EventCard : lieu ★

Avec `venue: "Tour & Taxis"`, vérifiez que le lieu est visible.

### B10 — EventCard : lien ★

Vérifiez qu'une `EventCard` contient un lien accessible.

**Indice :** préférez une query sémantique à un sélecteur CSS.

### B11 — EventCard : destination ★

Rendez une carte avec `id: 7`. Vérifiez que son lien conduit à `/events/7`.

### B12 — EventCard : textes fixes ★

Vérifiez que la carte affiche les deux libellés fixes `Billets` et `Voir`.

## C — Props visibles

Ici, concentrez-vous sur le contrat : **une prop différente doit produire un résultat visible différent**.

### C1 — Logo : taille 60 ★

Rendez `<Logo size={60} />` et vérifiez que sa largeur et sa hauteur valent `60`.

### C2 — Logo : taille 18 ★

Refaites le test avec `size={18}`. Les deux dimensions doivent maintenant valoir `18`.

### C3 — Avatar : taille 50 ★

Rendez un avatar sans image avec `size={50}`. Vérifiez que ses dimensions visibles sont de `50px` sur `50px`.

**Indice :** jest-dom permet aussi de vérifier les styles.

### C4 — Avatar : deux initiales maximum ★

Avec `full_name: "Alice Bob Charlie"`, vérifiez que l'avatar affiche `AB`.

### C5 — Avatar : image si URL ★

Fournissez un nom et `avatar: "/camille.png"`. Vérifiez que l'image correspondant à Camille utilise cette URL.

**À vous de choisir :** la query sémantique et le matcher d'attribut.

### C6 — EventCard : un autre titre ★

Remplacez le titre par `Namur QA Night`. Vérifiez que le nouveau titre apparaît.

### C7 — EventCard : un autre id ★★

Rendez une carte avec `id: 42`. Vérifiez que sa destination change en conséquence.

### C8 — Avatar : avec et sans image ★★

Écrivez deux tests séparés :

- un utilisateur avec avatar affiche une image ;
- un utilisateur sans avatar affiche ses initiales.

Choisissez vous-même les queries permettant de distinguer les deux branches.

## D — Choisir la bonne query

Dans cette section, le comportement à vérifier est donné, mais le choix de la query fait partie de l'exercice.

### D1 — Logo par label ★

Retrouvez le logo sans classe CSS grâce à son `aria-label`. Expliquez en commentaire pourquoi cette query fonctionne sur le SVG actuel.

Testez aussi mentalement cette question : le SVG possède-t-il automatiquement le rôle `img` ?

### D2 — EventCard par titre ★

Retrouvez `Brussels Testing Days` comme titre de niveau 3, puis vérifiez sa présence.

**Indice :** utilisez le rôle, le nom et le niveau du heading.

### D3 — Compter les liens ★

Rendez deux `EventCard` dans le même `MemoryRouter`. Vérifiez que le document contient exactement deux liens.

**À vous de choisir :** la query plurielle et le matcher de quantité.

### D4 — Avatar absent ★★

Rendez un avatar sans URL d'image et vérifiez qu'aucune image n'est présente.

Une query `getBy...` échoue immédiatement lorsqu'elle ne trouve rien. Pour tester une absence, découvrez la variante `queryBy...`, qui renvoie `null`.

### D5 — Détecter un défaut d'accessibilité ★★

Rendez `Login` avec le contexte minimal fourni par le formateur, puis essayez :

```jsx
screen.getByLabelText("Email");
```

Observez attentivement l'échec et le DOM affiché par Testing Library. Répondez avant de chercher une autre query : **problème du test ou du produit ?** Justifiez votre diagnostic, puis trouvez un moyen temporaire de récupérer le champ sans sélecteur CSS.

**Notions :** association label/champ, diagnostic QA.

## E — userEvent et interactions façon Counter

Le formateur fournit un mock API minimal qui renvoie un événement avec une seule catégorie. L'objectif est l'interaction, pas encore `vi.mock`.

### E1 — Quantité initiale ★

Rendez `EventDetail` dans un `MemoryRouter` sur la route `/events/7`. Après l'apparition du titre, vérifiez que la quantité commence à `0`.

### E2 — Boutons de quantité ★

Vérifiez l'état initial des trois actions :

- `-` est désactivé ;
- `+` est activé ;
- Continuer est désactivé.

### E3 — Un clic sur + ★★

Créez l'utilisateur puis cliquez une fois sur `+` :

```jsx
const user = userEvent.setup();
await user.click(button);
```

Vérifiez ensuite la quantité `1` et le texte `Total (1 billet)`.

### E4 — Double clic sur + ★★

Double-cliquez sur `+`. La quantité doit devenir `2` et le libellé doit employer `billets` au pluriel.

### E5 — Triple clic sur + ★★

Triple-cliquez sur `+`. Vérifiez la quantité `3` ainsi que le total monétaire correspondant.

### E6 — Décrémenter ★★

Ajoutez deux billets, puis retirez-en un. Vérifiez que la quantité revient à `1`.

### E7 — Plafond de six ★★

Ajoutez six billets. Vérifiez la quantité obtenue et l'état du bouton `+` lorsque la limite est atteinte.

### E8 — Code promo en majuscules ★★

Saisissez `welcome10` dans le champ promo et vérifiez la transformation visible. Videz ensuite le champ, saisissez `vip25` et vérifiez de nouveau le résultat.

**À vous de choisir :** comment trouver le champ et comment vérifier sa valeur.

## F — Formulaires avec Login

Le formateur fournit un petit wrapper Auth + Router. Commencez par l'état des champs ; la soumission vient ensuite.

### F1 — Valeurs initiales ★★

Vérifiez les valeurs initiales des champs email et mot de passe de démonstration.

**Indice :** vous connaissez déjà les valeurs affichées ; choisissez une query adaptée.

### F2 — Modifier l'email ★★

Remplacez l'email initial par `qa@eventflow.test`, puis vérifiez la valeur finale du champ.

### F3 — Afficher le champ conditionnel ★★

Passez en mode création de compte. Vérifiez le nouveau titre et l'apparition du champ supplémentaire.

### F4 — Revenir à Connexion ★★

Passez en inscription, puis revenez à Connexion. Vérifiez le titre et l'absence du champ supplémentaire.

**Indice :** pour vérifier une absence, réutilisez la famille `queryBy...`.

### F5 — Soumettre avec Entrée ★★★

Remplacez l'email, placez le focus dans le mot de passe et soumettez avec :

```jsx
await user.keyboard("{Enter}");
```

Vérifiez que la fonction `login` fournie a reçu l'email et le mot de passe attendus.

## G — vi.fn, très progressivement

`vi.fn` est une notion nouvelle : une fonction mockée se souvient de ses appels, comme `Mock()` en Python.

### G1 — Une fonction mémorise un appel ★

Commencez sans React :

```jsx
const fn = vi.fn();

fn();

expect(fn).toHaveBeenCalled();
```

Faites passer ce test et expliquez ce que la fonction a mémorisé.

### G2 — Nombre et arguments ★★

Appelez une fonction mockée deux fois avec des arguments différents. Vérifiez :

```jsx
expect(fn).toHaveBeenCalledTimes(2);
expect(fn).toHaveBeenCalledWith(/* un argument attendu */);
```

### G3 — Callback de Login ★★

Créez un callback async contrôlé :

```jsx
const login = vi.fn().mockResolvedValue();
```

Fournissez-le via le contexte de test, soumettez `Login`, puis vérifiez qu'il a reçu les valeurs présentes dans le formulaire.

## H — Mocks simples

### H1 — mockReturnValue sur useAuth ★★★

Contrôlez la valeur retournée par `useAuth` :

```jsx
useAuth.mockReturnValue({
  user: null,
  logout: vi.fn(),
});
```

Rendez `NavBar` dans un `MemoryRouter`. Vérifiez le lien `Connexion` et l'absence de `Mes billets`.

### H2 — Premier vi.mock ★★★

`vi.mock` remplace ici le module API entier. Commencez avec une seule méthode :

```jsx
vi.mock("../api", () => ({
  default: {
    get: vi.fn(),
  },
}));
```

Faites résoudre `get` avec `{ data: [] }`, rendez `Catalog`, puis vérifiez l'état vide après le chargement.

**Notions :** `vi.mock`, `mockResolvedValue`, mock de module simple.

## I — Async et API

### I1 — Premier findBy ★★★

`findBy` sert à attendre un élément qui apparaîtra plus tard :

```jsx
const message = await screen.findByText("Aucun evenement trouve.");

expect(message).toBeInTheDocument();
```

Faites résoudre l'API avec une liste vide. Vérifiez d'abord `Chargement...`, puis utilisez ce principe pour attendre l'état vide.

### I2 — Une carte apparaît ★★★

Faites résoudre l'API avec un événement complet. Rendez `Catalog` dans un `MemoryRouter`, attendez l'apparition de son titre, puis vérifiez sa ville.

**Indice :** choisissez une query asynchrone adaptée au titre.

### I3 — Recherche et waitFor ★★★★

`waitFor` répète une assertion jusqu'à ce qu'elle réussisse ou que le délai expire :

```jsx
await waitFor(() => {
  expect(/* appel attendu */).toHaveBeenCalledWith(/* arguments */);
});
```

Après le chargement initial, saisissez `Bruxelles` et cliquez sur `Rechercher`. Attendez que l'API ait été appelée avec `{ params: { q: "Bruxelles" } }`.

## J — Debugging QA

Pour chaque test rouge, répondez avant de modifier du code :

1. Qu'attend le test ?
2. Que fait réellement l'application ?
3. Pourquoi cela échoue-t-il ?
4. Le problème vient-il du test ou de l'application ?

### J1 — Mauvais texte ★

Partez d'un test qui cherche `Brussels Test Day` alors que la prop vaut `Brussels Testing Days`. Diagnostiquez l'échec et corrigez ce qui doit l'être.

### J2 — Oubli de await ★★

Retirez volontairement `await` devant `user.click`. Observez et expliquez le résultat, puis rendez le test fiable.

### J3 — Vrai défaut produit ★★★

Écrivez l'attente raisonnable `getByLabelText("Email")`. Analysez le DOM et proposez le correctif produit sans contourner le problème avec un sélecteur CSS.

## K — Coverage

### K1 — Lancer le rapport ★

Lancez `npm run test:coverage`. Relevez les valeurs de statements, branches, functions et lines, puis expliquez avec vos mots ce que chacune mesure.

### K2 — Choisir un manque utile ★★

Choisissez une branche métier non testée, écrivez un test pertinent, puis relancez la couverture. Commentez le changement sans chercher artificiellement 100 %.

## L — Bonus avancés

### L1 — Fixture et helper de render ★★★★

Extrayez l'événement répété dans une fixture et créez un `renderWithRouter`. Comparez la lisibilité avant/après sans masquer les props particulières à chaque test.

### L2 — AuthProvider et mock partiel ★★★★

Conservez les vrais utilitaires du module API avec `importOriginal`, remplacez uniquement le client API, simulez `/api/auth/me`, puis vérifiez l'utilisateur chargé dans un consommateur du contexte.

### L3 — Checkout et fake timers ★★★★

Mockez les deux appels API de `Checkout`, contrôlez le compte à rebours avec les fake timers, puis vérifiez le passage d'une réservation active à une réservation expirée. Restaurez toujours les vrais timers à la fin.

### L4 — Routes protégées et navigation ★★★★

Configurez les routes en mémoire et contrôlez `useAuth`. Vérifiez d'abord la redirection d'un visiteur, puis l'accès accordé à un utilisateur connecté.
