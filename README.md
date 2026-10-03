# compAI — Plateforme éducative IA

compAI est une application web éducative inspirée de la logique de mathia-encg : authentification, tableau de bord, chat IA, exercices, examens blancs, progression réelle et révisions.

## Fonctionnalités actuelles

- inscription et connexion avec token Bearer ;
- tableau de bord responsive ;
- chat IA Claude avec mémoire de session ;
- génération d’exercices de mathématiques appliquées ;
- soumission d’une réponse et enregistrement de la tentative ;
- progression calculée à partir des tentatives réellement stockées ;
- recherche web, PDF, fichiers et voix optionnels ;
- PostgreSQL ou SQLite ;
- rate limiting et validation de configuration ;
- runner séparé pour l’exécution Python en déploiement Docker.

## Démarrage local

```bash
cd compai
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# définir APP_TOKEN_SECRET ; ANTHROPIC_API_KEY active le chat IA réel
export APP_ENV=development
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Ouvrir `http://127.0.0.1:8000/`, créer un compte puis utiliser le tableau de bord.

## API éducative

- `GET /api/learning/overview` — indicateurs de l’utilisateur connecté ;
- `GET /api/exercises` — exercices disponibles ;
- `POST /api/exercises/generate` — générer un exercice ;
- `POST /api/exercises/{id}/submit` — enregistrer une tentative ;
- `GET /api/progress` — progression réelle calculée depuis les tentatives ;
- `GET /api/exams` — examens disponibles.

## Docker et production

```bash
cp .env.example .env
# définir APP_ENV=production, APP_TOKEN_SECRET, ANTHROPIC_API_KEY,
# POSTGRES_PASSWORD et SANDBOX_RUNNER_SECRET
docker compose up --build -d
```

En production, l’application refuse les secrets faibles, l’absence de clé Anthropic et le mode d’exécution Python local. Utiliser HTTPS, une sauvegarde PostgreSQL, des logs, une gestion de secrets et un runner sandbox adapté avant toute ouverture publique.

## Limites actuelles

La correction automatique détaillée et les examens blancs complets sont les prochaines extensions fonctionnelles. La progression n’affiche aucune donnée inventée : elle reste vide tant qu’aucune tentative réelle n’est enregistrée. Les clés API externes doivent être fournies par le propriétaire du déploiement et ne doivent jamais être publiées dans le frontend ou le chat.

## Tests

```bash
env APP_ENV=development CODE_EXECUTION_MODE=local pytest -q
```
