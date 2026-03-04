# Development Commands

## Backend (Django + Strawberry GraphQL)

```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install dependencies
pip install -r backend/requirements/dev.txt

# Database setup
python backend/manage.py migrate
python backend/manage.py createsuperuser

# Run development server
python backend/manage.py runserver
```

## Security Layer (Rust)

```bash
# Development build and run
cd security
cargo run --dev

# Watch for changes
cargo watch -x 'run --dev'
```

## Frontend (React + Next.js)

```bash
# Install dependencies
cd frontend
npm install

# Generate GraphQL types
npm run graphql:generate

# Run development server
npm run dev
```

## Full Stack (Docker)

```bash
# Build and start all services
docker-compose -f docker/docker-compose.dev.yml up --build

# Start specific services
docker-compose -f docker/docker-compose.dev.yml up backend security frontend

# View logs
docker-compose -f docker/docker-compose.dev.yml logs -f backend
```

## GraphQL Development

```bash
# Access GraphQL playground
# http://localhost:8000/graphql

# Generate schema documentation
python backend/manage.py export_schema > schema.graphql
```

## Database Operations

```bash
# Create new migration
python backend/manage.py makemigrations

# Apply migrations
python backend/manage.py migrate

# Reset database (development only)
python backend/manage.py flush
```