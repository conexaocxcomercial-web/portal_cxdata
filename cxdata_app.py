"""
CX Data - Enterprise Analytics Platform
============================================
Versão 6.1: Menu Lateral Limpo (Removido Reports/Projects/Settings)
"""

from nicegui import ui, app
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
import hashlib
from typing import Optional, List, Callable, Dict, Any
import os
from datetime import datetime, timedelta
import random

# ============================================================================
# DESIGN SYSTEM
# ============================================================================

class DS:
    """Design System - Centralized design tokens"""
    PRIMARY = '#6366f1'       # Indigo Brand Color
    PRIMARY_HOVER = '#4f46e5'
    PRIMARY_LIGHT = '#eef2ff'
    
    SURFACE = '#ffffff'
    SURFACE_50 = '#fafbfc'
    SURFACE_100 = '#f7f8fa'
    SURFACE_HOVER = '#f3f4f6'
    
    BORDER = '#e5e7eb'
    BORDER_LIGHT = '#f3f4f6'
    
    TEXT_PRIMARY = '#0f172a'
    TEXT_SECONDARY = '#475569'
    TEXT_TERTIARY = '#94a3b8'
    TEXT_DISABLED = '#cbd5e1'
    
    SHADOW_SM = '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)'
    SHADOW_MD = '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)'
    SHADOW_LG = '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)'
    
    FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    
    RADIUS_MD = '8px'
    RADIUS_LG = '12px'
    RADIUS_XL = '16px'
    
    TRANSITION_FAST = '150ms cubic-bezier(0.4, 0, 0.2, 1)'

# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

class LayoutComponents:
    @staticmethod
    def page_container(max_width: str = '1600px', padding: str = '40px'):
        return ui.column().classes('w-full').style(f'padding: {padding}; max-width: {max_width}; margin: 0 auto;')
    
    @staticmethod
    def page_header(title: str, subtitle: Optional[str] = None):
        with ui.column().classes('w-full gap-2 mb-8'):
            ui.label(title).classes('text-3xl font-bold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.03em; font-family: {DS.FONT};')
            if subtitle: ui.label(subtitle).classes('text-base').style(f'color: {DS.TEXT_SECONDARY}; line-height: 1.6;')
    
    @staticmethod
    def section_header(title: str, badge: Optional[str] = None):
        with ui.row().classes('w-full items-center gap-3 mb-6'):
            ui.label(title).classes('text-xl font-semibold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.02em;')
            if badge: ui.label(badge).classes('text-xs font-semibold').style(f'color: {DS.PRIMARY}; background: {DS.PRIMARY_LIGHT}; padding: 4px 10px; border-radius: {DS.RADIUS_MD}; letter-spacing: 0.05em;')

    @staticmethod
    def empty_state(icon: str, title: str, description: str):
        with ui.column().classes('w-full items-center justify-center').style('padding: 80px 20px;'):
            ui.icon(icon, size='48px').style(f'color: {DS.TEXT_DISABLED}; margin-bottom: 16px;')
            ui.label(title).classes('text-xl font-semibold').style(f'color: {DS.TEXT_PRIMARY};')
            ui.label(description).classes('text-base text-center').style(f'color: {DS.TEXT_SECONDARY}; max-width: 400px;')

# ============================================================================
# UI COMPONENTS
# ============================================================================

