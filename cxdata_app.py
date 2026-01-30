"""
CX Data - Portal de Dashboards
============================================
Versão Final 3.0: Correção do erro 'sanitize' no ui.html
"""

from nicegui import ui, app
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
import hashlib
from typing import Optional, List
import os

# ============================================================================
# 1. BANCO DE DADOS
# ============================================================================

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("AVISO: DATABASE_URL não encontrada.")
    DATABASE_URL = "sqlite:///exemplo.db" 

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ============================================================================
# 2. MODELOS
# ============================================================================

class Cliente(Base):
    __tablename__ = 'clientes'
    id = Column(Integer, primary_key=True)
    nome = Column(String(200), nullable=False)
    users = relationship('User', back_populates='cliente')
    dashboards = relationship('Dashboard', back_populates='cliente')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, nullable=False)
    password_hash = Column(String(64), nullable=False)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    perfil = Column(String(50), nullable=False)
    cliente = relationship('Cliente', back_populates='users')

class Dashboard(Base):
    __tablename__ = 'dashboards'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('clientes.id'), nullable=False)
    nome = Column(String(200), nullable=False)
    tipo = Column(String(50), nullable=False)
    link_embed = Column(Text, nullable=False)
    cliente = relationship('Cliente', back_populates='dashboards')
    permissoes = relationship('DashboardPermissao', back_populates='dashboard')

class DashboardPermissao(Base):
    __tablename__ = 'dashboard_permissoes'
    id = Column(Integer, primary_key=True)
    dashboard_id = Column(Integer, ForeignKey('dashboards.id'), nullable=False)
    perfil = Column(String(50), nullable=False)
    dashboard = relationship('Dashboard', back_populates='permissoes')

# ============================================================================
# 3. LÓGICA
# ============================================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def autenticar_usuario(email: str, password: str) -> Optional[User]:
    db = SessionLocal()
    try:
        password_hash = hash_password(password)
        return db.query(User).filter(User.email == email, User.password_hash == password_hash).first()
    finally:
        db.close()

def obter_dashboards_autorizados(cliente_id: int, perfil: str) -> List[Dashboard]:
    db = SessionLocal()
    try:
        return db.query(Dashboard).join(DashboardPermissao).filter(
            Dashboard.cliente_id == cliente_id,
            DashboardPermissao.perfil == perfil
        ).distinct().all()
    finally:
        db.close()

# ============================================================================
# 4. ESTADO DO USUÁRIO
# ============================================================================

class AppState:
    def __init__(self):
        self.user_email: Optional[str] = None
    
    def login(self, user: User):
        self.user_email = user.email
    
    def logout(self):
        self.user_email = None

    def get_user_completo(self) -> Optional[User]:
        if not self.user_email: return None
        db = SessionLocal()
        try:
            return db.query(User).filter(User.email == self.user_email).first()
        finally:
            db.close()

# ============================================================================
# 5. TELAS (FRONTEND)
# ============================================================================

@ui.page('/login')
def page_login():
    """Tela de Login"""
    state = app.storage.user.get('state', AppState())
    
    if state.user_email:
        ui.navigate.to('/')
        return

    with ui.column().classes('w-full h-screen items-center justify-center bg-gray-100'):
        with ui.card().classes('w-96 p-8 shadow-xl'):
            ui.label('CX Data').classes('text-3xl font-bold text-center mb-2 text-blue-600 w-full')
            ui.label('Acesso ao Portal').classes('text-center text-gray-500 mb-6 w-full')
            
            email = ui.input('Email').classes('w-full').props('outlined')
            senha = ui.input('Senha', password=True).classes('w-full').props('outlined')
            erro = ui.label('').classes('text-red-500 text-sm hidden w-full text-center mt-2')

            def try_login():
                user = autenticar_usuario(email.value.strip(), senha.value)
                if user:
                    state.login(user) 
                    app.storage.user['state'] = state
                    ui.navigate.to('/')
                else:
                    erro.text = 'Dados incorretos'
                    erro.classes(remove='hidden')
                    
            ui.button('Entrar', on_click=try_login).classes('w-full bg-blue-600 text-white mt-4')
            senha.on('keydown.enter', try_login)

