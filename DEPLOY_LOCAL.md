# Déployer compAI sur votre propre ordinateur

## Prérequis

- Docker Desktop installé et lancé ;
- idéalement un ordinateur qui reste allumé et connecté ;
- un nom de domaine pour une URL publique ;
- accès à la configuration de votre routeur si vous utilisez une IP publique.

## Installation

1. Décompresser `compai-ready.zip`.
2. Ouvrir un terminal dans le dossier `compai`.
3. Copier la configuration :

```bash
cp .env.example .env
```

Sous Windows PowerShell :

```powershell
Copy-Item .env.example .env
```

4. Modifier `.env` et définir au minimum :

```env
APP_ENV=production
ANTHROPIC_API_KEY=votre_cle_anthropic
APP_TOKEN_SECRET=une_valeur_aleatoire_d_au_moins_32_caracteres
POSTGRES_PASSWORD=un_mot_de_passe_fort
SANDBOX_RUNNER_SECRET=un_autre_secret_aleatoire
```

5. Changer les valeurs par défaut dans `docker-compose.yml` et `Caddyfile` si nécessaire.
6. Lancer :

```bash
docker compose -f docker-compose.yml -f docker-compose.local.yml up --build -d
```

7. Vérifier :

```bash
docker compose ps
curl http://127.0.0.1:8000/health
```

L'interface locale est disponible sur `http://127.0.0.1:8000`.

## Rendre le site accessible depuis Internet

- créer un enregistrement DNS `A` vers l'adresse IP publique de votre connexion ;
- remplacer `example.com` dans `Caddyfile` par ce domaine ;
- transférer les ports TCP 80 et 443 de votre routeur vers l'ordinateur ;
- relancer `docker compose ... up -d`.

Caddy demandera automatiquement un certificat HTTPS à Let's Encrypt si le domaine pointe correctement vers votre connexion et si les ports 80/443 sont accessibles.

## Limite importante

Votre ordinateur doit rester allumé, connecté à Internet et ne pas passer en veille. Si l'adresse IP change, utilisez un DNS dynamique. Pour une disponibilité 24 h/24 plus fiable, un serveur cloud reste préférable.

## Commandes utiles

```bash
docker compose logs -f app
docker compose restart
docker compose down
```
