# Terno AI

## Installation

### Docker
1. `docker build -t terno-ai .`
2. `docker compose up`

### Without docker
1. Clone Repository `git clone git@github.com:terno-ai/terno-ai.git`
2. Change directory `cd terno-ai`
3. Create virtualenv `virtualenv -p python3.10 venv`
4. Activate venv `. venv/bin/activate`
5. Install requirements `pip install -r requirements.txt`
6. Copy env sample `cp env-sample.sh env.sh`
7. Source env file `source env.sh`
8. Migrate Database `python terno/manage.py migrate`
9. Run server `python terno/manage.py runserver`

## Frontend
Run the `build_frontend.sh` script to build and deploy to django directly

## How to develop frontend
1. Make changes to src files in react frontend
2. Run `npm run build` to generate assets
3. Copy html templates to django frontend app
4. Copy assets to frontend/static directory
5. Run `python manage.py collectstatic --no-input`
