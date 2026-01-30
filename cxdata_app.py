"""
CX Data - Portal de Dashboards
============================================
Versão Professional UI 5.0: Interface SaaS Premium B2B
Inspiração: Linear, Vercel, Stripe Dashboard
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
    """Tela de Login - Design Corporativo Minimalista"""
    state = app.storage.user.get('state', AppState())
    
    if state.user_email:
        ui.navigate.to('/')
        return

    # Background clean corporativo
    with ui.column().classes('w-full h-screen items-center justify-center').style('background: #fafafa;'):
        
        with ui.column().classes('w-full max-w-md px-6 gap-12'):
            
            # Logo e identidade - minimalista
            with ui.column().classes('items-center gap-3'):
                ui.label('CX Data').classes('text-3xl font-semibold').style('color: #1e1e1e; letter-spacing: -0.02em;')
                ui.label('Analytics Platform').classes('text-sm font-normal').style('color: #737373;')
            
            # Container de login - sem card visível
            with ui.column().classes('gap-6 w-full'):
                
                # Campos minimalistas
                email = ui.input('Email').classes('w-full').props('outlined borderless').style('''
                    background: white;
                    border: 1px solid #e5e5e5;
                    border-radius: 8px;
                    font-size: 15px;
                ''')
                
                senha = ui.input('Senha', password=True).classes('w-full').props('outlined borderless').style('''
                    background: white;
                    border: 1px solid #e5e5e5;
                    border-radius: 8px;
                    font-size: 15px;
                ''')
                
                erro = ui.label('').classes('text-sm font-medium hidden').style('color: #ef4444;')

                def try_login():
                    user = autenticar_usuario(email.value.strip(), senha.value)
                    if user:
                        state.login(user) 
                        app.storage.user['state'] = state
                        ui.navigate.to('/')
                    else:
                        erro.text = 'Credenciais inválidas'
                        erro.classes(remove='hidden')
                
                # Botão clean
                ui.button('Acessar', on_click=try_login).classes('w-full font-medium').style('''
                    background: #7371ff;
                    color: white;
                    border-radius: 8px;
                    padding: 12px;
                    border: none;
                    font-size: 15px;
                    cursor: pointer;
                    transition: all 0.2s;
                ''').props('no-caps flat')
                
                senha.on('keydown.enter', try_login)

@ui.page('/')
def page_home():
    """Tela Principal - Interface Corporativa Premium"""
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

    # Layout com sidebar visual (não funcional, apenas estética)
    with ui.row().classes('w-full h-screen').style('background: #fafafa; margin: 0; padding: 0;'):
        
        # Sidebar visual minimalista
        with ui.column().classes('h-screen').style('''
            width: 240px;
            background: white;
            border-right: 1px solid #e5e5e5;
            padding: 24px 16px;
        '''):
            # Logo
            with ui.column().classes('gap-1 mb-8'):
                ui.label('CX Data').classes('text-lg font-semibold').style('color: #1e1e1e;')
                ui.label('Analytics').classes('text-xs').style('color: #a3a3a3;')
            
            # Menu item ativo
            with ui.row().classes('items-center gap-3 px-3 py-2').style('''
                background: #f5f5f5;
                border-radius: 6px;
            '''):
                ui.icon('analytics', size='20px').style('color: #7371ff;')
                ui.label('Dashboards').classes('text-sm font-medium').style('color: #1e1e1e;')
        
        # Conteúdo principal
        with ui.column().classes('flex-1 h-screen overflow-auto').style('padding: 0;'):
            
            # Header interno clean
            with ui.row().classes('w-full items-center justify-between').style('''
                padding: 20px 40px;
                background: white;
                border-bottom: 1px solid #e5e5e5;
            '''):
                with ui.column().classes('gap-1'):
                    ui.label(f'{cliente.nome}').classes('text-sm font-medium').style('color: #525252;')
                    ui.label(user.email).classes('text-xs').style('color: #a3a3a3;')
                
                def logout_action():
                    state.logout()
                    app.storage.user['state'] = state
                    ui.navigate.to('/login')
                
                ui.button('Sair', on_click=logout_action).classes('text-sm').style('''
                    background: transparent;
                    color: #737373;
                    border: 1px solid #e5e5e5;
                    border-radius: 6px;
                    padding: 6px 16px;
                    font-weight: 500;
                ''').props('no-caps flat')
            
            # Área de conteúdo
            with ui.column().classes('w-full').style('padding: 40px; max-width: 1400px;'):
                
                # Título da seção
                with ui.column().classes('gap-2 mb-8'):
                    ui.label('Seus dashboards').classes('text-2xl font-semibold').style('color: #1e1e1e; letter-spacing: -0.02em;')
                    ui.label('Acesse as análises disponíveis para sua conta').classes('text-sm').style('color: #737373;')
                
                if dashboards:
                    # Grid de cards profissionais
                    with ui.grid(columns='repeat(auto-fill, minmax(340px, 1fr))').classes('w-full').style('gap: 20px;'):
                        for dash in dashboards:
                            
                            # Configuração de cores por tipo
                            tipo_config = {
                                'financeiro': {'color': '#10b981', 'bg': '#ecfdf5', 'icon': 'account_balance_wallet'},
                                'rh': {'color': '#7371ff', 'bg': '#f5f3ff', 'icon': 'people'},
                                'comercial': {'color': '#f59e0b', 'bg': '#fffbeb', 'icon': 'storefront'},
                                'operacional': {'color': '#8b5cf6', 'bg': '#faf5ff', 'icon': 'settings'}
                            }
                            
                            config = tipo_config.get(dash.tipo.lower(), {'color': '#6b7280', 'bg': '#f9fafb', 'icon': 'dashboard'})
                            
                            # Card profissional
                            with ui.column().classes('cursor-pointer').style(f'''
                                background: white;
                                border: 1px solid #e5e5e5;
                                border-radius: 12px;
                                padding: 0;
                                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                                overflow: hidden;
                            ''').on('click', lambda d=dash: ui.navigate.to(f'/dashboard/{d.id}')):
                                
                                # Header do card
                                with ui.row().classes('items-center justify-between w-full').style(f'''
                                    padding: 20px 24px;
                                    background: {config["bg"]};
                                    border-bottom: 1px solid #e5e5e5;
                                '''):
                                    ui.icon(config['icon'], size='24px').style(f'color: {config["color"]};')
                                    
                                    ui.label(dash.tipo.upper()).classes('text-xs font-semibold').style(f'''
                                        color: {config["color"]};
                                        letter-spacing: 0.05em;
                                    ''')
                                
                                # Conteúdo
                                with ui.column().classes('gap-2').style('padding: 24px;'):
                                    ui.label(dash.nome).classes('text-base font-semibold').style('color: #1e1e1e; line-height: 1.4;')
                                    
                                    with ui.row().classes('items-center gap-2 mt-2'):
                                        ui.label('Abrir dashboard').classes('text-sm').style('color: #7371ff;')
                                        ui.icon('arrow_forward', size='16px').style('color: #7371ff;')
                
                else:
                    # Estado vazio profissional
                    with ui.column().classes('items-center justify-center w-full').style('padding: 80px 0;'):
                        with ui.column().classes('items-center gap-4 max-w-sm text-center'):
                            ui.icon('analytics', size='48px').style('color: #d4d4d4;')
                            ui.label('Nenhum dashboard disponível').classes('text-lg font-semibold').style('color: #525252;')
                            ui.label('Quando dashboards forem atribuídos à sua conta, eles aparecerão aqui.').classes('text-sm').style('color: #a3a3a3; line-height: 1.6;')

@ui.page('/dashboard/{dash_id}')
def page_dashboard(dash_id: int):
    """Tela de Visualização - Embed Profissional Imersivo"""
    state = app.storage.user.get('state', AppState())
    if not state or not state.user_email:
        ui.navigate.to('/login'); return

    db = SessionLocal()
    dash = db.query(Dashboard).filter(Dashboard.id == dash_id).first()
    db.close()

    if not dash:
        ui.label('Dashboard não encontrado'); return

    # Container fullscreen profissional
    with ui.column().classes('w-full h-screen').style('background: #fafafa; margin: 0; padding: 0;'):
        
        # Header minimalista e discreto
        with ui.row().classes('w-full items-center justify-between').style('''
            padding: 12px 24px;
            background: white;
            border-bottom: 1px solid #e5e5e5;
            height: 56px;
        '''):
            # Lado esquerdo
            with ui.row().classes('items-center gap-3'):
                ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).style('''
                    background: transparent;
                    color: #525252;
                    border: none;
                    min-width: 36px;
                    padding: 6px;
                ''').props('flat round dense')
                
                with ui.row().classes('items-center gap-2'):
                    ui.icon('analytics', size='20px').style('color: #7371ff;')
                    ui.label(dash.nome).classes('text-sm font-semibold').style('color: #1e1e1e;')
            
            # Lado direito - badge discreta
            ui.label(dash.tipo.upper()).classes('text-xs font-semibold').style('''
                color: #737373;
                background: #f5f5f5;
                padding: 4px 12px;
                border-radius: 6px;
                letter-spacing: 0.05em;
            ''')
        
        # Container do iframe profissional
        with ui.column().classes('w-full flex-1').style('''
            padding: 16px;
            background: #fafafa;
            position: relative;
        '''):
            
            # Wrapper com sombra suave e bordas
            with ui.column().classes('w-full h-full').style('''
                background: white;
                border-radius: 12px;
                border: 1px solid #e5e5e5;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            '''):
                
                # Loading state inicial
                loading_container = ui.column().classes('w-full h-full items-center justify-center').style('''
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: white;
                    z-index: 10;
                ''')
                
                with loading_container:
                    ui.spinner(size='lg').style('color: #7371ff;')
                    ui.label('Carregando dashboard...').classes('text-sm mt-4').style('color: #a3a3a3;')
                
                # Iframe embutido profissionalmente
                iframe_html = f'''
                <iframe 
                    src="{dash.link_embed}" 
                    style="
                        width: 100%;
                        height: 100%;
                        border: none;
                        display: block;
                        background: white;
                    "
                    onload="document.getElementById('loading-{dash_id}').style.display='none'"
                    allowfullscreen
                ></iframe>
                '''
                
                ui.html(iframe_html, sanitize=False)
                
                # Esconder loading após carregar (via CSS puro)
                loading_container.style(add=f'id: loading-{dash_id}')

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