@ui.page('/')
def page_home():
    """Tela Principal"""
    state = app.storage.user.get('state', AppState())
    
    if not state or not state.user_email:
        ui.navigate.to('/login'); return

    user = state.get_user_completo()
    if not user:
        state.logout(); ui.navigate.to('/login'); return

    db = SessionLocal()
    cliente = db.query(Cliente).filter(Cliente.id == user.cliente_id).first()
    dashboards = obter_dashboards_autorizados(user.cliente_id, user.perfil)
    db.close()

    # --- DESENHO DA TELA ---
    with ui.header().classes('bg-blue-600 text-white shadow-md'):
        with ui.row().classes('w-full items-center justify-between px-4 py-2'):
            ui.label('CX Data').classes('text-xl font-bold')
            with ui.row().classes('items-center gap-4'):
                ui.label(user.email).classes('text-sm opacity-90')
                def logout_action():
                    state.logout()
                    app.storage.user['state'] = state
                    ui.navigate.to('/login')
                ui.button(icon='logout', on_click=logout_action).props('flat round color=white')

    with ui.column().classes('w-full p-8 bg-gray-50 min-h-screen'):
        ui.label(f'Cliente: {cliente.nome}').classes('text-gray-500 font-medium')
        ui.label('Meus Dashboards').classes('text-3xl font-bold text-gray-800 mb-6')

        if dashboards:
            with ui.grid(columns='repeat(auto-fill, minmax(300px, 1fr))').classes('gap-6 w-full'):
                for dash in dashboards:
                    colors = {'financeiro': 'green', 'rh': 'blue', 'comercial': 'orange', 'operacional': 'purple'}
                    c = colors.get(dash.tipo.lower(), 'gray')
                    
                    with ui.card().classes('cursor-pointer hover:shadow-lg transition').on('click', lambda d=dash: ui.navigate.to(f'/dashboard/{d.id}')):
                        with ui.card_section().classes(f'bg-{c}-100 p-6 flex justify-center'):
                            ui.icon('analytics', size='3rem').classes(f'text-{c}-600')
                        with ui.card_section().classes('p-4'):
                            ui.label(dash.nome).classes('text-lg font-bold')
                            ui.badge(dash.tipo, color=c).classes('mt-2')
        else:
            with ui.column().classes('w-full items-center justify-center py-12'):
                ui.icon('folder_off', size='4rem').classes('text-gray-300 mb-4')
                ui.label('Nenhum dashboard encontrado.').classes('text-gray-400 text-lg')

@ui.page('/dashboard/{dash_id}')
def page_dashboard(dash_id: int):
    """Tela de Dashboard"""
    state = app.storage.user.get('state', AppState())
    if not state or not state.user_email:
        ui.navigate.to('/login'); return

    db = SessionLocal()
    dash = db.query(Dashboard).filter(Dashboard.id == dash_id).first()
    db.close()

    if not dash:
        ui.label('Dashboard não encontrado'); return

    with ui.column().classes('w-full h-screen p-0 m-0'):
        # Barra superior
        with ui.row().classes('w-full bg-blue-600 text-white p-2 items-center shadow-md'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat round color=white')
            ui.label(dash.nome).classes('font-bold ml-2')
        
        # --- AQUI ESTÁ A CORREÇÃO: sanitize=False ---
        ui.html(
            f'<iframe src="{dash.link_embed}" style="width:100%; height:calc(100vh - 60px); border:none;"></iframe>', 
            sanitize=False
        )

# ============================================================================
# 6. INICIALIZAÇÃO
# ============================================================================

Base.metadata.create_all(bind=engine)

if __name__ in {'__main__', '__mp_main__'}:
    port = int(os.environ.get('PORT', 8080))
    ui.run(
        title='CX Data Portal',
        favicon='📊',
        host='0.0.0.0',
        port=port,
        storage_secret='cx_key_9988',
        reload=False
    )
