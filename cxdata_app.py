"""
CX Data - Premium Analytics Platform
============================================
Enterprise-grade B2B SaaS Dashboard Portal
Design System: Inspired by Linear, Vercel, Stripe, Notion
"""

from nicegui import ui, app
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError
import hashlib
from typing import Optional, List
import os
from datetime import datetime

# ============================================================================
# DESIGN SYSTEM - Tokens de Design Profissional
# ============================================================================

class DesignTokens:
    """Sistema de design tokens para consistência visual premium"""
    
    # Colors - Paleta profissional sofisticada
    PRIMARY = '#6366f1'  # Indigo moderno
    PRIMARY_HOVER = '#4f46e5'
    PRIMARY_LIGHT = '#eef2ff'
    
    SURFACE = '#ffffff'
    SURFACE_SECONDARY = '#fafbfc'
    SURFACE_TERTIARY = '#f7f8fa'
    
    BORDER = '#e5e7eb'
    BORDER_LIGHT = '#f3f4f6'
    BORDER_FOCUS = '#6366f1'
    
    TEXT_PRIMARY = '#0f172a'
    TEXT_SECONDARY = '#475569'
    TEXT_TERTIARY = '#94a3b8'
    TEXT_DISABLED = '#cbd5e1'
    
    SUCCESS = '#10b981'
    SUCCESS_BG = '#ecfdf5'
    WARNING = '#f59e0b'
    WARNING_BG = '#fffbeb'
    ERROR = '#ef4444'
    ERROR_BG = '#fef2f2'
    INFO = '#3b82f6'
    INFO_BG = '#eff6ff'
    
    # Shadows - Sistema de elevação profissional
    SHADOW_SM = '0 1px 2px 0 rgb(0 0 0 / 0.05)'
    SHADOW_MD = '0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05)'
    SHADOW_LG = '0 10px 15px -3px rgb(0 0 0 / 0.05), 0 4px 6px -4px rgb(0 0 0 / 0.05)'
    SHADOW_XL = '0 20px 25px -5px rgb(0 0 0 / 0.05), 0 8px 10px -6px rgb(0 0 0 / 0.05)'
    
    # Typography
    FONT_FAMILY = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    
    # Spacing
    SPACING_BASE = 16
    
    # Border Radius
    RADIUS_SM = '6px'
    RADIUS_MD = '8px'
    RADIUS_LG = '12px'
    RADIUS_XL = '16px'
    
    # Transitions
    TRANSITION_FAST = '150ms cubic-bezier(0.4, 0, 0.2, 1)'
    TRANSITION_BASE = '200ms cubic-bezier(0.4, 0, 0.2, 1)'
    TRANSITION_SLOW = '300ms cubic-bezier(0.4, 0, 0.2, 1)'

# ============================================================================
# COMPONENTES UI REUTILIZÁVEIS - Design System
# ============================================================================

