"""
CX Data - Portal de Dashboards
============================================
Versão Premium UI 4.0: Interface SaaS profissional
Paleta: #7371ff (primária), #bef533 (destaque), #1e1e1e (escuro), #dbbfff (secundária)
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
    """Tela de Login - Interface Premium"""
    state = app.storage.user.get('state', AppState())
    
    if state.user_email:
        ui.navigate.to('/')
        return

    # Background gradient premium
    with ui.column().classes('w-full h-screen items-center justify-center').style('background: linear-gradient(135deg, #7371ff 0%, #dbbfff 100%);'):
        with ui.card().classes('w-full max-w-md shadow-2xl').style('border-radius: 24px; border: none;'):
            with ui.column().classes('p-10 gap-6'):
                # Logo e título
                with ui.column().classes('items-center gap-3 mb-2'):
                    ui.label('📊').classes('text-6xl')
                    ui.label('CX Data').classes('text-4xl font-bold').style('color: #7371ff; letter-spacing: -0.5px;')
                    ui.label('Acesse seu portal de analytics').classes('text-base text-gray-500 font-light')
                
                # Campos de entrada
                with ui.column().classes('gap-4 w-full mt-4'):
                    email = ui.input('Email').classes('w-full').props('outlined dense').style(
                        'border-radius: 12px;'
                    )
                    senha = ui.input('Senha', password=True).classes('w-full').props('outlined dense').style(
                        'border-radius: 12px;'
                    )
                    
                    erro = ui.label('').classes('text-red-600 text-sm font-medium hidden w-full text-center')

                    def try_login():
                        user = autenticar_usuario(email.value.strip(), senha.value)
                        if user:
                            state.login(user) 
                            app.storage.user['state'] = state
                            ui.navigate.to('/')
                        else:
                            erro.text = '❌ Email ou senha incorretos'
                            erro.classes(remove='hidden')
                    
                    # Botão premium
                    ui.button('Entrar', on_click=try_login).classes('w-full text-white font-semibold text-base').style(
                        'background: #7371ff; border-radius: 12px; padding: 14px; border: none; box-shadow: 0 4px 12px rgba(115, 113, 255, 0.3); transition: all 0.3s;'
                    ).props('no-caps')
                    
                    senha.on('keydown.enter', try_login)

@ui.page('/')
def page_home():
    """Tela Principal - Interface Premium"""
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

    # Header premium
    with ui.header().classes('shadow-lg').style('background: #7371ff; border-bottom: 2px solid #bef533;'):
        with ui.row().classes('w-full items-center justify-between px-8 py-4'):
            with ui.row().classes('items-center gap-3'):
                ui.label('📊').classes('text-3xl')
                ui.label('CX Data').classes('text-2xl font-bold text-white').style('letter-spacing: -0.5px;')
            
            with ui.row().classes('items-center gap-6'):
                with ui.column().classes('items-end gap-0'):
                    ui.label(user.email).classes('text-sm text-white font-medium')
                    ui.label(f'{cliente.nome}').classes('text-xs').style('color: #bef533;')
                
                def logout_action():
                    state.logout()
                    app.storage.user['state'] = state
                    ui.navigate.to('/login')
                
                ui.button(icon='logout', on_click=logout_action).props('flat round').classes('text-white').style(
                    'background: rgba(255, 255, 255, 0.1); transition: all 0.3s;'
                )

    # Container principal
    with ui.column().classes('w-full p-8 min-h-screen').style('background: #f8f9fa;'):
        # Cabeçalho da seção
        with ui.column().classes('mb-8 gap-2'):
            ui.label('Meus Dashboards').classes('text-4xl font-bold').style('color: #1e1e1e; letter-spacing: -1px;')
            ui.label(f'Explore os analytics disponíveis para {cliente.nome}').classes('text-lg text-gray-500 font-light')

        if dashboards:
            # Grid de cards premium
            with ui.grid(columns='repeat(auto-fill, minmax(320px, 1fr))').classes('gap-6 w-full'):
                for dash in dashboards:
                    # Mapeamento de cores por tipo
                    tipo_colors = {
                        'financeiro': {'bg': '#10b981', 'light': '#d1fae5', 'icon': 'account_balance'},
                        'rh': {'bg': '#7371ff', 'light': '#dbbfff', 'icon': 'groups'},
                        'comercial': {'bg': '#f59e0b', 'light': '#fef3c7', 'icon': 'trending_up'},
                        'operacional': {'bg': '#8b5cf6', 'light': '#ede9fe', 'icon': 'settings'}
                    }
                    
                    config = tipo_colors.get(dash.tipo.lower(), {'bg': '#6b7280', 'light': '#f3f4f6', 'icon': 'dashboard'})
                    
                    # Card premium com hover
                    with ui.card().classes('cursor-pointer overflow-hidden').style(
                        f'border-radius: 20px; border: 2px solid {config["light"]}; transition: all 0.3s; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'
                    ).on('click', lambda d=dash: ui.navigate.to(f'/dashboard/{d.id}')):
                        
                        # Header do card com ícone
                        with ui.card_section().classes('p-8 flex items-center justify-center').style(
                            f'background: linear-gradient(135deg, {config["bg"]} 0%, {config["light"]} 100%);'
                        ):
                            ui.icon(config['icon'], size='3.5rem').classes('text-white').style('filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));')
                        
                        # Conteúdo do card
                        with ui.card_section().classes('p-6'):
                            ui.label(dash.nome).classes('text-xl font-bold mb-3').style('color: #1e1e1e;')
                            
                            with ui.row().classes('items-center gap-2'):
                                ui.label(dash.tipo.upper()).classes('text-xs font-bold px-3 py-1').style(
                                    f'background: {config["light"]}; color: {config["bg"]}; border-radius: 8px; letter-spacing: 0.5px;'
                                )
        else:
            # Estado vazio premium
            with ui.column().classes('w-full items-center justify-center py-20 gap-4'):
                ui.icon('analytics', size='5rem').classes('text-gray-300')
                ui.label('Nenhum dashboard disponível').classes('text-2xl font-bold text-gray-400')
                ui.label('Novos dashboards serão exibidos aqui assim que forem configurados').classes('text-base text-gray-400 text-center max-w-md')

@ui.page('/dashboard/{dash_id}')
def page_dashboard(dash_id: int):
    """Tela de Dashboard - Interface Premium"""
    state = app.storage.user.get('state', AppState())
    if not state or not state.user_email:
        ui.navigate.to('/login'); return

    db = SessionLocal()
    dash = db.query(Dashboard).filter(Dashboard.id == dash_id).first()
    db.close()

    if not dash:
        ui.label('Dashboard não encontrado'); return

    with ui.column().classes('w-full h-screen p-0 m-0'):
        # Barra superior premium
        with ui.row().classes('w-full items-center px-6 py-3 shadow-md').style(
            'background: linear-gradient(90deg, #7371ff 0%, #9b99ff 100%); border-bottom: 2px solid #bef533;'
        ):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat round').classes('text-white').style(
                'background: rgba(255, 255, 255, 0.15); transition: all 0.3s;'
            )
            
            with ui.row().classes('items-center gap-3 ml-2'):
                ui.icon('analytics', size='1.5rem').classes('text-white')
                ui.label(dash.nome).classes('text-xl font-bold text-white').style('letter-spacing: -0.3px;')
        
        # Iframe do dashboard (mantido exatamente como está)
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
