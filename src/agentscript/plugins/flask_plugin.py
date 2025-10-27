"""
Flask Plugin for AgentScript

Generates Flask web applications with:
- Flask blueprints and application factory pattern
- SQLAlchemy models with Flask-Migrate
- RESTful API endpoints with Flask-RESTful or blueprints
- Flask-CORS support for API access
- Authentication with Flask-Login
- Flask-Admin for admin interface
- Configuration management
- Database migrations
- CLI commands
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import os

from .base import BasePlugin, PluginConfig, GenerationContext
from ..ast_nodes import Program, IntentDeclaration, PipelineStage


class FlaskPlugin(BasePlugin):
    """Flask web application generator"""
    
    plugin_name = "flask"
    plugin_description = "Generate Flask web applications with SQLAlchemy, blueprints, and REST APIs"
    plugin_version = "1.0.0"
    plugin_dependencies = ["Flask>=2.3.0", "Flask-SQLAlchemy>=3.0.0", "Flask-Migrate>=4.0.0"]
    plugin_optional_dependencies = ["Flask-Login", "Flask-Admin", "Flask-CORS", "Flask-Bcrypt"]
    plugin_output_extension = ".py"
    plugin_supports_async = False
    plugin_supports_web = True
    plugin_supports_database = True
    plugin_supports_auth = True
    
    @property
    def name(self) -> str:
        return "flask"
    
    @property
    def description(self) -> str:
        return "Generate Flask web applications with SQLAlchemy, blueprints, and REST APIs"
    
    def generate_code(self, ast: Program, context: GenerationContext) -> Dict[str, str]:
        """Generate Flask application code from AgentScript AST"""
        files = {}
        
        app_name = context.options.get("app_name", "myapp")
        use_auth = context.options.get("auth", False)
        use_admin = context.options.get("admin", False)
        database = context.options.get("database_type", "sqlite")
        use_api = context.options.get("with_api", True)
        
        # Generate application structure
        files[f"{app_name}/__init__.py"] = self._generate_app_factory(app_name, use_auth, use_admin, use_api)
        files[f"{app_name}/config.py"] = self._generate_config(database)
        files[f"{app_name}/extensions.py"] = self._generate_extensions(use_auth, use_admin)
        files[f"{app_name}/models.py"] = self._generate_models(ast, use_auth)
        
        # Generate blueprints
        if use_api:
            files[f"{app_name}/api/__init__.py"] = self._generate_api_blueprint(ast)
            files[f"{app_name}/api/routes.py"] = self._generate_api_routes(ast)
            files[f"{app_name}/api/schemas.py"] = self._generate_schemas(ast)
        
        files[f"{app_name}/blueprints/__init__.py"] = ""
        files[f"{app_name}/blueprints/main.py"] = self._generate_main_blueprint(ast)
        
        if use_auth:
            files[f"{app_name}/blueprints/auth.py"] = self._generate_auth_blueprint()
        
        # Generate admin interface
        if use_admin:
            files[f"{app_name}/admin.py"] = self._generate_admin(ast)
        
        # Generate CLI commands
        files[f"{app_name}/cli.py"] = self._generate_cli_commands(ast)
        
        # Generate utilities
        files[f"{app_name}/utils/__init__.py"] = ""
        files[f"{app_name}/utils/pipeline_executor.py"] = self._generate_pipeline_executor(ast)
        
        # Configuration files
        files["requirements.txt"] = self._generate_requirements(use_auth, use_admin, database)
        files[".env.example"] = self._generate_env_example(database)
        files[".flaskenv"] = self._generate_flaskenv(app_name)
        files["wsgi.py"] = self._generate_wsgi(app_name)
        files["run.py"] = self._generate_run_script(app_name)
        files["README.md"] = self._generate_readme(app_name, use_auth, use_admin, database)
        
        # Docker support
        files["Dockerfile"] = self._generate_dockerfile(app_name)
        files["docker-compose.yml"] = self._generate_docker_compose(app_name, database)
        
        # Migrations
        files["migrations/.gitkeep"] = ""
        
        return files
    
    def _generate_app_factory(self, app_name: str, use_auth: bool, use_admin: bool, use_api: bool) -> str:
        imports = ["from flask import Flask", "from .config import Config", "from .extensions import db"]
        
        if use_auth:
            imports.append("from .extensions import login_manager, bcrypt")
        if use_admin:
            imports.append("from .admin import init_admin")
        
        if use_api:
            imports.append("from flask_cors import CORS")
        
        imports_str = "\n".join(imports)
        
        cors_init = "CORS(app)" if use_api else ""
        
        auth_init = ''''''
        if use_auth:
            auth_init = '''# Initialize Flask-Login
    login_manager.init_app(app)
    bcrypt.init_app(app)
    
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))'''
        
        admin_init = "# Initialize admin interface\n    init_admin(app)" if use_admin else ""
        
        auth_bp_reg = ''''''
        if use_auth:
            auth_bp_reg = '''from .blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')'''
        
        api_bp_reg = ''''''
        if use_api:
            api_bp_reg = '''from .api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')'''
        
        return f'''"""