class PremiumComponents:
    """Biblioteca de componentes UI premium reutilizáveis"""
    
    @staticmethod
    def input_field(label: str, password: bool = False, placeholder: str = '', icon: Optional[str] = None):
        """Input field premium com estados visuais sofisticados"""
        with ui.column().classes('w-full gap-2'):
            # Label
            ui.label(label).classes('text-sm font-medium').style(f'''
                color: {DesignTokens.TEXT_SECONDARY};
                letter-spacing: -0.01em;
            ''')
            
            # Input wrapper para adicionar ícone se necessário
            with ui.row().classes('w-full items-center relative'):
                if icon:
                    ui.icon(icon, size='20px').classes('absolute left-3 z-10').style(f'''
                        color: {DesignTokens.TEXT_TERTIARY};
                        pointer-events: none;
                    ''')
                
                input_field = ui.input(placeholder=placeholder, password=password).classes('w-full').props('outlined borderless').style(f'''
                    background: {DesignTokens.SURFACE};
                    border: 1.5px solid {DesignTokens.BORDER};
                    border-radius: {DesignTokens.RADIUS_MD};
                    font-size: 15px;
                    font-family: {DesignTokens.FONT_FAMILY};
                    color: {DesignTokens.TEXT_PRIMARY};
                    transition: all {DesignTokens.TRANSITION_FAST};
                    padding-left: {'40px' if icon else '16px'};
                ''')
                
                # Estados de interação via JavaScript
                input_field.on('focus', lambda: input_field.style(f'''
                    border-color: {DesignTokens.PRIMARY};
                    box-shadow: 0 0 0 3px {DesignTokens.PRIMARY_LIGHT};
                '''))
                
                input_field.on('blur', lambda: input_field.style(f'''
                    border-color: {DesignTokens.BORDER};
                    box-shadow: none;
                '''))
                
                return input_field
    
    @staticmethod
    def primary_button(text: str, on_click=None, full_width: bool = False, loading: bool = False, icon: Optional[str] = None):
        """Botão primary premium com estados e microinterações"""
        button = ui.button(text, on_click=on_click).props('no-caps flat').style(f'''
            background: {DesignTokens.PRIMARY};
            color: white;
            border-radius: {DesignTokens.RADIUS_MD};
            padding: 12px 24px;
            font-size: 15px;
            font-weight: 600;
            font-family: {DesignTokens.FONT_FAMILY};
            letter-spacing: -0.01em;
            border: none;
            box-shadow: {DesignTokens.SHADOW_SM};
            transition: all {DesignTokens.TRANSITION_FAST};
            cursor: pointer;
            {'width: 100%;' if full_width else ''}
        ''')
        
        if icon:
            button.props(f'icon={icon}')
        
        # Hover state
        button.on('mouseenter', lambda: button.style(f'''
            background: {DesignTokens.PRIMARY_HOVER};
            box-shadow: {DesignTokens.SHADOW_MD};
            transform: translateY(-1px);
        '''))
        
        button.on('mouseleave', lambda: button.style(f'''
            background: {DesignTokens.PRIMARY};
            box-shadow: {DesignTokens.SHADOW_SM};
            transform: translateY(0);
        '''))
        
        return button
    
    @staticmethod
    def ghost_button(text: str, on_click=None, icon: Optional[str] = None):
        """Botão ghost/secondary premium"""
        button = ui.button(text, on_click=on_click).props('no-caps flat').style(f'''
            background: transparent;
            color: {DesignTokens.TEXT_SECONDARY};
            border: 1.5px solid {DesignTokens.BORDER};
            border-radius: {DesignTokens.RADIUS_MD};
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
            font-family: {DesignTokens.FONT_FAMILY};
            transition: all {DesignTokens.TRANSITION_FAST};
            cursor: pointer;
        ''')
        
        if icon:
            button.props(f'icon={icon}')
        
        button.on('mouseenter', lambda: button.style(f'''
            background: {DesignTokens.SURFACE_TERTIARY};
            border-color: {DesignTokens.TEXT_TERTIARY};
        '''))
        
        button.on('mouseleave', lambda: button.style(f'''
            background: transparent;
            border-color: {DesignTokens.BORDER};
        '''))
        
        return button
    
    @staticmethod
    def icon_button(icon: str, on_click=None, tooltip: str = ''):
        """Botão de ícone premium com tooltip"""
        button = ui.button(icon=icon, on_click=on_click).props('flat round dense').style(f'''
            background: transparent;
            color: {DesignTokens.TEXT_SECONDARY};
            border: none;
            min-width: 36px;
            padding: 8px;
            transition: all {DesignTokens.TRANSITION_FAST};
        ''')
        
        if tooltip:
            button.tooltip(tooltip)
        
        button.on('mouseenter', lambda: button.style(f'''
            background: {DesignTokens.SURFACE_TERTIARY};
            color: {DesignTokens.TEXT_PRIMARY};
        '''))
        
        button.on('mouseleave', lambda: button.style(f'''
            background: transparent;
            color: {DesignTokens.TEXT_SECONDARY};
        '''))
        
        return button

# ============================================================================
# BANCO DE DADOS
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
# MODELOS
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
# LÓGICA
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
# ESTADO DO USUÁRIO
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
# TELAS (FRONTEND PREMIUM)
# ============================================================================

