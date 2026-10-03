# Mettre compAI en ligne — GRATUIT, sans carte bancaire

compAI est prêt à être publié sur **Render** (plan gratuit) via un dépôt **GitHub** (gratuit).
Le mode `COMPAI_DEMO=1` est activé : le site démarre **sans aucune clé payante**.
Le chat IA affiche un message « clé non configurée » tant qu'aucune `ANTHROPIC_API_KEY` n'est ajoutée.

---

## Étape 1 — GitHub (5 min, gratuit)
1. Créer un compte : **github.com** → « Sign up » (email + mot de passe, aucune carte).
2. Bouton **+** (haut à droite) → **New repository** → nom : `compai` → **Public** ou **Private** → « Create repository ».
3. Sur la page du dépôt vide : **uploading an existing file** → glisser-déposer le **contenu** du dossier `compai` de l'archive (tous les fichiers et sous-dossiers, PAS l'archive elle-même).
4. Tout en bas : « Commit changes » → **Commit**.

## Étape 2 — Render (5 min, gratuit, sans carte)
1. Créer un compte : **render.com** → « Sign up » (email ; carte **non demandée** pour le plan gratuit).
2. Cliquer **New +** → **Blueprint** → « Configure account » → Connecter GitHub (autoriser Render).
3. Choisir le dépôt `compai` → Render lit `render.yaml` et crée le service tout seul.
4. « Apply » → attendre le build (5 à 8 min).
5. Ouvrir l'URL : `https://compai.onrender.com` → le site est en ligne ✅

> ⚠️ Le plan gratuit « dort » après 15 min sans visite : le 1er chargement peut prendre 30 à 60 secondes.

## Étape 3 (conseillé) — Base de données gratuite pour garder les comptes
Sans `DATABASE_URL`, tout est en SQLite : les comptes sont **effacés à chaque redéploiement**.
1. Créer une base **PostgreSQL gratuite** sur **neon.tech** (email suffisant) ou **supabase.com**.
2. Copier la « connection string » (elle ressemble à `postgresql://user:pass@host/db`).
3. Dans Render : service `compai` → **Environment** → **Add Environment Variable** :
   - `DATABASE_URL` = la connection string
4. Déployer (bouton **Deploy**). Les comptes deviennent permanents.

## Étape 4 (optionnel) — Activer le vrai chat IA
1. Créer une clé sur **console.anthropic.com** (des crédits de bienvenue sont offerts au premier essai).
2. Render → Environment → `ANTHROPIC_API_KEY` = ta clé → Deploy.
3. (Facultatif) `TAVILY_API_KEY` pour la recherche web, `OPENAI_API_KEY` + `ELEVENLABS_API_KEY` pour la voix.

## Tests après mise en ligne
- [ ] `https://compai.onrender.com/` affiche l'interface
- [ ] `https://compai.onrender.com/health` répond `{"status":"ok", ...}`
- [ ] Créer un compte + se connecter
- [ ] Générer un exercice et soumettre une réponse → la progression s'affiche
- [ ] Ouvrir le chat → message d'activation IA (ou vraie réponse si clé ajoutée)

## Sécurité (mode démo)
- `CODE_EXECUTION_MODE=disabled` : l'exécution de code Python est bloquée sur le serveur.
- `APP_TOKEN_SECRET` est généré automatiquement par Render.
- Ne jamais mettre de clé API dans le code ou le fichier HTML : uniquement dans les variables Render.