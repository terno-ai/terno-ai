# Terno AI

Terno AI is an open-source, enterprise-grade Text-to-SQL solution that ensures accuracy, security, and performance when querying databases using natural language. It integrates domain knowledge management and SQL sanitization to generate safe and optimized queries.

## 🚀 Features

- **Metastore** - Stores domain knowledge to improve SQL generation accuracy

- **SQLShield** - Sanitizes queries, prevents harmful SQL execution, and enforces RBAC (Role-Based Access Control)

- **Optimized Query Generation** - Reduces prompt size while improving LLM-generated SQL efficiency

- **Enterprise Security** - Protects against SQL injection and unauthorized access

- **Multi-Database Support** - Works with major databases like PostgreSQL, MySQL, BigQuery, and more

- **LLM** - Use LLM of your choice without leaking data in your database to them

- **Open Source & Extensible** - Built for developers, data teams, and enterprises

## 📦 Installation

### Using Docker

1. `git clone https://github.com/terno-ai/terno-ai.git`
2. `cd terno-ai`
3. `docker compose up --build`

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

## 🔧 Configuring
Django server is running on http://127.0.0.1:8000 by default and admin url is http://127.0.0.1:8000/admin/. To configure go to the admin page.

### Basic config
1. Add LLM Configuration - `/admin/terno/llmconfiguration/`
2. Connect your Datasource - `/admin/terno/datasource/`. It will import your tables and columns.
3. Go to http://127.0.0.1:8000 to start using Terno.ai

### Adding table, column and row filters
1. To restrict a table's access globally use `/admin/terno/privatetableselector/`. To allow access to the globally restricted table to a specific group use `/admin/terno/grouptableselector/`
2. To restrict a column's access globally use `/admin/terno/privatecolumnselector/`. To allow access to the globally restricted column to a specific group use `/admin/terno/groupcolumnselector/`
3. To restrict a row's access globally use `/admin/terno/tablerowfilter/`. To allow access to the globally restricted row to a specific group use `/admin/terno/grouptablerowfilter/`

## Customizing Frontend (Optional)

### How to develop frontend
1. Run `npm run dev` inside frontend directory to run vite dev server
2. Make changes to src files in react frontend
3. Run the `build_frontend.sh` script to build and deploy to django directly
4. Commit both react changes and build files

## 🧪 Testing and Code Coverage

### To only run the test
`python manage.py test terno`

### To run the tests and collect coverage data
`coverage run manage.py test`

### To see a report of this data
`coverage report -m`

### To get annotated HTML
`coverage html`

Open the `htmlcov/index.html` file in browser

## 🔍 Row Filters
1. To restrict a table's access globally use `/admin/terno/tablerowfilter/`.

Ex. To restrict row access for `sales` table with filter `company_id = 10 and category_id not in (1, 2, 3)` add create tablerowfilter

2. To allow access to the globally restricted table to a specific group use `/admin/terno/grouptablerowfilter/`

Ex. To allow access to group `Groceries` access to the restricted category_ids and category_ids 12 and 13  which was added using previous method, create grouptablerowfilter with group `Groceries` and filter like
```where (
(company_id = 10 and category_id not in (1, 2, 3))
    AND (
        (category_id = 12)
            OR 
        (category_id = 13)
    )
)
```

## 🤝 Contributing

We welcome contributions! Feel free to open an issue or submit a pull request