@ui.page('/login')
def page_login():
    """Tela de Login - Premium Authentication Experience"""
    state = app.storage.user.get('state', AppState())
    
    if state.user_email:
        ui.navigate.to('/')
        return

    # Background com gradiente sutil premium
    with ui.column().classes('w-full h-screen items-center justify-center').style(f'''
        background: linear-gradient(135deg, {DesignTokens.SURFACE_SECONDARY} 0%, {DesignTokens.PRIMARY_LIGHT} 100%);
        position: relative;
        overflow: hidden;
    '''):
        
        # Pattern de fundo sutil (opcional, decorativo)
        ui.html('''
            <div style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-image: radial-gradient(circle at 20px 20px, rgba(99, 102, 241, 0.03) 1px, transparent 0);
                background-size: 40px 40px;
                pointer-events: none;
            "></div>
        ''')
        
        # Container central premium com elevação
        with ui.column().classes('w-full max-w-md px-8 relative z-10').style('gap: 48px;'):
            
            # Branding premium
            with ui.column().classes('items-center gap-4'):
                # Logo placeholder (pode ser substituído por imagem real)
                with ui.column().classes('items-center justify-center').style(f'''
                    width: 56px;
                    height: 56px;
                    background: linear-gradient(135deg, {DesignTokens.PRIMARY} 0%, {DesignTokens.PRIMARY_HOVER} 100%);
                    border-radius: {DesignTokens.RADIUS_LG};
                    box-shadow: {DesignTokens.SHADOW_LG};
                '''):
                    ui.icon('analytics', size='32px', color='white')
                
                ui.label('CX Data').classes('text-3xl font-bold').style(f'''
                    color: {DesignTokens.TEXT_PRIMARY};
                    letter-spacing: -0.03em;
                    font-family: {DesignTokens.FONT_FAMILY};
                ''')
                
                ui.label('Enterprise Analytics Platform').classes('text-sm font-medium').style(f'''
                    color: {DesignTokens.TEXT_TERTIARY};
                    letter-spacing: 0.01em;
                ''')
            
            # Card de login premium
            with ui.column().classes('w-full gap-6').style(f'''
                background: {DesignTokens.SURFACE};
                border: 1px solid {DesignTokens.BORDER_LIGHT};
                border-radius: {DesignTokens.RADIUS_XL};
                padding: 40px;
                box-shadow: {DesignTokens.SHADOW_XL};
                backdrop-filter: blur(10px);
            '''):
                
                # Título do card
                with ui.column().classes('gap-2 mb-2'):
                    ui.label('Welcome back').classes('text-xl font-semibold').style(f'''
                        color: {DesignTokens.TEXT_PRIMARY};
                        letter-spacing: -0.02em;
                    ''')
                    ui.label('Sign in to access your analytics workspace').classes('text-sm').style(f'''
                        color: {DesignTokens.TEXT_SECONDARY};
                    ''')
                
                # Inputs premium
                email = PremiumComponents.input_field('Email address', icon='mail', placeholder='you@company.com')
                senha = PremiumComponents.input_field('Password', password=True, icon='lock', placeholder='Enter your password')
                
                # Mensagem de erro premium
                erro_container = ui.row().classes('w-full items-center gap-2 hidden').style(f'''
                    background: {DesignTokens.ERROR_BG};
                    border: 1px solid {DesignTokens.ERROR};
                    border-radius: {DesignTokens.RADIUS_MD};
                    padding: 12px 16px;
                ''')
                
                with erro_container:
                    ui.icon('error', size='20px').style(f'color: {DesignTokens.ERROR};')
                    erro_label = ui.label('').classes('text-sm font-medium').style(f'color: {DesignTokens.ERROR};')
                
                # Estado de loading
                loading_state = {'is_loading': False}
                
                def try_login():
                    if loading_state['is_loading']:
                        return
                    
                    # Validação básica
                    if not email.value.strip() or not senha.value:
                        erro_label.text = 'Please fill in all fields'
                        erro_container.classes(remove='hidden')
                        # Animação de shake (simulada via timeout)
                        ui.timer(0.5, lambda: erro_container.classes(add='hidden'), once=True)
                        return
                    
                    loading_state['is_loading'] = True
                    login_btn.set_text('Signing in...')
                    login_btn.props('disable')
                    
                    # Simulação de loading (em produção, seria assíncrono)
                    def finish_login():
                        user = autenticar_usuario(email.value.strip(), senha.value)
                        if user:
                            state.login(user) 
                            app.storage.user['state'] = state
                            ui.navigate.to('/')
                        else:
                            erro_label.text = 'Invalid email or password'
                            erro_container.classes(remove='hidden')
                            login_btn.set_text('Sign in')
                            login_btn.props(remove='disable')
                            loading_state['is_loading'] = False
                            
                            # Auto-hide error após 3s
                            ui.timer(3, lambda: erro_container.classes(add='hidden'), once=True)
                    
                    ui.timer(0.3, finish_login, once=True)
                
                # Botão de login premium
                login_btn = PremiumComponents.primary_button('Sign in', on_click=try_login, full_width=True, icon='arrow_forward')
                
                # Enter key support
                senha.on('keydown.enter', try_login)
                
                # Link "Forgot password" (opcional)
                with ui.row().classes('w-full justify-center mt-2'):
                    ui.label('Forgot your password?').classes('text-sm cursor-pointer').style(f'''
                        color: {DesignTokens.TEXT_TERTIARY};
                        transition: color {DesignTokens.TRANSITION_FAST};
                    ''').on('mouseenter', lambda e: e.sender.style(f'color: {DesignTokens.PRIMARY};')).on('mouseleave', lambda e: e.sender.style(f'color: {DesignTokens.TEXT_TERTIARY};'))
            
            # Footer
            with ui.row().classes('w-full justify-center gap-1'):
                ui.label('©').classes('text-xs').style(f'color: {DesignTokens.TEXT_DISABLED};')
                ui.label('2024 CX Data.').classes('text-xs').style(f'color: {DesignTokens.TEXT_DISABLED};')
                ui.label('All rights reserved.').classes('text-xs').style(f'color: {DesignTokens.TEXT_DISABLED};')

