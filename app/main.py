from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Union
from api.v1.endpoints import chatbot, auth, tenant
import typer
import subprocess
import os
from sqlalchemy.orm import Session
from core.config import get_db, Base
from models.user import User
from models.chatbot import Chatbot
from models.tenant import BusinessProfile
import models  
from api.v1.endpoints.auth import get_current_user_from_cookie, get_current_user_from_cookie_optional

app = FastAPI(
    title="ChatAI SaaS Chatbot Service",
    description="A SaaS platform for businesses to create and embed chatbots.",
    version="0.1.0"
)

# Serve static files
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static"
)

# Admin templates
admin_templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db), user_id: int = None):
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized")
    users = db.query(User).all()
    chatbots = db.query(Chatbot).all()
    tenants = db.query(BusinessProfile).all()
    # Build owner email maps
    user_map = {u.id: u.email for u in users}
    chatbot_list = []
    for bot in chatbots:
        chatbot_list.append({
            'id': bot.id,
            'name': bot.name,
            'owner_id': bot.owner_id,
            'owner_email': user_map.get(bot.owner_id, ''),
            'business_profile_id': bot.business_profile_id,
            'prompt': bot.prompt
        })
    tenant_list = []
    for t in tenants:
        # Find owner (first user with this business_profile_id)
        owner = next((u for u in users if u.business_profile_id == t.id), None)
        tenant_list.append({
            'id': t.id,
            'name': t.name,
            'settings': t.settings,
            'owner_id': owner.id if owner else '',
            'owner_email': owner.email if owner else ''
        })

    return admin_templates.TemplateResponse(
        "admin_panel.html",
        {
            "request": request,
            "user": user,
            "user_authenticated": True,
            "users": users,
            "chatbots": chatbot_list,
            "tenants": tenant_list
        }
    )

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, user=Depends(get_current_user_from_cookie_optional)):
    if user:
        return RedirectResponse(url="/dashboard")
    return admin_templates.TemplateResponse("login.html", {"request": request, "user_authenticated": False})

@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, user=Depends(get_current_user_from_cookie_optional)):
    if user:
        return RedirectResponse(url="/dashboard")
    return admin_templates.TemplateResponse("signup.html", {"request": request, "user_authenticated": False})

@app.get('/',response_class=HTMLResponse)
def home(request:Request, user=Depends(get_current_user_from_cookie_optional)):
    if user:
        return admin_templates.TemplateResponse('home.html',{"request": request, "user_authenticated": True, "user_id": user.id, "user": user})
    return admin_templates.TemplateResponse('home.html',{"request": request, "user_authenticated": False})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, user=Depends(get_current_user_from_cookie)):
    return admin_templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user_authenticated": True, "user_id": user.id, "user": user}
    )

@app.get("/forgot-password", response_class=HTMLResponse)
def forgot_password_page(request: Request):
    return admin_templates.TemplateResponse("forgot_password.html", {"request": request})

@app.get("/reset-password", response_class=HTMLResponse)
def reset_password_page(request: Request, token: str = ""):
    return admin_templates.TemplateResponse("reset_password.html", {"request": request, "token": token})

app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["chatbot"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tenant.router, prefix="/api/v1/tenant", tags=["tenant"])


cli = typer.Typer()

@cli.command()
def makemigrations(message: str = "auto migration"):
    """Create new migration based on the models (like Django's makemigrations)."""
    migrations_env = os.path.join("migrations", "env.py")
    alembic_ini = os.path.join("alembic.ini")
    if not os.path.exists(migrations_env):
        typer.echo("Alembic not initialized. Running 'alembic init migrations'...")
        subprocess.run(["alembic", "init", "migrations"], check=True)
        # Update alembic.ini to blank out sqlalchemy.url
        if os.path.exists(alembic_ini):
            with open(alembic_ini, "r", encoding="utf-8") as f:
                ini_content = f.read()
            import re
            ini_content = re.sub(r"sqlalchemy.url\s*=.*", "sqlalchemy.url =", ini_content)
            with open(alembic_ini, "w", encoding="utf-8") as f:
                f.write(ini_content)
            typer.echo("alembic.ini updated: sqlalchemy.url set to blank.")
    # Always overwrite env.py with a working version
    env_py_content = '''
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from core.config import engine, Base, SQLALCHEMY_DATABASE_URL
import models  # Ensure all models are imported
from alembic import context
config = context.config
target_metadata = Base.metadata
config.set_main_option('sqlalchemy.url', SQLALCHEMY_DATABASE_URL)
def run_migrations_online():
    connectable = engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()
if context.is_offline_mode():
    pass  # (implement offline mode if needed)
else:
    run_migrations_online()
'''
    with open(migrations_env, "w", encoding="utf-8") as f:
        f.write(env_py_content)
    typer.echo("env.py overwritten with custom DB config.")
    # 2. Test all models are registered
    expected_tables = {'users', 'chatbots', 'chats', 'business_profiles'}
    actual_tables = set(Base.metadata.tables.keys())
    missing = expected_tables - actual_tables
    if missing:
        typer.echo(f"Error: Missing tables in metadata: {missing}")
        raise typer.Exit(code=1)
    typer.echo("All models registered. Running Alembic revision...")
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)
    typer.echo("Migration created.")

@cli.command()
def migrate():
    """Apply migrations to the database (like Django's migrate)."""
    subprocess.run(["alembic", "upgrade", "head"], check=True)

if __name__ == "__main__":
    cli() 