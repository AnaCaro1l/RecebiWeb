import os
import shutil

# Script PowerShell como uma string

powershell_script = '''

if (-Not (Test-Path "venv")) {
    py -m venv venv
}

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force

. .\\venv\\Scripts\\Activate.ps1

py -m pip install --upgrade pip
pip install invoke

'''


# Salva o script em um arquivo temporário
with open("temp_script.ps1", "w") as f:
    f.write(powershell_script)

# Executa o script usando PowerShell

os.system("powershell -ExecutionPolicy Bypass -File temp_script.ps1")

# Remove o script temporário (opcional)
os.remove("temp_script.ps1")

def create_env_files():
    envs = {
        ".env.dev": (
            "FLASK_APP=app.py\n"
            "FLASK_DEBUG=1\n"
            "DATABASE_URI=sqlite:///recebi_dev.db\n"
            "JWT_SECRET_KEY=dev_secret_key_12345_long_and_secure_for_dev_environment\n"
        ),
        ".env.test": (
            "FLASK_APP=app.py\n"
            "FLASK_DEBUG=1\n"
            "DATABASE_URI=sqlite:///recebi_test.db\n"
            "JWT_SECRET_KEY=test_secret_key_12345_long_and_secure_for_test_environment\n"
        ),
        ".env.prod": (
            "FLASK_APP=app.py\n"
            "FLASK_DEBUG=0\n"
            "DATABASE_URI=mysql+pymysql://usuario:senha@localhost/recebi_db\n"
            "JWT_SECRET_KEY=prod_secret_key_abcde12345_long_and_secure_for_prod_environment\n"
        )
    }
    
    for filename, content in envs.items():
        if not os.path.exists(filename):
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Created {filename}")
        else:
            print(f"{filename} already exists")
            
    # Default to copying .env.dev to .env if .env doesn't exist
    if not os.path.exists(".env"):
        shutil.copyfile(".env.dev", ".env")
        print("Copied .env.dev to .env")
    else:
        print(".env already exists")

if __name__ == "__main__":
    create_env_files()

    print("\nExecuting Virtual Environment setup...")

    os.system(r".\venv\Scripts\python -m pip install .")

    print("\nExecuting database setup tasks...")

    os.system(r".\venv\Scripts\python tasks.py init-db")
    os.system(r".\venv\Scripts\python tasks.py create-sindico")