class UIComponents:
    @staticmethod
    def input_field(label: str, password: bool = False, placeholder: str = '', icon: Optional[str] = None):
        with ui.column().classes('w-full gap-2'):
            ui.label(label).classes('text-sm font-medium').style(f'color: {DS.TEXT_SECONDARY};')
            with ui.row().classes('w-full items-center relative'):
                if icon: ui.icon(icon, size='20px').classes('absolute left-3 z-10').style(f'color: {DS.TEXT_TERTIARY}; pointer-events: none;')
                return ui.input(placeholder=placeholder, password=password).classes('w-full').props('outlined borderless').style(f'background: {DS.SURFACE}; border: 1.5px solid {DS.BORDER}; border-radius: {DS.RADIUS_MD}; padding-left: {"40px" if icon else "16px"};')

    @staticmethod
    def primary_button(text: str, on_click=None, full_width: bool = False, icon: Optional[str] = None):
        btn = ui.button(text, on_click=on_click).props('no-caps flat').style(f'background: {DS.PRIMARY}; color: white; border-radius: {DS.RADIUS_MD}; padding: 10px 24px; font-weight: 600; {"width: 100%;" if full_width else ""}')
        if icon: btn.props(f'icon={icon}')
        return btn

    @staticmethod
    def ghost_button(text: str, on_click=None, icon: Optional[str] = None):
        btn = ui.button(text, on_click=on_click).props('no-caps flat').style(f'background: transparent; color: {DS.TEXT_SECONDARY}; border: 1.5px solid {DS.BORDER}; border-radius: {DS.RADIUS_MD}; padding: 8px 16px;')
        if icon: btn.props(f'icon={icon}')
        return btn

    @staticmethod
    def icon_button(icon: str, on_click=None, tooltip: str = ''):
        btn = ui.button(icon=icon, on_click=on_click).props('flat round dense').style(f'color: {DS.TEXT_SECONDARY};')
        if tooltip: btn.tooltip(tooltip)
        return btn

    @staticmethod
    def breadcrumb(items: List[Dict[str, Any]]):
        with ui.row().classes('items-center gap-2'):
            for i, item in enumerate(items):
                label = ui.label(item['label']).classes('text-sm').style(f'color: {DS.TEXT_SECONDARY if i < len(items) - 1 else DS.TEXT_PRIMARY}; font-weight: {500 if i == len(items) - 1 else 400}; cursor: {"pointer" if "onClick" in item else "default"};')
                if 'onClick' in item: label.on('click', item['onClick'])
                if i < len(items) - 1: ui.icon('chevron_right', size='16px').style(f'color: {DS.TEXT_DISABLED};')

# ============================================================================
# SKELETON LOADER
# ============================================================================

class SkeletonLoader:
    @staticmethod
    def create(height: str = '100%'):
        ui.html(f'''
            <div style="width: 100%; height: {height}; background: linear-gradient(90deg, {DS.SURFACE_100} 0%, {DS.SURFACE_HOVER} 50%, {DS.SURFACE_100} 100%); background-size: 200% 100%; animation: shimmer 2s ease-in-out infinite; border-radius: {DS.RADIUS_LG};"></div>
            <style>@keyframes shimmer {{ 0% {{ background-position: -200% 0; }} 100% {{ background-position: 200% 0; }} }}</style>
        ''', sanitize=False)

# ============================================================================
# DATABASE SETUP
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
# MODELS
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
# AUTH & LOGIC
# ============================================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def autenticar_usuario(email: str, password: str) -> Optional[User]:
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email, User.password_hash == hash_password(password)).first()
    finally: db.close()

def obter_dashboards_autorizados(cliente_id: int, perfil: str) -> List[Dashboard]:
    db = SessionLocal()
    try:
        return db.query(Dashboard).join(DashboardPermissao).filter(Dashboard.cliente_id == cliente_id, DashboardPermissao.perfil == perfil).distinct().all()
    finally: db.close()

class AppState:
    def __init__(self): self.user_email: Optional[str] = None
    def login(self, user: User): self.user_email = user.email
    def logout(self): self.user_email = None
    def get_user_completo(self) -> Optional[User]:
        if not self.user_email: return None
        db = SessionLocal()
        try: return db.query(User).filter(User.email == self.user_email).first()
        finally: db.close()

# ============================================================================
# PAGES
# ============================================================================

@ui.page('/login')
def page_login():
    state = app.storage.user.get('state', AppState())
    if state.user_email: ui.navigate.to('/'); return

    with ui.column().classes('w-full h-screen items-center justify-center').style(f'background: linear-gradient(135deg, {DS.SURFACE_50} 0%, {DS.PRIMARY_LIGHT} 100%);'):
        ui.html(f'<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: radial-gradient(circle at 20px 20px, rgba(99, 102, 241, 0.03) 1px, transparent 0); background-size: 40px 40px; pointer-events: none;"></div>', sanitize=False)
        
        with ui.column().classes('w-full max-w-md px-8 relative z-10').style('gap: 32px;'):
            # Simple Branding
            with ui.column().classes('items-center gap-2'):
                ui.label('CX Data').classes('text-3xl font-bold').style(f'color: {DS.TEXT_PRIMARY};')
                ui.label('Analytics Platform').classes('text-sm').style(f'color: {DS.TEXT_TERTIARY};')
            
            # Login Card
            with ui.column().classes('w-full gap-6').style(f'background: {DS.SURFACE}; border: 1px solid {DS.BORDER_LIGHT}; border-radius: {DS.RADIUS_XL}; padding: 40px; box-shadow: {DS.SHADOW_MD};'):
                ui.label('Sign in to your workspace').classes('text-lg font-semibold').style(f'color: {DS.TEXT_PRIMARY};')
                
                email = UIComponents.input_field('Email address', icon='mail')
                senha = UIComponents.input_field('Password', password=True, icon='lock')
                erro_label = ui.label('').classes('text-sm text-red-500 hidden')
                
                def try_login():
                    user = autenticar_usuario(email.value.strip(), senha.value)
                    if user:
                        state.login(user)
                        app.storage.user['state'] = state
                        ui.navigate.to('/')
                    else:
                        erro_label.text = 'Invalid credentials.'
                        erro_label.classes(remove='hidden')
                
                UIComponents.primary_button('Sign in', on_click=try_login, full_width=True, icon='arrow_forward')
                senha.on('keydown.enter', try_login)