Flask Application Factory
"""

{imports_str}


def create_app(config_class=Config):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    {cors_init}
    
    {auth_init}
    
    {admin_init}
    
    # Register blueprints
    from .blueprints.main import main_bp
    app.register_blueprint(main_bp)
    
    {auth_bp_reg}
    
    {api_bp_reg}
    
    # Register CLI commands
    from . import cli
    cli.init_app(app)
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
'''
    
    def _generate_config(self, database: str) -> str:
        db_uri_map = {
            "sqlite": "sqlite:///app.db",
            "postgresql": "postgresql://user:password@localhost/dbname",
            "mysql": "mysql://user:password@localhost/dbname"
        }
        
        return f'''"""
Application Configuration
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or '{db_uri_map.get(database, db_uri_map["sqlite"])}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # API
    JSON_SORT_KEYS = False
    
    # Pagination
    ITEMS_PER_PAGE = 20


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config = {{
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}}
'''
    
    def _generate_extensions(self, use_auth: bool, use_admin: bool) -> str:
        code = '''"""
Flask Extensions
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
'''
        
        if use_auth:
            code += '''
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
bcrypt = Bcrypt()
'''
        
        return code
    
    def _generate_models(self, program: Program, use_auth: bool) -> str:
        models = []
        
        if use_auth:
            models.append('''
class User(db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        from .extensions import bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        from .extensions import bcrypt
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_authenticated(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)
    
    def __repr__(self):
        return f'<User {{self.username}}>'
''')
        
        # Generate models from pipelines
        for pipeline in program.statements:
            if isinstance(pipeline, IntentDeclaration):
                model_name = pipeline.name.capitalize()
                models.append(f'''
class {model_name}Data(db.Model):
    """Generated from AgentScript pipeline: {pipeline.name}"""
    __tablename__ = '{pipeline.name.lower()}_data'
    
    id = db.Column(db.Integer, primary_key=True)
    pipeline_name = db.Column(db.String(100), default='{pipeline.name}')
    input_data = db.Column(db.Text)
    output_data = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    def __repr__(self):
        return f'<{model_name}Data {{self.id}} - {{self.status}}>'
''')
        
        return f'''"""
Database Models
"""

from datetime import datetime
from .extensions import db

{chr(10).join(models)}
'''
    
    def _generate_api_blueprint(self, program: Program) -> str:
        return '''"""
