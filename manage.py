import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import create_app
from app.extensions import db

config_name = os.environ.get('FLASK_ENV')
app = create_app(config_name)
app.app_context().push()

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

@manager.command
def drop_tables():
    """Drop all existing tables."""
    print("Destroying tables...")
    db.drop_all()
    print("Tables destroyed successfully.")

@manager.command
def create_tables():
    """Create tables."""
    print("Creating new tables...")
    db.create_all()
    print("New tables created.")


if __name__ == '__main__':
    manager.run()
