import sys

try:
    from invoke import task
except ImportError:
    # Fallback dummy decorator if invoke is not installed
    def task(func):
        return func

@task
def init_db(c=None):
    """Clean and recreate all database tables."""
    from app import app
    from recebi.ext.db import db
    from recebi import models  # Ensure models are loaded
    with app.app_context():
        print("Cleaning and recreating database tables...")
        print("Dropping old tables...")
        db.drop_all()
        print("Creating new tables...")
        db.create_all()
        print("Database initialized successfully!")

@task
def create_sindico(c=None):
    """Create the default Sindico user."""
    from app import app
    from recebi.ext.db import db
    from recebi.models import Usuario  # Ensure models are loaded
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        if not Usuario.query.filter_by(email='sindico@recebi.com').first():
            sindico = Usuario(
                nome='Administrador Principal', 
                email='sindico@recebi.com', 
                senha=generate_password_hash('senha123'), 
                perfil='Sindico',
                is_active=True
            )
            db.session.add(sindico)
            db.session.commit()
            print("Sindico created! Email: sindico@recebi.com | Password: senha123")
        else:
            print("Sindico already exists.")

@task
def run(c=None):
    """Run the Flask development server."""
    import subprocess
    subprocess.run(["flask", "run"])

@task
def test(c=None):
    """Run the test suite."""
    import subprocess
    subprocess.run(["pytest"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tasks.py [init-db | create-sindico | run | test]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    def run_task(task_func):
        if hasattr(task_func, "body"):
            task_func.body()
        else:
            task_func()

    if command == "init-db":
        run_task(init_db)
    elif command == "create-sindico":
        run_task(create_sindico)
    elif command == "run":
        run_task(run)
    elif command == "test":
        run_task(test)
    else:
        print(f"Unknown task: {command}")