API Blueprint initialization
"""

from flask import Blueprint

api_bp = Blueprint('api', __name__)
'''
    
    def _generate_api_routes(self, program: Program) -> str:
        routes = []
        
        for pipeline in program.statements:
            if isinstance(pipeline, IntentDeclaration):
                pipeline_name = pipeline.name
                model_name = pipeline_name.capitalize()
                
                routes.append(f'''
@api_bp.route('/{pipeline_name}', methods=['GET'])
def get_{pipeline_name}_list():
    """Get all {pipeline_name} records"""
    records = {model_name}Data.query.order_by({model_name}Data.created_at.desc()).all()
    return jsonify([{{
        'id': r.id,
        'status': r.status,
        'created_at': r.created_at.isoformat(),
        'completed_at': r.completed_at.isoformat() if r.completed_at else None
    }} for r in records])


@api_bp.route('/{pipeline_name}/<int:id>', methods=['GET'])
def get_{pipeline_name}_detail(id):
    """Get specific {pipeline_name} record"""
    record = {model_name}Data.query.get_or_404(id)
    return jsonify({{
        'id': record.id,
        'pipeline_name': record.pipeline_name,
        'input_data': record.input_data,
        'output_data': record.output_data,
        'status': record.status,
        'created_at': record.created_at.isoformat(),
        'completed_at': record.completed_at.isoformat() if record.completed_at else None,
        'error_message': record.error_message
    }})


@api_bp.route('/{pipeline_name}', methods=['POST'])
def create_{pipeline_name}():
    """Execute {pipeline_name} pipeline"""
    data = request.get_json()
    
    record = {model_name}Data(input_data=str(data))
    db.session.add(record)
    db.session.commit()
    
    try:
        # Execute pipeline
        executor = PipelineExecutor()
        result = executor.execute_{pipeline_name}(data)
        
        record.output_data = str(result)
        record.status = 'completed'
        record.completed_at = datetime.utcnow()
    except Exception as e:
        record.status = 'failed'
        record.error_message = str(e)
    
    db.session.commit()
    
    return jsonify({{'id': record.id, 'status': record.status}}), 201
''')
        
        return f'''"""
API Routes for AgentScript Pipelines
"""

from flask import jsonify, request
from datetime import datetime
from . import api_bp
from ..extensions import db
from ..models import {", ".join([p.name.capitalize() + "Data" for p in program.statements if isinstance(p, Pipeline)])}
from ..utils.pipeline_executor import PipelineExecutor

{chr(10).join(routes)}
'''
    
    def _generate_schemas(self, program: Program) -> str:
        return '''"""
API Schemas for validation
"""

from marshmallow import Schema, fields, validate


class PipelineExecutionSchema(Schema):
    """Schema for pipeline execution request"""
    input_data = fields.Dict(required=True)
    options = fields.Dict(missing={})
'''
    
    def _generate_main_blueprint(self, program: Program) -> str:
        routes = []
        
        for pipeline in program.statements:
            if isinstance(pipeline, IntentDeclaration):
                pipeline_name = pipeline.name
                routes.append(f'''
@main_bp.route('/{pipeline_name}')
def {pipeline_name}_view():
    """View for {pipeline_name} pipeline"""
    return render_template('{pipeline_name}.html', pipeline_name='{pipeline_name}')
''')
        
        return f'''"""
Main Blueprint for web views
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from ..extensions import db
from ..models import *

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page"""
    pipelines = [
        {', '.join([f'"{p.name}"' for p in program.statements if isinstance(p, Pipeline)])}
    ]
    return render_template('index.html', pipelines=pipelines)

{chr(10).join(routes)}
'''
    
    def _generate_auth_blueprint(self) -> str:
        return '''"""
Authentication Blueprint
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from ..extensions import db
from ..models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')
'''
    
    def _generate_admin(self, program: Program) -> str:
        model_views = []
        
        for pipeline in program.statements:
            if isinstance(pipeline, IntentDeclaration):
                model_name = pipeline.name.capitalize() + "Data"
                model_views.append(f"    admin.add_view(ModelView({model_name}, db.session))")
        
        return f'''"""
Flask-Admin Configuration
"""

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from .extensions import db
from .models import User, {", ".join([p.name.capitalize() + "Data" for p in program.statements if isinstance(p, Pipeline)])}


def init_admin(app):
    """Initialize Flask-Admin"""
    admin = Admin(app, name='AgentScript Admin', template_mode='bootstrap4')
    
    # Add model views
    admin.add_view(ModelView(User, db.session))
{chr(10).join(model_views)}
    
    return admin
