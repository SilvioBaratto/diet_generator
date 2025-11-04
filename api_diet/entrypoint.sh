#!/bin/bash
set -e

echo "Starting Diet Generator API..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
until pg_isready -h db -p 5432 -U postgres; do
    echo "Database is unavailable - sleeping"
    sleep 2
done
echo "Database is ready!"

# Run migrations using DATABASE_URL from environment
echo "Running database migrations..."
alembic upgrade head
echo "Migrations completed!"

# Create default user if needed
echo "Setting up default user..."
python -c "
from app.database import database_manager
from app.repositories import UserRepository, UserSettingsRepository
import uuid

# Initialize database
database_manager.initialize()

with database_manager.get_session() as session:
    user_repo = UserRepository(session)
    settings_repo = UserSettingsRepository(session)

    # Check if default user exists
    default_email = 'admin@dietgenerator.com'
    existing_user = user_repo.get_by_email(default_email)

    if not existing_user:
        print('Creating default admin user...')
        user = user_repo.create_user(
            user_id=str(uuid.uuid4()),
            email=default_email
        )

        # Create default settings
        settings_repo.create_user_settings(
            settings_id=str(uuid.uuid4()),
            user_id=user.id,
            weight=70.0,
            height=175.0,
            goals='Stay healthy',
            other_data='Default user'
        )

        session.commit()
        print(f'✓ Default user created: {default_email}')
        print(f'  User ID: {user.id}')
    else:
        print(f'✓ Default user already exists: {default_email}')
        print(f'  User ID: {existing_user.id}')
"

echo "Setup complete! Starting application..."

# Execute the main command (start uvicorn)
exec "$@"