@ui.page('/')
def page_home():
    state = app.storage.user.get('state', AppState())
    if not state or not state.user_email: ui.navigate.to('/login'); return
    user = state.get_user_completo()
    if not user: state.logout(); ui.navigate.to('/login'); return
    
    db = SessionLocal()
    cliente = db.query(Cliente).filter(Cliente.id == user.cliente_id).first()
    dashboards = obter_dashboards_autorizados(user.cliente_id, user.perfil)
    db.close()

    with ui.row().classes('w-full h-screen').style(f'background: {DS.SURFACE_50}; margin: 0; padding: 0; font-family: {DS.FONT};'):
        
        # --- SIDEBAR LIMPA ---
        with ui.column().classes('h-screen').style(f'width: 260px; background: {DS.SURFACE}; border-right: 1px solid {DS.BORDER}; padding: 32px 24px; display: flex; flex-direction: column; gap: 40px;'):
            
            # Logo: Apenas Texto
            with ui.column().classes('gap-0'):
                ui.label('CX Data').classes('text-lg font-bold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.02em;')
            
            # Navigation: APENAS WORKSPACES (Removidos outros itens)
            with ui.column().classes('gap-4 flex-1'):
                # Item ativo
                ui.label('Workspaces').classes('text-sm font-bold cursor-pointer').style(f'color: {DS.TEXT_PRIMARY};')
            
            # User Footer
            with ui.column().classes('gap-2'):
                ui.separator()
                ui.label(cliente.nome).classes('text-sm font-bold truncate').style(f'color: {DS.TEXT_PRIMARY};')
                ui.label(user.email).classes('text-xs truncate').style(f'color: {DS.TEXT_TERTIARY};')

        # --- MAIN CONTENT ---
        with ui.column().classes('flex-1 h-screen overflow-auto').style('padding: 0;'):
            # Header Superior da Home
            with ui.row().classes('w-full items-center justify-between').style(f'padding: 24px 40px;'):
                ui.label(f'Welcome, {cliente.nome}').classes('text-xl font-semibold').style(f'color: {DS.TEXT_PRIMARY};')
                
                def logout_action(): state.logout(); app.storage.user['state'] = state; ui.navigate.to('/login')
                UIComponents.ghost_button('Sign out', on_click=logout_action, icon='logout')
            
            # Grid de Workspaces
            with LayoutComponents.page_container():
                LayoutComponents.section_header(title='Your Workspaces', badge=f'{len(dashboards)}' if dashboards else None)
                
                if dashboards:
                    # Cards Padronizados
                    with ui.grid(columns='repeat(auto-fill, minmax(340px, 1fr))').classes('w-full').style('gap: 24px;'):
                        for idx, dash in enumerate(dashboards):
                            
                            # Card Container
                            card = ui.column().classes('cursor-pointer group').style(f'''
                                background: {DS.SURFACE}; 
                                border: 1px solid {DS.BORDER}; 
                                border-radius: {DS.RADIUS_LG}; 
                                overflow: hidden; 
                                transition: all {DS.TRANSITION_FAST}; 
                                box-shadow: {DS.SHADOW_SM};
                                animation: fadeInUp 0.5s ease-out forwards; 
                                animation-delay: {idx * 0.05}s;
                                opacity: 0;
                            ''')
                            
                            with card:
                                # Standard Header
                                with ui.row().classes('items-center justify-between w-full').style(f'padding: 24px; background: {DS.SURFACE_50}; border-bottom: 1px solid {DS.BORDER_LIGHT};'):
                                    # Standard Icon Box
                                    with ui.column().classes('items-center justify-center').style(f'width: 48px; height: 48px; background: white; border: 1px solid {DS.BORDER}; border-radius: {DS.RADIUS_MD};'):
                                        ui.icon('bar_chart', size='24px').style(f'color: {DS.PRIMARY};')
                                    
                                    # Standard Badge
                                    ui.label('DASHBOARD').classes('text-xs font-bold').style(f'color: {DS.TEXT_TERTIARY}; letter-spacing: 0.05em;')
                                
                                # Body
                                with ui.column().classes('gap-2').style('padding: 24px;'):
                                    ui.label(dash.nome).classes('text-lg font-bold').style(f'color: {DS.TEXT_PRIMARY}; line-height: 1.3;')
                                    ui.label(dash.tipo.capitalize()).classes('text-sm').style(f'color: {DS.TEXT_SECONDARY};')
                                    
                                    # Seta indicativa
                                    with ui.row().classes('w-full justify-end mt-2'):
                                        ui.icon('arrow_forward', size='20px').style(f'color: {DS.PRIMARY}; opacity: 0.8;')

                            # Hover Effect
                            card.on('mouseenter', lambda e, c=card: c.style(f'border-color: {DS.PRIMARY}; transform: translateY(-2px); box-shadow: {DS.SHADOW_MD};'))
                            card.on('mouseleave', lambda e, c=card: c.style(f'border-color: {DS.BORDER}; transform: translateY(0); box-shadow: {DS.SHADOW_SM};'))
                            card.on('click', lambda d=dash: ui.navigate.to(f'/dashboard/{d.id}'))
                else:
                    LayoutComponents.empty_state(icon='analytics', title='No workspaces available', description='Dashboards assigned to you will appear here.')

