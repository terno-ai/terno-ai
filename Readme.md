# Terno AI

## Installation
1. `docker build -t terno-ai .`
2. `docker compose up`

## Frontend
Run the build_frontend.sh script to build and deploy to django directly

## How to develop frontend
1. Make changes to src files in react frontend
2. Run `npm run build` to generate assets
3. Copy html templates to django frontend app
4. Copy assets to frontend/static directory
5. Run `python manage.py collectstatic --no-input`