@ui.page('/')
def page_home():
    """Tela Principal - Premium Dashboard Hub"""
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

    # Layout principal com sidebar
    with ui.row().classes('w-full h-screen').style(f'''
        background: {DesignTokens.SURFACE_SECONDARY};
        margin: 0;
        padding: 0;
        font-family: {DesignTokens.FONT_FAMILY};
    '''):
        
        # Sidebar premium com navegação
        with ui.column().classes('h-screen').style(f'''
            width: 260px;
            background: {DesignTokens.SURFACE};
            border-right: 1px solid {DesignTokens.BORDER};
            padding: 24px 16px;
            display: flex;
            flex-direction: column;
            gap: 32px;
        '''):
            
            # Logo e branding
            with ui.row().classes('items-center gap-3 px-3'):
                with ui.column().classes('items-center justify-center').style(f'''
                    width: 36px;
                    height: 36px;
                    background: linear-gradient(135deg, {DesignTokens.PRIMARY} 0%, {DesignTokens.PRIMARY_HOVER} 100%);
                    border-radius: {DesignTokens.RADIUS_MD};
                    box-shadow: {DesignTokens.SHADOW_SM};
                '''):
                    ui.icon('analytics', size='20px', color='white')
                
                with ui.column().classes('gap-0'):
                    ui.label('CX Data').classes('text-base font-semibold').style(f'''
                        color: {DesignTokens.TEXT_PRIMARY};
                        letter-spacing: -0.01em;
                    ''')
                    ui.label('Analytics').classes('text-xs font-medium').style(f'''
                        color: {DesignTokens.TEXT_TERTIARY};
                    ''')
            
            # Navegação principal
            with ui.column().classes('gap-1 flex-1'):
                # Menu item ativo
                with ui.row().classes('items-center gap-3 px-3 py-2.5 cursor-pointer').style(f'''
                    background: {DesignTokens.PRIMARY_LIGHT};
                    border-radius: {DesignTokens.RADIUS_MD};
                    transition: all {DesignTokens.TRANSITION_FAST};
                '''):
                    ui.icon('dashboard', size='20px').style(f'color: {DesignTokens.PRIMARY};')
                    ui.label('Dashboards').classes('text-sm font-medium').style(f'''
                        color: {DesignTokens.PRIMARY};
                        letter-spacing: -0.01em;
                    ''')
                
                # Menu items inativos (placeholder para futuras funcionalidades)
                for item_data in [
                    {'icon': 'bar_chart', 'label': 'Reports'},
                    {'icon': 'folder', 'label': 'Projects'},
                    {'icon': 'settings', 'label': 'Settings'}
                ]:
                    item_row = ui.row().classes('items-center gap-3 px-3 py-2.5 cursor-pointer').style(f'''
                        background: transparent;
                        border-radius: {DesignTokens.RADIUS_MD};
                        transition: all {DesignTokens.TRANSITION_FAST};
                    ''')
                    
                    with item_row:
                        ui.icon(item_data['icon'], size='20px').style(f'color: {DesignTokens.TEXT_TERTIARY};')
                        ui.label(item_data['label']).classes('text-sm font-medium').style(f'''
                            color: {DesignTokens.TEXT_SECONDARY};
                            letter-spacing: -0.01em;
                        ''')
                    
                    # Hover effect
                    item_row.on('mouseenter', lambda e: e.sender.style(f'background: {DesignTokens.SURFACE_TERTIARY};'))
                    item_row.on('mouseleave', lambda e: e.sender.style('background: transparent;'))
            
            # User section no rodapé da sidebar
            with ui.column().classes('gap-3'):
                ui.separator().style(f'background: {DesignTokens.BORDER_LIGHT};')
                
                with ui.row().classes('items-center gap-3 px-3 py-2').style(f'''
                    background: {DesignTokens.SURFACE_TERTIARY};
                    border-radius: {DesignTokens.RADIUS_MD};
                '''):
                    # Avatar com iniciais
                    iniciais = ''.join([palavra[0].upper() for palavra in cliente.nome.split()[:2]])
                    with ui.column().classes('items-center justify-center').style(f'''
                        width: 36px;
                        height: 36px;
                        background: linear-gradient(135deg, {DesignTokens.PRIMARY} 0%, {DesignTokens.PRIMARY_HOVER} 100%);
                        border-radius: {DesignTokens.RADIUS_MD};
                        font-size: 14px;
                        font-weight: 600;
                        color: white;
                    '''):
                        ui.label(iniciais)
                    
                    with ui.column().classes('gap-0 flex-1'):
                        ui.label(cliente.nome).classes('text-sm font-medium truncate').style(f'''
                            color: {DesignTokens.TEXT_PRIMARY};
                            max-width: 140px;
                        ''')
                        ui.label(user.email).classes('text-xs truncate').style(f'''
                            color: {DesignTokens.TEXT_TERTIARY};
                            max-width: 140px;
                        ''')
        
        # Área de conteúdo principal
        with ui.column().classes('flex-1 h-screen overflow-auto').style('padding: 0;'):
            
            # Header com ações
            with ui.row().classes('w-full items-center justify-between').style(f'''
                padding: 20px 40px;
                background: {DesignTokens.SURFACE};
                border-bottom: 1px solid {DesignTokens.BORDER};
                min-height: 72px;
            '''):
                # Breadcrumb e título
                with ui.column().classes('gap-1'):
                    ui.label('Your workspace').classes('text-xs font-medium').style(f'''
                        color: {DesignTokens.TEXT_TERTIARY};
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ''')
                    ui.label(cliente.nome).classes('text-lg font-semibold').style(f'''
                        color: {DesignTokens.TEXT_PRIMARY};
                        letter-spacing: -0.02em;
                    ''')
                
                # Ações do header
                with ui.row().classes('items-center gap-3'):
                    # Status badge
                    with ui.row().classes('items-center gap-2 px-3 py-1.5').style(f'''
                        background: {DesignTokens.SUCCESS_BG};
                        border-radius: {DesignTokens.RADIUS_MD};
                    '''):
                        ui.icon('check_circle', size='16px').style(f'color: {DesignTokens.SUCCESS};')
                        ui.label('Active').classes('text-xs font-semibold').style(f'''
                            color: {DesignTokens.SUCCESS};
                            letter-spacing: 0.02em;
                        ''')
                    
                    def logout_action():
                        state.logout()
                        app.storage.user['state'] = state
                        ui.navigate.to('/login')
                    
                    PremiumComponents.ghost_button('Sign out', on_click=logout_action, icon='logout')
            
            # Conteúdo principal
            with ui.column().classes('w-full').style('padding: 40px; max-width: 1600px; margin: 0 auto;'):
                
                # Cabeçalho da seção
                with ui.column().classes('gap-3 mb-8'):
                    ui.label('Analytics dashboards').classes('text-2xl font-bold').style(f'''
                        color: {DesignTokens.TEXT_PRIMARY};
                        letter-spacing: -0.03em;
                    ''')
                    ui.label('Access real-time insights and data visualizations for your organization').classes('text-base').style(f'''
                        color: {DesignTokens.TEXT_SECONDARY};
                        line-height: 1.6;
                    ''')
                
                if dashboards:
                    # Grid de cards premium
                    with ui.grid(columns='repeat(auto-fill, minmax(360px, 1fr))').classes('w-full').style('gap: 24px;'):
                        for dash in dashboards:
                            
                            # Configuração de tema por tipo
                            tipo_themes = {
                                'financeiro': {
                                    'color': DesignTokens.SUCCESS,
                                    'bg': DesignTokens.SUCCESS_BG,
                                    'icon': 'account_balance_wallet',
                                    'gradient': f'linear-gradient(135deg, {DesignTokens.SUCCESS} 0%, #059669 100%)'
                                },
                                'rh': {
                                    'color': DesignTokens.PRIMARY,
                                    'bg': DesignTokens.PRIMARY_LIGHT,
                                    'icon': 'people',
                                    'gradient': f'linear-gradient(135deg, {DesignTokens.PRIMARY} 0%, {DesignTokens.PRIMARY_HOVER} 100%)'
                                },
                                'comercial': {
                                    'color': DesignTokens.WARNING,
                                    'bg': DesignTokens.WARNING_BG,
                                    'icon': 'storefront',
                                    'gradient': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'
                                },
                                'operacional': {
                                    'color': '#8b5cf6',
                                    'bg': '#faf5ff',
                                    'icon': 'settings',
                                    'gradient': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)'
                                }
                            }
                            
                            theme = tipo_themes.get(dash.tipo.lower(), {
                                'color': DesignTokens.TEXT_SECONDARY,
                                'bg': DesignTokens.SURFACE_TERTIARY,
                                'icon': 'dashboard',
                                'gradient': f'linear-gradient(135deg, {DesignTokens.TEXT_SECONDARY} 0%, {DesignTokens.TEXT_TERTIARY} 100%)'
                            })
                            
                            # Card premium com microinterações
                            card = ui.column().classes('cursor-pointer group').style(f'''
                                background: {DesignTokens.SURFACE};
                                border: 1px solid {DesignTokens.BORDER};
                                border-radius: {DesignTokens.RADIUS_LG};
                                overflow: hidden;
                                transition: all {DesignTokens.TRANSITION_BASE};
                                box-shadow: {DesignTokens.SHADOW_SM};
                            ''')
                            
                            with card:
                                # Header com gradiente
                                with ui.row().classes('items-center justify-between w-full').style(f'''
                                    padding: 24px;
                                    background: {theme["bg"]};
                                    border-bottom: 1px solid {DesignTokens.BORDER_LIGHT};
                                '''):
                                    # Ícone com gradiente
                                    with ui.column().classes('items-center justify-center').style(f'''
                                        width: 48px;
                                        height: 48px;
                                        background: {theme["gradient"]};
                                        border-radius: {DesignTokens.RADIUS_MD};
                                        box-shadow: {DesignTokens.SHADOW_MD};
                                    '''):
                                        ui.icon(theme['icon'], size='24px', color='white')
                                    
                                    # Badge de tipo
                                    ui.label(dash.tipo.upper()).classes('text-xs font-bold').style(f'''
                                        color: {theme["color"]};
                                        background: {DesignTokens.SURFACE};
                                        padding: 4px 10px;
                                        border-radius: {DesignTokens.RADIUS_SM};
                                        letter-spacing: 0.08em;
                                        box-shadow: {DesignTokens.SHADOW_SM};
                                    ''')
                                
                                # Conteúdo do card
                                with ui.column().classes('gap-4').style('padding: 24px;'):
                                    # Título e descrição
                                    with ui.column().classes('gap-2'):
                                        ui.label(dash.nome).classes('text-lg font-semibold').style(f'''
                                            color: {DesignTokens.TEXT_PRIMARY};
                                            line-height: 1.4;
                                            letter-spacing: -0.01em;
                                        ''')
                                        
                                        ui.label('Real-time analytics and insights').classes('text-sm').style(f'''
                                            color: {DesignTokens.TEXT_SECONDARY};
                                            line-height: 1.5;
                                        ''')
                                    
                                    # Footer com CTA
                                    with ui.row().classes('items-center gap-2 mt-2'):
                                        ui.label('Open dashboard').classes('text-sm font-medium').style(f'''
                                            color: {theme["color"]};
                                            transition: all {DesignTokens.TRANSITION_FAST};
                                        ''')
                                        ui.icon('arrow_forward', size='18px').style(f'''
                                            color: {theme["color"]};
                                            transition: all {DesignTokens.TRANSITION_FAST};
                                        ''')
                            
                            # Hover effects
                            card.on('mouseenter', lambda e, c=card: c.style(f'''
                                border-color: {DesignTokens.PRIMARY};
                                box-shadow: {DesignTokens.SHADOW_LG};
                                transform: translateY(-4px);
                            '''))
                            
                            card.on('mouseleave', lambda e, c=card: c.style(f'''
                                border-color: {DesignTokens.BORDER};
                                box-shadow: {DesignTokens.SHADOW_SM};
                                transform: translateY(0);
                            '''))
                            
                            # Click action
                            card.on('click', lambda d=dash: ui.navigate.to(f'/dashboard/{d.id}'))
                
                else:
                    # Empty state premium
                    with ui.column().classes('items-center justify-center w-full').style('padding: 120px 0;'):
                        with ui.column().classes('items-center gap-6 max-w-md text-center'):
                            # Ícone ilustrativo
                            with ui.column().classes('items-center justify-center').style(f'''
                                width: 80px;
                                height: 80px;
                                background: {DesignTokens.SURFACE_TERTIARY};
                                border-radius: {DesignTokens.RADIUS_XL};
                                border: 1px solid {DesignTokens.BORDER};
                            '''):
                                ui.icon('analytics', size='40px').style(f'color: {DesignTokens.TEXT_DISABLED};')
                            
                            # Mensagem
                            with ui.column().classes('gap-3'):
                                ui.label('No dashboards available').classes('text-xl font-semibold').style(f'''
                                    color: {DesignTokens.TEXT_PRIMARY};
                                    letter-spacing: -0.02em;
                                ''')
                                
                                ui.label('Your analytics dashboards will appear here once they\'re assigned to your account. Contact your administrator for access.').classes('text-base').style(f'''
                                    color: {DesignTokens.TEXT_SECONDARY};
                                    line-height: 1.6;
                                ''')

