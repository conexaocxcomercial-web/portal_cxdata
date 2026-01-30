"""
CX Data - Portal de Dashboards Multi-Tenant
============================================
Atualização: Correção do erro de Storage (RuntimeError) e Porta do Render
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
# CONFIGURAÇÃO DO BANCO DE DADOS
# ============================================================================

# Pegue a URL do arquivo .env ou variáveis de ambiente do Render
DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres:SUA_SENHA@db.seu_projeto.supabase.co:5432/postgres' 
)

# Correção para SQLAlchemy
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ============================================================================
# MODELOS DO BANCO DE DADOS
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
    perfil = Column(String(50), nullable=False)  # admin, gestor, analista, operacional
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
# LÓGICA DE NEGÓCIO E AUTENTICAÇÃO
# ============================================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def autenticar_usuario(email: str, password: str) -> Optional[User]:
    db = SessionLocal()
    try:
        password_hash = hash_password(password)
        user = db.query(User).filter(User.email == email, User.password_hash == password_hash).first()
        return user
    finally:
        db.close()

def criar_novo_usuario_db(email, senha, perfil, cliente_id):
    """Cria um novo usuário no banco de dados"""
    db = SessionLocal()
    try:
        novo_usuario = User(
            email=email,
            password_hash=hash_password(senha),
            perfil=perfil,
            cliente_id=cliente_id
        )
        db.add(novo_usuario)
        db.commit()
        return True, "Usuário criado com sucesso!"
    except IntegrityError:
        db.rollback()
        return False, "Erro: Este e-mail já está cadastrado."
    except Exception as e:
        db.rollback()
        return False, f"Erro ao criar usuário: {str(e)}"
    finally:
        db.close()

def obter_dashboards_autorizados(cliente_id: int, perfil: str) -> List[Dashboard]:
    db = SessionLocal()
    try:
        dashboards = db.query(Dashboard).join(
            DashboardPermissao, Dashboard.id == DashboardPermissao.dashboard_id
        ).filter(
            Dashboard.cliente_id == cliente_id,
            DashboardPermissao.perfil == perfil
        ).distinct().all()
        return dashboards
    finally:
        db.close()


# ============================================================================
# ESTADO E INTERFACE
# ============================================================================

class AppState:
    def __init__(self):
        self.user: Optional[User] = None
        self.cliente: Optional[Cliente] = None
        self.perfil: Optional[str] = None
        self.dashboards_autorizados: List[Dashboard] = []
    
    def fazer_login(self, user: User):
        self.user = user
        self.perfil = user.perfil
        db = SessionLocal()
        try:
            self.cliente = db.query(Cliente).filter(Cliente.id == user.cliente_id).first()
            self.dashboards_autorizados = obter_dashboards_autorizados(user.cliente_id, user.perfil)
        finally:
            db.close()
    
    def fazer_logout(self):
        self.user = None
        self.cliente = None
        self.perfil = None
        self.dashboards_autorizados = []
    
    def esta_autenticado(self) -> bool:
        return self.user is not None

# --- Componente: Modal de Criação de Usuário ---
def abrir_modal_criar_usuario(state: AppState):
    """Abre um diálogo para cadastro de usuário (Apenas Admin)"""
    
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label(f'Novo Usuário para {state.cliente.nome}').classes('text-xl font-bold mb-4')
        
        email = ui.input('E-mail').classes('w-full')
        senha = ui.input('Senha', password=True, password_toggle_button=True).classes('w-full')
        
        # Opções de perfil disponíveis
        perfil = ui.select(
            options=['admin', 'gestor', 'operacional', 'rh', 'financeiro'], 
            label='Perfil de Acesso', 
            value='operacional'
        ).classes('w-full')
        
        status_msg = ui.label('').classes('text-sm mt-2')

        def salvar():
            if not email.value or not senha.value:
                status_msg.text = 'Preencha todos os campos.'
                status_msg.classes('text-red-500')
                return

            sucesso, msg = criar_novo_usuario_db(
                email.value, 
                senha.value, 
                perfil.value, 
                state.user.cliente_id # Vincula ao mesmo cliente do admin logado
            )
            
            status_msg.text = msg
            if sucesso:
                status_msg.classes('text-green-600')
                ui.timer(1.5, dialog.close) # Fecha após 1.5s
            else:
                status_msg.classes('text-red-600')

        with ui.row().classes('w-full justify-end mt-4'):
            ui.button('Cancelar', on_click=dialog.close).props('flat')
            ui.button('Salvar Usuário', on_click=salvar).classes('bg-blue-600 text-white')
    
    dialog.open()


# --- Telas ---

def tela_login(state: AppState):
    ui.clear()
    with ui.column().classes('w-full h-screen items-center justify-center bg-gray-100'):
        with ui.card().classes('w-96 p-8'):
            ui.label('CX Data').classes('text-3xl font-bold text-center mb-2 text-blue-600')
            ui.label('Portal de Dashboards').classes('text-center text-gray-600 mb-6')
            
            email_input = ui.input('Email').classes('w-full').props('outlined')
            password_input = ui.input('Senha', password=True, password_toggle_button=True).classes('w-full').props('outlined')
            erro_label = ui.label('').classes('text-red-600 text-sm mt-2 hidden')
            
            def processar_login():
                user = autenticar_usuario(email_input.value.strip(), password_input.value)
                if user:
                    state.fazer_login(user)
                    tela_principal(state)
                else:
                    erro_label.text = 'Email ou senha incorretos'
                    erro_label.classes(remove='hidden')
            
            ui.button('Entrar', on_click=processar_login).classes('w-full bg-blue-600 text-white mt-4').props('size=lg')

def tela_principal(state: AppState):
    ui.clear()
    
    # Header
    with ui.header().classes('bg-blue-600 text-white shadow-lg'):
        with ui.row().classes('w-full items-center justify-between px-6 py-3'):
            ui.label('CX Data').classes('text-2xl font-bold')
            
            with ui.row().classes('items-center gap-4'):
                # Botão de Admin (Só aparece se for admin)
                if state.perfil == 'admin':
                    ui.button('Gerenciar Usuários', icon='person_add', 
                              on_click=lambda: abrir_modal_criar_usuario(state)).props('flat color=white')

                ui.label(state.user.email).classes('text-sm opacity-90')
                ui.button('Sair', icon='logout', on_click=lambda: [state.fazer_logout(), tela_login(state)]).props('flat color=white')
    
    # Grid Dashboards
    with ui.column().classes('w-full p-8 bg-gray-50 min-h-screen'):
        ui.label(f'Olá, {state.cliente.nome}').classes('text-xl text-gray-500')
        ui.label('Meus Dashboards').classes('text-3xl font-bold mb-6 text-gray-800')
        
        if state.dashboards_autorizados:
            with ui.grid(columns='repeat(auto-fill, minmax(300px, 1fr))').classes('gap-6 w-full'):
                for dashboard in state.dashboards_autorizados:
                    criar_card_dashboard(dashboard, state)
        else:
            with ui.card().classes('w-full p-8 text-center'):
                ui.icon('dashboard', size='4rem').classes('text-gray-400 mb-4')
                ui.label('Nenhum dashboard disponível para seu perfil.').classes('text-xl text-gray-600')

def criar_card_dashboard(dashboard: Dashboard, state: AppState):
    tipo_config = {
        'financeiro': {'icon': 'attach_money', 'color': 'green'},
        'rh': {'icon': 'people', 'color': 'blue'},
        'comercial': {'icon': 'shopping_cart', 'color': 'orange'},
        'operacional': {'icon': 'settings', 'color': 'purple'},
    }
    config = tipo_config.get(dashboard.tipo.lower(), {'icon': 'dashboard', 'color': 'gray'})
    
    with ui.card().classes('cursor-pointer hover:shadow-xl transition-shadow duration-200').on('click', lambda: tela_dashboard(dashboard, state)):
        with ui.card_section().classes(f'bg-{config["color"]}-100 p-6'):
            ui.icon(config['icon'], size='3rem').classes(f'text-{config["color"]}-600')
        with ui.card_section().classes('p-4'):
            ui.label(dashboard.nome).classes('text-xl font-bold text-gray-800 mb-2')
            with ui.badge().classes(f'bg-{config["color"]}-500 text-white px-3 py-1'):
                ui.label(dashboard.tipo.capitalize()).classes('text-sm')

def tela_dashboard(dashboard: Dashboard, state: AppState):
    ui.clear()
    with ui.header().classes('bg-blue-600 text-white shadow-lg'):
        with ui.row().classes('w-full items-center justify-between px-6 py-3'):
            with ui.row().classes('items-center gap-4'):
                ui.button(icon='arrow_back', on_click=lambda: tela_principal(state)).props('flat color=white')
                ui.label(dashboard.nome).classes('text-xl font-bold')
    
    with ui.column().classes('w-full h-screen p-0 m-0'):
        ui.html(f'<iframe src="{dashboard.link_embed}" style="width: 100%; height: calc(100vh - 64px); border: none;"></iframe>')

# ============================================================================
# INICIALIZAÇÃO E EXECUÇÃO
# ============================================================================

Base.metadata.create_all(bind=engine)
# REMOVIDO: app.storage.user['state'] = AppState() <--- A LINHA QUE CAUSAVA O ERRO FOI APAGADA

@ui.page('/')
def index():
    # A inicialização correta acontece AQUI dentro, quando o usuário acessa
    state: AppState = app.storage.user.get('state', AppState())
    
    if state.esta_autenticado():
        tela_principal(state)
    else:
        tela_login(state)

if __name__ in {'__main__', '__mp_main__'}:
    # Render define a porta na variável de ambiente PORT.
    port = int(os.environ.get('PORT', 8080))
    
    ui.run(
        title='CX Data', 
        favicon='📊', 
        host='0.0.0.0',
        port=port,
        storage_secret='cx_secret_key_123', # Necessário para o login funcionar
        reload=False
    )
