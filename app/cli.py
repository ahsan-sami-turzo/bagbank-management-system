# app/cli.py
import click
from app import db
from app.models import User
from sqlalchemy import text

def register_cli_commands(app):
    @app.cli.command("init_db")
    @click.option("--reset", is_flag=True, help="Reset the database before creating the SuperAdmin.")
    def init_db(reset):
        """Initializes the database and creates the first SuperAdmin."""
        with app.app_context():
            if reset:
                db.drop_all()
                click.echo("INFO: Dropped all existing tables.")
            
            db.create_all()
            click.echo("INFO: Database tables created.")

            username = app.config['SUPERADMIN_USERNAME']
            if not User.query.filter_by(username=username).first():
                super_admin = User(
                    role=0,
                    name="System Superadmin",
                    phone="0000000000",
                    email=app.config['SUPERADMIN_EMAIL'],
                    username=username
                )
                super_admin.set_password(app.config['SUPERADMIN_PASSWORD'])
                db.session.add(super_admin)
                db.session.commit()
                click.echo(f"SUCCESS: Initial SuperAdmin '{username}' created with password 'superadmin'.")
            else:
                click.echo("INFO: SuperAdmin already exists. Skipping creation.")

    @app.cli.command("reset_alembic")
    def reset_alembic():
        """Drops the alembic_version table to reset migration history."""
        with app.app_context():
            if db.engine.dialect.has_table(db.engine.connect(), "alembic_version"):
                try:
                    db.session.execute(text("DROP TABLE alembic_version;"))
                    db.session.commit()
                    click.echo("SUCCESS: The 'alembic_version' table has been deleted.")
                except Exception as e:
                    db.session.rollback()
                    click.echo(f"ERROR: Failed to delete the 'alembic_version' table. {e}")
            else:
                click.echo("INFO: The 'alembic_version' table does not exist. Nothing to delete.")