@ui.page('/dashboard/{dash_id}')
def page_dashboard(dash_id: int):
    """Clean Dashboard Viewer"""
    state = app.storage.user.get('state', AppState())
    if not state or not state.user_email: ui.navigate.to('/login'); return
    user = state.get_user_completo()
    if not user: ui.navigate.to('/login'); return
    db = SessionLocal()
    dash = db.query(Dashboard).filter(Dashboard.id == dash_id).first()
    db.close()

    if not dash:
        ui.label('Dashboard not found').classes('text-xl p-8')
        return

    with ui.column().classes('w-full h-screen').style(f'background: {DS.SURFACE_50}; margin: 0; padding: 0; overflow: hidden;'):
        
        # Header Limpo
        header = ui.row().classes('w-full items-center gap-4').style(f'padding: 12px 24px; background: {DS.SURFACE}; border-bottom: 1px solid {DS.BORDER}; height: 60px; flex-shrink: 0;')
        with header:
            back_btn = ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat round dense').style(f'color: {DS.TEXT_PRIMARY};')
            ui.separator().classes('h-6').style(f'background: {DS.BORDER};')
            with ui.row().classes('items-center gap-2'):
                ui.label('Workspaces').classes('text-sm cursor-pointer').style(f'color: {DS.TEXT_SECONDARY};').on('click', lambda: ui.navigate.to('/'))
                ui.label('/').classes('text-sm').style(f'color: {DS.TEXT_DISABLED};')
                ui.label(dash.nome).classes('text-sm font-bold').style(f'color: {DS.TEXT_PRIMARY};')

        # Área do Dashboard Full
        content_area = ui.column().classes('w-full flex-grow relative').style('padding: 0; margin: 0; overflow: hidden;')
        
        with content_area:
            with ui.column().classes('w-full h-full absolute top-0 left-0 z-0 items-center justify-center').style(f'background: {DS.SURFACE};'):
                 SkeletonLoader.create('100%')
            
            ui.html(f'''
                <iframe 
                    src="{dash.link_embed}" 
                    style="
                        position: absolute; 
                        top: 0; 
                        left: 0; 
                        width: 100%; 
                        height: 100%; 
                        border: none; 
                        z-index: 10;
                        background: transparent;
                    " 
                    allowfullscreen>
                </iframe>
            ''', sanitize=False)

# ============================================================================
# INITIALIZATION
# ============================================================================

Base.metadata.create_all(bind=engine)

def inject_global_styles():
    ui.add_head_html(f'''
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: {DS.FONT}; background: {DS.SURFACE_50}; }}
            ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
            ::-webkit-scrollbar-track {{ background: transparent; }}
            ::-webkit-scrollbar-thumb {{ background: {DS.BORDER}; border-radius: 4px; }}
            @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes shimmer {{ 0% {{ background-position: -200% 0; }} 100% {{ background-position: 200% 0; }} }}
        </style>
    ''', shared=True)

if __name__ in {'__main__', '__mp_main__'}:
    inject_global_styles()
    port = int(os.environ.get('PORT', 8080))
    ui.run(title='CX Data', favicon='📊', host='0.0.0.0', port=port, storage_secret='cx_secure_key_v6', reload=False)