'''
    
    def _generate_cli_commands(self, program: Program) -> str:
        commands = []
        
        for pipeline in program.statements:
            if isinstance(pipeline, IntentDeclaration):
                pipeline_name = pipeline.name
                commands.append(f'''
@click.command()
@click.argument('input_data')
@with_appcontext
def run_{pipeline_name}(input_data):
    """Run {pipeline_name} pipeline from CLI"""
    executor = PipelineExecutor()
    result = executor.execute_{pipeline_name}(input_data)
    click.echo(f"Result: {{result}}")
''')
        
        return f'''"""
Flask CLI Commands
"""

import click
from flask.cli import with_appcontext
from .extensions import db
from .models import User
from .utils.pipeline_executor import PipelineExecutor


def init_app(app):
    """Register CLI commands"""
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
{chr(10).join([f'    app.cli.add_command(run_{p.name})' for p in program.statements if isinstance(p, Pipeline)])}


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Initialize the database"""
    db.create_all()
    click.echo('Initialized the database.')


@click.command('create-admin')
@click.option('--username', prompt=True)
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@with_appcontext
def create_admin_command(username, email, password):
    """Create an admin user"""
    user = User(username=username, email=email, is_admin=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    click.echo(f'Created admin user: {{username}}')

{chr(10).join(commands)}
'''
    
    def _generate_pipeline_executor(self, program: Program) -> str:
        methods = []
        
        for pipeline in program.statements:
            if isinstance(pipeline, IntentDeclaration):
                pipeline_name = pipeline.name
                steps_code = []
                
                for step in pipeline.pipeline.stages if pipeline.pipeline else []:
                    if isinstance(step, PipelineStage):
                        steps_code.append(f"        # Step: {step.action}")
                        steps_code.append(f"        # Action: {step.action}, Target: {step.target}")
                
                methods.append(f'''
    def execute_{pipeline_name}(self, data):
        """Execute {pipeline_name} pipeline"""
        result = data
        
{chr(10).join(steps_code) if steps_code else "        # Pipeline logic here"}
        
        return result
''')
        
        return f'''"""
Pipeline Executor for AgentScript Pipelines
"""


class PipelineExecutor:
    """Executes AgentScript pipelines"""
    
    def __init__(self):
        self.results = {{}}
{chr(10).join(methods)}
'''
    
    def _generate_requirements(self, use_auth: bool, use_admin: bool, database: str) -> str:
        reqs = [
            "Flask>=2.3.0",
            "Flask-SQLAlchemy>=3.0.0",
            "Flask-Migrate>=4.0.0",
            "Flask-CORS>=4.0.0",
            "python-dotenv>=1.0.0",
            "gunicorn>=21.0.0"
        ]
        
        if use_auth:
            reqs.extend(["Flask-Login>=0.6.0", "Flask-Bcrypt>=1.0.0"])
        
        if use_admin:
            reqs.append("Flask-Admin>=1.6.0")
        
        if database == "postgresql":
            reqs.append("psycopg2-binary>=2.9.0")
        elif database == "mysql":
            reqs.append("pymysql>=1.1.0")
        
        reqs.append("marshmallow>=3.20.0")
        
        return "\n".join(sorted(reqs))
    
    def _generate_env_example(self, database: str) -> str:
        return f'''FLASK_APP=wsgi.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL={self._get_database_url_example(database)}
'''
    
    def _get_database_url_example(self, database: str) -> str:
        urls = {
            "sqlite": "sqlite:///app.db",
            "postgresql": "postgresql://user:password@localhost:5432/dbname",
            "mysql": "mysql://user:password@localhost:3306/dbname"
        }
        return urls.get(database, urls["sqlite"])
    
    def _generate_flaskenv(self, app_name: str) -> str:
        return f'''FLASK_APP={app_name}
FLASK_ENV=development
'''
    
    def _generate_wsgi(self, app_name: str) -> str:
        return f'''"""
