[![codecov](https://codecov.io/gh/terno-ai/terno-ai/graph/badge.svg?token=J9K3H77UOZ)](https://codecov.io/gh/terno-ai/terno-ai)

# Terno AI

Terno AI is a team of AI data scientist for your structured data in organizations.

It an open-source, enterprise-grade solution that ensures accuracy, security, and performance when querying databases using natural language. It integrates domain knowledge management and SQL sanitization to generate safe and optimized queries. It builds the supervised and unsupervised machine learning models along with domain specific algorithms such as job shop scheduler. It also prepares charts and schedules email reports.

## 🚀 Features

### Metastore
- Stores domain knowledge—automatically inferred or provided by experts—to enhance SQL generation accuracy.
- Supports seamless, automatic updates to the Metastore.
- Captures inferred knowledge from data to improve query precision.

### SQLShield
- **Query Sanitization**: Prevents harmful SQL execution and enforces Role-Based Access Control (RBAC) without direct database interaction.
- **Optimized Query Generation**: Minimizes prompt size while boosting the efficiency of LLM-generated SQL.
- **Enterprise Security**: Guards against SQL injection and unauthorized access.

### Semantic Layer on Databases
Databases are critical for organizations but are limited to syntactic searches rather than semantic understanding. For example, searching for "blue jeans" in an e-commerce database might miss products labeled "navy denims" due to keyword-based limitations.

Terno AI addresses this with a semantic layer, enabling text searches based on meaning and similarity, not just exact matches.

### Artifact Store
Terno AI generates intermediate artifacts—such as datasets, machine learning models, code, graphs, and charts—to answer complex queries. These artifacts are saved in the Artifact Store, making them reusable across teams. This accelerates result generation and enhances data understanding within organizations.

### Enterprise Tooling Augmentation
Every organization has unique workflows, such as sending emails, calling internal APIs, or scheduling jobs. Terno AI offers an extensible tooling augmentation layer to integrate with these processes. For example, you can instruct Terno to "send a report via email to my team every Monday morning."


### Multi-Database Support
    
- Works with major databases like PostgreSQL, MySQL, BigQuery, and more
- Also integrate with most of the ERPs such as Odoo.

### Works with any LLM

- Use LLM of your choice without leaking data in your database to them
- It also support multi-LLMs setup where you may have one LLM for long form generation, second LLM backend tasks and other LLM for text embeddings generation.

### Open Source & Extensible
    
 - Built for developers, data teams, and enterprises


## 📦 Installation

### Using Docker

1. `git clone https://github.com/terno-ai/terno-ai.git`
2. `cd terno-ai`
3. `docker compose up --build`

### Without docker
1. Clone Repository `git clone git@github.com:terno-ai/terno-ai.git --depth 1`
2. Change directory `cd terno-ai`
3. Build frontend `. ./build_frontend.sh`
4. Create virtualenv `virtualenv -p python3.10 venv`
5. Activate venv `. venv/bin/activate`
6. Install requirements `pip install -r requirements.txt`
7. Source env file `source env-sample.sh`
8. Migrate Database `python terno/manage.py migrate`
9. Run server `python terno/manage.py runserver`

## 🔧 Configuring
Django server is running on http://127.0.0.1:8000 by default and admin url is http://127.0.0.1:8000/admin/. To configure go to the admin page. 
1. Default admin user email is `admin@example.com`  
2. password is `Superadmin@123`

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

## Celery
1. Run rabbitmq for message broker
2. `celery -A mysite worker --loglevel=info`

## 🤝 Contributing

We welcome contributions! Feel free to open an issue or submit a pull request