@ui.page('/dashboard/{dash_id}')
def page_dashboard(dash_id: int):
    """Tela de Visualização - Premium Embed Experience"""
    state = app.storage.user.get('state', AppState())
    if not state or not state.user_email:
        ui.navigate.to('/login'); return

    db = SessionLocal()
    dash = db.query(Dashboard).filter(Dashboard.id == dash_id).first()
    db.close()

    if not dash:
        # Error state premium
        with ui.column().classes('w-full h-screen items-center justify-center').style(f'background: {DesignTokens.SURFACE_SECONDARY};'):
            with ui.column().classes('items-center gap-4'):
                ui.icon('error_outline', size='64px').style(f'color: {DesignTokens.ERROR};')
                ui.label('Dashboard not found').classes('text-2xl font-semibold').style(f'color: {DesignTokens.TEXT_PRIMARY};')
                PremiumComponents.primary_button('Return to home', on_click=lambda: ui.navigate.to('/'))
        return

    # Estado de fullscreen
    fullscreen_state = {'active': False}
    
    # Container principal
    with ui.column().classes('w-full h-screen').style(f'''
        background: {DesignTokens.SURFACE_SECONDARY};
        margin: 0;
        padding: 0;
        font-family: {DesignTokens.FONT_FAMILY};
    '''):
        
        # Header premium com toolbar
        header = ui.row().classes('w-full items-center justify-between').style(f'''
            padding: 16px 32px;
            background: {DesignTokens.SURFACE};
            border-bottom: 1px solid {DesignTokens.BORDER};
            min-height: 64px;
            z-index: 100;
            transition: all {DesignTokens.TRANSITION_BASE};
        ''')
        
        with header:
            # Lado esquerdo - navegação e info
            with ui.row().classes('items-center gap-4'):
                PremiumComponents.icon_button('arrow_back', on_click=lambda: ui.navigate.to('/'), tooltip='Back to home')
                
                ui.separator().classes('h-6').style(f'background: {DesignTokens.BORDER};')
                
                with ui.row().classes('items-center gap-3'):
                    # Ícone do tipo
                    tipo_icons = {
                        'financeiro': 'account_balance_wallet',
                        'rh': 'people',
                        'comercial': 'storefront',
                        'operacional': 'settings'
                    }
                    icon_name = tipo_icons.get(dash.tipo.lower(), 'dashboard')
                    
                    with ui.column().classes('items-center justify-center').style(f'''
                        width: 32px;
                        height: 32px;
                        background: {DesignTokens.PRIMARY_LIGHT};
                        border-radius: {DesignTokens.RADIUS_MD};
                    '''):
                        ui.icon(icon_name, size='18px').style(f'color: {DesignTokens.PRIMARY};')
                    
                    # Título e meta
                    with ui.column().classes('gap-0'):
                        ui.label(dash.nome).classes('text-base font-semibold').style(f'''
                            color: {DesignTokens.TEXT_PRIMARY};
                            letter-spacing: -0.01em;
                        ''')
                        
                        with ui.row().classes('items-center gap-2'):
                            ui.label(dash.tipo.upper()).classes('text-xs font-medium').style(f'''
                                color: {DesignTokens.TEXT_TERTIARY};
                                letter-spacing: 0.05em;
                            ''')
                            ui.label('•').classes('text-xs').style(f'color: {DesignTokens.TEXT_DISABLED};')
                            
                            # Status live
                            with ui.row().classes('items-center gap-1'):
                                ui.html(f'''
                                    <div style="
                                        width: 6px;
                                        height: 6px;
                                        background: {DesignTokens.SUCCESS};
                                        border-radius: 50%;
                                        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
                                    "></div>
                                    <style>
                                        @keyframes pulse {{
                                            0%, 100% {{ opacity: 1; }}
                                            50% {{ opacity: 0.5; }}
                                        }}
                                    </style>
                                ''')
                                ui.label('Live').classes('text-xs font-medium').style(f'color: {DesignTokens.SUCCESS};')
            
            # Lado direito - controles
            with ui.row().classes('items-center gap-2'):
                # Refresh button
                refresh_btn = PremiumComponents.icon_button('refresh', tooltip='Refresh dashboard')
                
                def refresh_dashboard():
                    # Simula refresh recarregando o iframe
                    refresh_btn.props('loading')
                    ui.timer(1, lambda: refresh_btn.props(remove='loading'), once=True)
                
                refresh_btn.on('click', refresh_dashboard)
                
                # Fullscreen toggle
                fullscreen_btn = PremiumComponents.icon_button('fullscreen', tooltip='Toggle fullscreen')
                
                def toggle_fullscreen():
                    fullscreen_state['active'] = not fullscreen_state['active']
                    if fullscreen_state['active']:
                        header.classes(add='hidden')
                        fullscreen_btn.props('icon=fullscreen_exit')
                    else:
                        header.classes(remove='hidden')
                        fullscreen_btn.props('icon=fullscreen')
                
                fullscreen_btn.on('click', toggle_fullscreen)
        
        # Container do embed com loading state premium
        with ui.column().classes('w-full flex-1').style(f'''
            padding: 20px;
            background: {DesignTokens.SURFACE_SECONDARY};
            position: relative;
        '''):
            
            # Wrapper premium do iframe
            embed_wrapper = ui.column().classes('w-full h-full').style(f'''
                background: {DesignTokens.SURFACE};
                border-radius: {DesignTokens.RADIUS_XL};
                border: 1px solid {DesignTokens.BORDER};
                overflow: hidden;
                box-shadow: {DesignTokens.SHADOW_XL};
                position: relative;
            ''')
            
            with embed_wrapper:
                # Loading overlay premium
                loading_overlay = ui.column().classes('w-full h-full items-center justify-center absolute top-0 left-0 z-50').style(f'''
                    background: linear-gradient(135deg, {DesignTokens.SURFACE} 0%, {DesignTokens.SURFACE_SECONDARY} 100%);
                    backdrop-filter: blur(10px);
                ''')
                
                with loading_overlay:
                    with ui.column().classes('items-center gap-6'):
                        # Spinner animado customizado
                        ui.html(f'''
                            <div style="
                                width: 48px;
                                height: 48px;
                                border: 3px solid {DesignTokens.BORDER};
                                border-top-color: {DesignTokens.PRIMARY};
                                border-radius: 50%;
                                animation: spin 1s linear infinite;
                            "></div>
                            <style>
                                @keyframes spin {{
                                    to {{ transform: rotate(360deg); }}
                                }}
                            </style>
                        ''')
                        
                        with ui.column().classes('items-center gap-2'):
                            ui.label('Loading dashboard...').classes('text-base font-medium').style(f'''
                                color: {DesignTokens.TEXT_PRIMARY};
                            ''')
                            ui.label('Please wait while we prepare your visualization').classes('text-sm').style(f'''
                                color: {DesignTokens.TEXT_TERTIARY};
                            ''')
                
                # Error overlay (hidden por padrão)
                error_overlay = ui.column().classes('w-full h-full items-center justify-center absolute top-0 left-0 z-40 hidden').style(f'''
                    background: {DesignTokens.SURFACE};
                ''')
                
                with error_overlay:
                    with ui.column().classes('items-center gap-6 max-w-md text-center'):
                        with ui.column().classes('items-center justify-center').style(f'''
                            width: 64px;
                            height: 64px;
                            background: {DesignTokens.ERROR_BG};
                            border-radius: {DesignTokens.RADIUS_XL};
                        '''):
                            ui.icon('error_outline', size='32px').style(f'color: {DesignTokens.ERROR};')
                        
                        with ui.column().classes('gap-3'):
                            ui.label('Failed to load dashboard').classes('text-xl font-semibold').style(f'''
                                color: {DesignTokens.TEXT_PRIMARY};
                            ''')
                            ui.label('The dashboard could not be loaded. Please check your connection and try again.').classes('text-base').style(f'''
                                color: {DesignTokens.TEXT_SECONDARY};
                                line-height: 1.6;
                            ''')
                        
                        with ui.row().classes('gap-3'):
                            PremiumComponents.primary_button('Reload dashboard', on_click=lambda: ui.navigate.reload())
                            PremiumComponents.ghost_button('Go back', on_click=lambda: ui.navigate.to('/'))
                
                # Iframe embutido profissionalmente
                iframe_id = f'dashboard-iframe-{dash_id}'
                
                iframe_html = f'''
                <iframe 
                    id="{iframe_id}"
                    src="{dash.link_embed}" 
                    style="
                        width: 100%;
                        height: 100%;
                        border: none;
                        display: block;
                        background: white;
                    "
                    allowfullscreen
                    loading="lazy"
                ></iframe>
                
                <script>
                    (function() {{
                        const iframe = document.getElementById('{iframe_id}');
                        const loadingOverlay = iframe.previousElementSibling;
                        const errorOverlay = loadingOverlay.previousElementSibling;
                        
                        // Timeout para considerar erro se não carregar em 15s
                        const timeoutId = setTimeout(() => {{
                            loadingOverlay.classList.add('hidden');
                            errorOverlay.classList.remove('hidden');
                        }}, 15000);
                        
                        iframe.addEventListener('load', function() {{
                            clearTimeout(timeoutId);
                            setTimeout(() => {{
                                loadingOverlay.classList.add('hidden');
                            }}, 500);
                        }});
                        
                        iframe.addEventListener('error', function() {{
                            clearTimeout(timeoutId);
                            loadingOverlay.classList.add('hidden');
                            errorOverlay.classList.remove('hidden');
                        }});
                    }})();
                </script>
                '''
                
                ui.html(iframe_html, sanitize=False)

# ============================================================================
# INICIALIZAÇÃO
# ============================================================================

Base.metadata.create_all(bind=engine)

if __name__ in {'__main__', '__mp_main__'}:
    port = int(os.environ.get('PORT', 8080))
    
    # Estilos globais premium
    ui.add_head_html(f'''
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: {DesignTokens.FONT_FAMILY};
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}
            
            /* Scrollbar customizada premium */
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            
            ::-webkit-scrollbar-track {{
                background: {DesignTokens.SURFACE_SECONDARY};
            }}
            
            ::-webkit-scrollbar-thumb {{
                background: {DesignTokens.BORDER};
                border-radius: 4px;
            }}
            
            ::-webkit-scrollbar-thumb:hover {{
                background: {DesignTokens.TEXT_TERTIARY};
            }}
            
            /* Animações globais */
            @keyframes fadeIn {{
                from {{
                    opacity: 0;
                    transform: translateY(10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
            
            .animate-fade-in {{
                animation: fadeIn 0.3s ease-out;
            }}
        </style>
    ''')
    
    ui.run(
        title='CX Data - Enterprise Analytics',
        favicon='📊',
        host='0.0.0.0',
        port=port,
        storage_secret='cx_key_premium_2024',
        reload=False
    )