WSGI Entry Point
"""

from {app_name} import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
'''
    
    def _generate_run_script(self, app_name: str) -> str:
        return f'''#!/usr/bin/env python3
"""
Development Server Runner
"""

from {app_name} import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
    
    def _generate_readme(self, app_name: str, use_auth: bool, use_admin: bool, database: str) -> str:
        auth_feature = "- Authentication with Flask-Login" if use_auth else ""
        admin_feature = "- Admin interface with Flask-Admin" if use_admin else ""
        
        admin_user_step = '''4. Create admin user:
```bash
flask create-admin
```

''' if use_auth else ""
        
        auth_section = '''## Authentication

- `/auth/login` - User login
- `/auth/logout` - User logout
- `/auth/register` - User registration

''' if use_auth else ""
        
        admin_section = '''## Admin Interface

Access at `/admin` after logging in with admin credentials.

''' if use_admin else ""
        
        admin_cli_cmd = "- `flask create-admin` - Create admin user" if use_auth else ""
        
        return f'''# {app_name.capitalize()} - Flask Application

Generated by AgentScript Flask Plugin

## Features

- Flask web application with application factory pattern
- SQLAlchemy ORM with Flask-Migrate for database migrations
- RESTful API with CORS support
{auth_feature}
{admin_feature}
- Database: {database.capitalize()}
- Docker support

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Initialize database:
```bash
flask init-db
```

{admin_user_step}
## Running

Development server:
```bash
python run.py
```

Or with Flask CLI:
```bash
flask run
```

Production with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

## Docker

Build and run:
```bash
docker-compose up --build
```

## API Endpoints

- `GET /api/<pipeline>` - List all records
- `GET /api/<pipeline>/<id>` - Get specific record
- `POST /api/<pipeline>` - Execute pipeline

{auth_section}{admin_section}## Database Migrations

Create migration:
```bash
flask db migrate -m "description"
```

Apply migration:
```bash
flask db upgrade
```

## CLI Commands

- `flask init-db` - Initialize database
{admin_cli_cmd}
- `flask run-<pipeline>` - Run specific pipeline

## Project Structure

```
{app_name}/
├── __init__.py          # Application factory
├── config.py            # Configuration
├── extensions.py        # Flask extensions
├── models.py            # Database models
├── api/                 # API blueprints
├── blueprints/          # Web blueprints
├── utils/               # Utilities
└── cli.py               # CLI commands
```
'''
    
    def _generate_dockerfile(self, app_name: str) -> str:
        return f'''FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
'''
    
    def _generate_docker_compose(self, app_name: str, database: str) -> str:
        if database == "postgresql":
            db_service = '''
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
'''
        elif database == "mysql":
            db_service = '''
  db:
    image: mysql:8
    environment:
      MYSQL_USER: user
      MYSQL_PASSWORD: password
      MYSQL_DATABASE: dbname
      MYSQL_ROOT_PASSWORD: rootpassword
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  mysql_data:
'''
        else:
            db_service = ""
        
        return f'''version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL={'postgresql://user:password@db:5432/dbname' if database == 'postgresql' else 'mysql://user:password@db:3306/dbname' if database == 'mysql' else 'sqlite:///app.db'}
    volumes:
      - .:/app
    depends_on:
      - db
{db_service}
'''
    
    def get_dependencies(self, context: GenerationContext) -> List[str]:
        """Get required dependencies for Flask project"""
        deps = self.plugin_dependencies.copy()
        
        # Add auth dependencies
        if context.options.get('auth', False):
            deps.extend(["Flask-Login>=0.6.0", "Flask-Bcrypt>=1.0.0"])
        
        # Add admin dependencies
        if context.options.get('admin', False):
            deps.append("Flask-Admin>=1.6.0")
        
        # Add database dependencies
        database = context.options.get('database_type', 'sqlite')
        if database == 'postgresql':
            deps.append('psycopg2-binary>=2.9.0')
        elif database == 'mysql':
            deps.append('pymysql>=1.1.0')
        
        # Add CORS support
        deps.append("Flask-CORS>=4.0.0")
        deps.append("marshmallow>=3.20.0")
        deps.append("gunicorn>=21.0.0")
        deps.append("python-dotenv>=1.0.0")
        
        return deps
