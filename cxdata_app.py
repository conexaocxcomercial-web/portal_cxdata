"""
CX Data - Enterprise Analytics Platform
============================================
Versão 7.0: Enterprise Premium UI/UX
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
# DESIGN SYSTEM - ENTERPRISE PREMIUM
# ============================================================================

class DS:
    """Design System - Enterprise Grade"""
    
    # Primary Colors - Sophisticated Blue
    PRIMARY = '#0f62fe'
    PRIMARY_HOVER = '#0353e9'
    PRIMARY_ACTIVE = '#002d9c'
    PRIMARY_LIGHT = '#e8f0ff'
    PRIMARY_ULTRA_LIGHT = '#f5f9ff'
    
    # Surfaces - Neutral & Clean
    SURFACE = '#ffffff'
    SURFACE_50 = '#f8f9fa'
    SURFACE_100 = '#f1f3f5'
    SURFACE_200 = '#e9ecef'
    SURFACE_HOVER = '#f8f9fa'
    SURFACE_ELEVATED = '#ffffff'
    
    # Borders - Subtle & Refined
    BORDER = '#dee2e6'
    BORDER_LIGHT = '#e9ecef'
    BORDER_HOVER = '#adb5bd'
    BORDER_FOCUS = '#0f62fe'
    
    # Text - Clear Hierarchy
    TEXT_PRIMARY = '#212529'
    TEXT_SECONDARY = '#495057'
    TEXT_TERTIARY = '#6c757d'
    TEXT_DISABLED = '#adb5bd'
    TEXT_INVERSE = '#ffffff'
    
    # Shadows - Depth & Elevation
    SHADOW_XS = '0 1px 2px 0 rgba(0, 0, 0, 0.03)'
    SHADOW_SM = '0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px 0 rgba(0, 0, 0, 0.04)'
    SHADOW_MD = '0 4px 8px -2px rgba(0, 0, 0, 0.08), 0 2px 4px -2px rgba(0, 0, 0, 0.04)'
    SHADOW_LG = '0 12px 24px -4px rgba(0, 0, 0, 0.10), 0 4px 8px -4px rgba(0, 0, 0, 0.06)'
    SHADOW_FOCUS = '0 0 0 3px rgba(15, 98, 254, 0.12)'
    
    # Typography - Professional Sans
    FONT = '-apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    
    # Spacing
    SPACING_XS = '4px'
    SPACING_SM = '8px'
    SPACING_MD = '12px'
    SPACING_LG = '16px'
    SPACING_XL = '24px'
    SPACING_2XL = '32px'
    SPACING_3XL = '48px'
    
    # Radius - Consistent & Modern
    RADIUS_SM = '6px'
    RADIUS_MD = '8px'
    RADIUS_LG = '12px'
    RADIUS_XL = '16px'
    RADIUS_FULL = '9999px'
    
    # Transitions - Smooth & Fast
    TRANSITION_FAST = '120ms cubic-bezier(0.4, 0, 0.2, 1)'
    TRANSITION_BASE = '200ms cubic-bezier(0.4, 0, 0.2, 1)'
    TRANSITION_SLOW = '300ms cubic-bezier(0.4, 0, 0.2, 1)'

# ============================================================================
# LAYOUT COMPONENTS - ENTERPRISE
# ============================================================================

class LayoutComponents:
    @staticmethod
    def page_container(max_width: str = '1400px', padding: str = '32px'):
        return ui.column().classes('w-full').style(f'''
            padding: {padding}; 
            max-width: {max_width}; 
            margin: 0 auto;
        ''')
    
    @staticmethod
    def page_header(title: str, subtitle: Optional[str] = None):
        with ui.column().classes('w-full gap-1').style(f'margin-bottom: {DS.SPACING_2XL};'):
            ui.label(title).classes('text-2xl').style(f'''
                color: {DS.TEXT_PRIMARY}; 
                font-weight: 700; 
                letter-spacing: -0.03em; 
                line-height: 1.2;
                font-family: {DS.FONT};
            ''')
            if subtitle:
                ui.label(subtitle).classes('text-sm').style(f'''
                    color: {DS.TEXT_SECONDARY}; 
                    line-height: 1.5;
                    margin-top: 4px;
                ''')
    
    @staticmethod
    def section_header(title: str, badge: Optional[str] = None):
        with ui.row().classes('w-full items-center gap-3').style(f'margin-bottom: {DS.SPACING_LG};'):
            ui.label(title).classes('text-sm').style(f'''
                color: {DS.TEXT_PRIMARY}; 
                font-weight: 600; 
                letter-spacing: -0.01em;
            ''')
            if badge:
                ui.label(badge).classes('text-xs').style(f'''
                    color: {DS.TEXT_TERTIARY}; 
                    background: {DS.SURFACE_100}; 
                    padding: 4px 10px; 
                    border-radius: {DS.RADIUS_FULL}; 
                    font-weight: 500;
                    letter-spacing: 0;
                ''')

    @staticmethod
    def empty_state(icon: str, title: str, description: str):
        with ui.column().classes('w-full items-center justify-center').style(f'padding: {DS.SPACING_3XL} {DS.SPACING_XL};'):
            with ui.column().classes('items-center justify-center').style(f'''
                width: 56px; 
                height: 56px; 
                background: {DS.SURFACE_100}; 
                border-radius: {DS.RADIUS_LG};
                margin-bottom: {DS.SPACING_LG};
            '''):
                ui.icon(icon, size='28px').style(f'color: {DS.TEXT_DISABLED};')
            ui.label(title).classes('text-base').style(f'''
                color: {DS.TEXT_PRIMARY}; 
                font-weight: 600;
                margin-bottom: {DS.SPACING_XS};
            ''')
            ui.label(description).classes('text-sm text-center').style(f'''
                color: {DS.TEXT_SECONDARY}; 
                max-width: 360px;
                line-height: 1.5;
            ''')

# ============================================================================
# UI COMPONENTS - PREMIUM
# ============================================================================

class UIComponents:
    @staticmethod
    def input_field(label: str, password: bool = False, placeholder: str = '', icon: Optional[str] = None):
        with ui.column().classes('w-full').style(f'gap: {DS.SPACING_SM};'):
            ui.label(label).classes('text-sm').style(f'''
                color: {DS.TEXT_SECONDARY}; 
                font-weight: 500;
            ''')
            with ui.row().classes('w-full items-center relative'):
                if icon:
                    ui.icon(icon, size='18px').classes('absolute z-10').style(f'''
                        left: 14px;
                        color: {DS.TEXT_TERTIARY}; 
                        pointer-events: none;
                    ''')
                input_elem = ui.input(placeholder=placeholder, password=password).classes('w-full').props('outlined borderless').style(f'''
                    background: {DS.SURFACE}; 
                    border: 1.5px solid {DS.BORDER}; 
                    border-radius: {DS.RADIUS_MD}; 
                    padding-left: {"44px" if icon else "14px"};
                    transition: all {DS.TRANSITION_FAST};
                    height: 44px;
                    font-size: 14px;
                ''')
                input_elem.on('focus', lambda e: e.sender.style(f'''
                    border-color: {DS.BORDER_FOCUS}; 
                    box-shadow: {DS.SHADOW_FOCUS};
                '''))
                input_elem.on('blur', lambda e: e.sender.style(f'''
                    border-color: {DS.BORDER}; 
                    box-shadow: none;
                '''))
                return input_elem

    @staticmethod
    def primary_button(text: str, on_click=None, full_width: bool = False, icon: Optional[str] = None):
        btn = ui.button(text, on_click=on_click).props('no-caps flat').style(f'''
            background: {DS.PRIMARY}; 
            color: {DS.TEXT_INVERSE}; 
            border-radius: {DS.RADIUS_MD}; 
            padding: 0 20px; 
            font-weight: 600;
            font-size: 14px;
            height: 44px;
            box-shadow: {DS.SHADOW_XS};
            transition: all {DS.TRANSITION_FAST};
            {"width: 100%;" if full_width else ""}
        ''')
        if icon: btn.props(f'icon={icon}')
        btn.on('mouseenter', lambda e: e.sender.style(f'background: {DS.PRIMARY_HOVER}; box-shadow: {DS.SHADOW_SM};'))
        btn.on('mouseleave', lambda e: e.sender.style(f'background: {DS.PRIMARY}; box-shadow: {DS.SHADOW_XS};'))
        return btn

    @staticmethod
    def ghost_button(text: str, on_click=None, icon: Optional[str] = None):
        btn = ui.button(text, on_click=on_click).props('no-caps flat').style(f'''
            background: transparent; 
            color: {DS.TEXT_SECONDARY}; 
            border: 1.5px solid {DS.BORDER}; 
            border-radius: {DS.RADIUS_MD}; 
            padding: 0 16px;
            height: 36px;
            font-weight: 500;
            font-size: 13px;
            transition: all {DS.TRANSITION_FAST};
        ''')
        if icon: btn.props(f'icon={icon}')
        btn.on('mouseenter', lambda e: e.sender.style(f'background: {DS.SURFACE_HOVER}; border-color: {DS.BORDER_HOVER}; color: {DS.TEXT_PRIMARY};'))
        btn.on('mouseleave', lambda e: e.sender.style(f'background: transparent; border-color: {DS.BORDER}; color: {DS.TEXT_SECONDARY};'))
        return btn

    @staticmethod
    def icon_button(icon: str, on_click=None, tooltip: str = ''):
        btn = ui.button(icon=icon, on_click=on_click).props('flat round dense').style(f'''
            color: {DS.TEXT_SECONDARY};
            transition: all {DS.TRANSITION_FAST};
        ''')
        if tooltip: btn.tooltip(tooltip)
        btn.on('mouseenter', lambda e: e.sender.style(f'background: {DS.SURFACE_HOVER}; color: {DS.TEXT_PRIMARY};'))
        btn.on('mouseleave', lambda e: e.sender.style(f'background: transparent; color: {DS.TEXT_SECONDARY};'))
        return btn

# ============================================================================
# SKELETON LOADER - REFINED
# ============================================================================

class SkeletonLoader:
    @staticmethod
    def create(height: str = '100%'):
        ui.html(f'''
            <div style="
                width: 100%; 
                height: {height}; 
                background: linear-gradient(90deg, {DS.SURFACE_100} 0%, {DS.SURFACE_200} 50%, {DS.SURFACE_100} 100%); 
                background-size: 200% 100%; 
                animation: shimmer 1.8s ease-in-out infinite; 
                border-radius: {DS.RADIUS_LG};
            "></div>
            <style>
                @keyframes shimmer {{ 
                    0% {{ background-position: -200% 0; }} 
                    100% {{ background-position: 200% 0; }} 
                }}
            </style>
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

    with ui.column().classes('w-full h-screen items-center justify-center').style(f'''
        background: linear-gradient(135deg, {DS.SURFACE_50} 0%, {DS.PRIMARY_ULTRA_LIGHT} 100%);
    '''):
        # Subtle grid pattern
        ui.html(f'''
            <div style="
                position: absolute; 
                top: 0; 
                left: 0; 
                right: 0; 
                bottom: 0; 
                background-image: 
                    linear-gradient(to right, {DS.BORDER_LIGHT} 1px, transparent 1px),
                    linear-gradient(to bottom, {DS.BORDER_LIGHT} 1px, transparent 1px);
                background-size: 32px 32px; 
                pointer-events: none;
                opacity: 0.4;
            "></div>
        ''', sanitize=False)
        
        with ui.column().classes('w-full max-w-md px-8 relative z-10').style(f'gap: {DS.SPACING_2XL};'):
            # Branding
            with ui.column().classes('items-center').style(f'gap: {DS.SPACING_MD};'):
                with ui.column().classes('items-center justify-center').style(f'''
                    width: 48px; 
                    height: 48px; 
                    background: {DS.PRIMARY}; 
                    border-radius: {DS.RADIUS_LG};
                    box-shadow: {DS.SHADOW_MD};
                '''):
                    ui.icon('analytics', size='24px', color='white')
                ui.label('CX Data').classes('text-2xl').style(f'''
                    color: {DS.TEXT_PRIMARY}; 
                    font-weight: 700;
                    letter-spacing: -0.02em;
                ''')
                ui.label('Analytics Platform').classes('text-xs').style(f'''
                    color: {DS.TEXT_TERTIARY}; 
                    font-weight: 500;
                    letter-spacing: 0.05em;
                    text-transform: uppercase;
                ''')
            
            # Login Card
            with ui.column().classes('w-full').style(f'''
                gap: {DS.SPACING_XL};
                background: {DS.SURFACE_ELEVATED}; 
                border: 1px solid {DS.BORDER_LIGHT}; 
                border-radius: {DS.RADIUS_XL}; 
                padding: {DS.SPACING_3XL}; 
                box-shadow: {DS.SHADOW_LG};
            '''):
                ui.label('Acesse sua conta').classes('text-lg').style(f'''
                    color: {DS.TEXT_PRIMARY}; 
                    font-weight: 600;
                    letter-spacing: -0.01em;
                ''')
                
                email = UIComponents.input_field('Email', icon='mail', placeholder='seu@email.com')
                senha = UIComponents.input_field('Senha', password=True, icon='lock', placeholder='••••••••')
                
                erro_label = ui.label('').classes('text-sm hidden').style(f'color: #dc2626;')
                
                def try_login():
                    user = autenticar_usuario(email.value.strip(), senha.value)
                    if user:
                        state.login(user)
                        app.storage.user['state'] = state
                        ui.navigate.to('/')
                    else:
                        erro_label.text = 'Credenciais inválidas. Verifique e tente novamente.'
                        erro_label.classes(remove='hidden')
                
                UIComponents.primary_button('Acessar plataforma', on_click=try_login, full_width=True, icon='arrow_forward')
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

    with ui.row().classes('w-full h-screen').style(f'''
        background: {DS.SURFACE_50}; 
        margin: 0; 
        padding: 0; 
        font-family: {DS.FONT};
    '''):
        
        # --- SIDEBAR ULTRA-MINIMALISTA PREMIUM ---
        with ui.column().classes('h-screen').style(f'''
            width: 280px; 
            background: {DS.SURFACE}; 
            border-right: 1px solid {DS.BORDER}; 
            padding: {DS.SPACING_2XL} {DS.SPACING_XL}; 
            display: flex; 
            flex-direction: column; 
            gap: {DS.SPACING_3XL};
        '''):
            
            # Branding Premium
            with ui.row().classes('items-center').style(f'gap: {DS.SPACING_MD}; padding: 0 {DS.SPACING_SM};'):
                with ui.column().classes('items-center justify-center').style(f'''
                    width: 36px; 
                    height: 36px; 
                    background: linear-gradient(135deg, {DS.PRIMARY} 0%, {DS.PRIMARY_HOVER} 100%); 
                    border-radius: {DS.RADIUS_MD};
                    box-shadow: {DS.SHADOW_SM};
                '''):
                    ui.icon('analytics', size='20px', color='white')
                ui.label('CX Data').classes('text-base').style(f'''
                    color: {DS.TEXT_PRIMARY}; 
                    font-weight: 700; 
                    letter-spacing: -0.02em;
                ''')
            
            # Spacer - Empurra footer para baixo
            ui.element('div').classes('flex-1')

            # User Profile Card Premium
            with ui.column().classes('w-full').style(f'gap: {DS.SPACING_LG};'):
                ui.separator().style(f'background: {DS.BORDER}; opacity: 0.6;')
                
                with ui.row().classes('items-center w-full cursor-pointer').style(f'''
                    gap: {DS.SPACING_MD}; 
                    padding: {DS.SPACING_MD}; 
                    border-radius: {DS.RADIUS_MD}; 
                    transition: background {DS.TRANSITION_FAST};
                '''):
                    # Avatar com iniciais
                    iniciais = ''.join([palavra[0].upper() for palavra in cliente.nome.split()[:2]])
                    with ui.column().classes('items-center justify-center').style(f'''
                        width: 40px; 
                        height: 40px; 
                        background: linear-gradient(135deg, {DS.PRIMARY_LIGHT} 0%, {DS.PRIMARY_ULTRA_LIGHT} 100%); 
                        border: 1.5px solid {DS.BORDER}; 
                        border-radius: {DS.RADIUS_FULL}; 
                        color: {DS.PRIMARY}; 
                        font-size: 13px; 
                        font-weight: 700;
                        flex-shrink: 0;
                    '''):
                        ui.label(iniciais)
                    
                    # Info do usuário
                    with ui.column().classes('flex-1 overflow-hidden').style(f'gap: {DS.SPACING_XS};'):
                        ui.label(cliente.nome).classes('text-sm truncate').style(f'''
                            color: {DS.TEXT_PRIMARY}; 
                            font-weight: 600;
                            line-height: 1.3;
                        ''')
                        ui.label(user.email).classes('text-xs truncate').style(f'''
                            color: {DS.TEXT_TERTIARY}; 
                            line-height: 1.2;
                        ''')
                    
                    # Settings icon
                    ui.icon('settings', size='18px').style(f'''
                        color: {DS.TEXT_DISABLED};
                        flex-shrink: 0;
                    ''')

        # --- MAIN CONTENT ---
        with ui.column().classes('flex-1 h-screen overflow-auto').style(f'''
            padding: 0; 
            background: {DS.SURFACE_50};
        '''):
            # Header Premium
            with ui.row().classes('w-full items-center justify-between').style(f'''
                padding: {DS.SPACING_XL} {DS.SPACING_3XL}; 
                border-bottom: 1px solid {DS.BORDER};
                background: {DS.SURFACE};
            '''):
                with ui.column().style(f'gap: {DS.SPACING_XS};'):
                    ui.label('Seus Workspaces').classes('text-xl').style(f'''
                        color: {DS.TEXT_PRIMARY}; 
                        font-weight: 700; 
                        letter-spacing: -0.02em;
                    ''')
                    ui.label(f'Bem-vindo de volta, {cliente.nome.split()[0]}').classes('text-sm').style(f'''
                        color: {DS.TEXT_SECONDARY};
                    ''')
                
                def logout_action(): 
                    state.logout()
                    app.storage.user['state'] = state
                    ui.navigate.to('/login')
                UIComponents.ghost_button('Sair', on_click=logout_action, icon='logout')
            
            # Workspace Grid
            with LayoutComponents.page_container():
                if dashboards:
                    # Section Header
                    with ui.row().classes('w-full items-center justify-between').style(f'margin-bottom: {DS.SPACING_XL};'):
                        ui.label('Todos os workspaces').classes('text-sm').style(f'''
                            color: {DS.TEXT_PRIMARY}; 
                            font-weight: 600;
                        ''')
                        ui.label(f'{len(dashboards)} {"workspace" if len(dashboards) == 1 else "workspaces"}').classes('text-xs').style(f'''
                            color: {DS.TEXT_TERTIARY}; 
                            background: {DS.SURFACE_100}; 
                            padding: 4px 12px; 
                            border-radius: {DS.RADIUS_FULL};
                            font-weight: 500;
                        ''')

                    # Cards Grid
                    with ui.grid(columns='repeat(auto-fill, minmax(340px, 1fr))').classes('w-full').style(f'gap: {DS.SPACING_XL};'):
                        for idx, dash in enumerate(dashboards):
                            card = ui.column().classes('cursor-pointer').style(f'''
                                background: {DS.SURFACE_ELEVATED}; 
                                border: 1px solid {DS.BORDER}; 
                                border-radius: {DS.RADIUS_LG}; 
                                overflow: hidden; 
                                transition: all {DS.TRANSITION_BASE}; 
                                box-shadow: {DS.SHADOW_SM};
                                animation: fadeInUp 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards; 
                                animation-delay: {idx * 0.04}s; 
                                opacity: 0;
                            ''')
                            
                            with card:
                                # Card Header
                                with ui.row().classes('items-start justify-between w-full').style(f'padding: {DS.SPACING_XL};'):
                                    # Icon
                                    with ui.column().classes('items-center justify-center').style(f'''
                                        width: 44px; 
                                        height: 44px; 
                                        background: {DS.PRIMARY_ULTRA_LIGHT}; 
                                        border: 1px solid {DS.BORDER_LIGHT}; 
                                        border-radius: {DS.RADIUS_MD};
                                    '''):
                                        ui.icon('bar_chart', size='22px').style(f'color: {DS.PRIMARY};')
                                    
                                    # Menu icon
                                    ui.icon('more_horiz', size='20px').style(f'''
                                        color: {DS.TEXT_DISABLED};
                                        transition: color {DS.TRANSITION_FAST};
                                    ''')
                                
                                # Card Content
                                with ui.column().style(f'''
                                    gap: {DS.SPACING_SM}; 
                                    padding: 0 {DS.SPACING_XL} {DS.SPACING_XL} {DS.SPACING_XL};
                                '''):
                                    ui.label(dash.nome).classes('text-base').style(f'''
                                        color: {DS.TEXT_PRIMARY}; 
                                        font-weight: 600; 
                                        line-height: 1.4;
                                        letter-spacing: -0.01em;
                                    ''')
                                    ui.label(f'{dash.tipo.capitalize()} · Dashboard').classes('text-xs').style(f'''
                                        color: {DS.TEXT_TERTIARY};
                                        font-weight: 500;
                                    ''')
                                
                                # Card Footer
                                with ui.row().classes('w-full items-center justify-between').style(f'''
                                    padding: {DS.SPACING_MD} {DS.SPACING_XL}; 
                                    background: {DS.SURFACE_50}; 
                                    border-top: 1px solid {DS.BORDER_LIGHT};
                                '''):
                                    ui.label('Abrir workspace').classes('text-xs').style(f'''
                                        color: {DS.PRIMARY}; 
                                        font-weight: 600;
                                    ''')
                                    ui.icon('arrow_forward', size='16px').style(f'color: {DS.PRIMARY};')
                            
                            # Card Interactions
                            card.on('mouseenter', lambda e, c=card: c.style(f'''
                                border-color: {DS.BORDER_HOVER}; 
                                transform: translateY(-2px); 
                                box-shadow: {DS.SHADOW_MD};
                            '''))
                            card.on('mouseleave', lambda e, c=card: c.style(f'''
                                border-color: {DS.BORDER}; 
                                transform: translateY(0); 
                                box-shadow: {DS.SHADOW_SM};
                            '''))
                            card.on('click', lambda d=dash: ui.navigate.to(f'/dashboard/{d.id}'))
                else:
                    LayoutComponents.empty_state(
                        icon='analytics', 
                        title='Nenhum workspace disponível', 
                        description='Você ainda não tem workspaces atribuídos. Entre em contato com seu administrador.'
                    )

@ui.page('/dashboard/{dash_id}')
def page_dashboard(dash_id: int):
    state = app.storage.user.get('state', AppState())
    if not state or not state.user_email: ui.navigate.to('/login'); return
    user = state.get_user_completo()
    if not user: ui.navigate.to('/login'); return
    
    db = SessionLocal()
    dash = db.query(Dashboard).filter(Dashboard.id == dash_id).first()
    db.close()

    if not dash:
        with ui.column().classes('w-full h-screen items-center justify-center'):
            LayoutComponents.empty_state(
                icon='error_outline', 
                title='Workspace não encontrado', 
                description='O workspace solicitado não existe ou você não tem permissão para acessá-lo.'
            )
        return

    with ui.column().classes('w-full h-screen').style(f'''
        background: {DS.SURFACE_50}; 
        margin: 0; 
        padding: 0; 
        overflow: hidden;
    '''):
        # Header Premium
        with ui.row().classes('w-full items-center').style(f'''
            padding: {DS.SPACING_LG} {DS.SPACING_XL}; 
            background: {DS.SURFACE}; 
            border-bottom: 1px solid {DS.BORDER}; 
            height: 64px; 
            flex-shrink: 0;
            gap: {DS.SPACING_LG};
        '''):
            # Back button
            back_btn = ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/')).props('flat round dense').style(f'''
                color: {DS.TEXT_SECONDARY};
                transition: all {DS.TRANSITION_FAST};
            ''')
            back_btn.on('mouseenter', lambda e: e.sender.style(f'background: {DS.SURFACE_HOVER}; color: {DS.TEXT_PRIMARY};'))
            back_btn.on('mouseleave', lambda e: e.sender.style(f'background: transparent; color: {DS.TEXT_SECONDARY};'))
            
            # Separator
            ui.separator().classes('h-6').style(f'background: {DS.BORDER}; opacity: 0.6;')
            
            # Breadcrumb
            with ui.row().classes('items-center').style(f'gap: {DS.SPACING_SM};'):
                home_link = ui.label('Workspaces').classes('text-sm cursor-pointer').style(f'''
                    color: {DS.TEXT_SECONDARY}; 
                    font-weight: 500;
                    transition: color {DS.TRANSITION_FAST};
                ''')
                home_link.on('click', lambda: ui.navigate.to('/'))
                home_link.on('mouseenter', lambda e: e.sender.style(f'color: {DS.TEXT_PRIMARY};'))
                home_link.on('mouseleave', lambda e: e.sender.style(f'color: {DS.TEXT_SECONDARY};'))
                
                ui.icon('chevron_right', size='16px').style(f'color: {DS.TEXT_DISABLED};')
                
                ui.label(dash.nome).classes('text-sm').style(f'''
                    color: {DS.TEXT_PRIMARY}; 
                    font-weight: 600;
                ''')

        # Embed Container Premium
        content_area = ui.column().classes('w-full flex-grow relative').style('padding: 0; margin: 0; overflow: hidden;')
        with content_area:
            # Loading Skeleton
            with ui.column().classes('w-full h-full absolute top-0 left-0 z-0 items-center justify-center').style(f'''
                background: {DS.SURFACE};
                padding: {DS.SPACING_2XL};
            '''):
                with ui.column().classes('w-full h-full').style(f'''
                    max-width: 1400px;
                    margin: 0 auto;
                '''):
                    SkeletonLoader.create('100%')
            
            # Embed with Premium Wrapper
            ui.html(f'''
                <div style="
                    position: absolute; 
                    top: {DS.SPACING_XL}; 
                    left: {DS.SPACING_XL}; 
                    right: {DS.SPACING_XL}; 
                    bottom: {DS.SPACING_XL}; 
                    z-index: 10;
                    background: {DS.SURFACE_ELEVATED};
                    border-radius: {DS.RADIUS_LG};
                    border: 1px solid {DS.BORDER};
                    box-shadow: {DS.SHADOW_MD};
                    overflow: hidden;
                ">
                    <iframe 
                        src="{dash.link_embed}" 
                        style="
                            width: 100%; 
                            height: 100%; 
                            border: none; 
                            background: transparent;
                        " 
                        allowfullscreen>
                    </iframe>
                </div>
            ''', sanitize=False)

# ============================================================================
# INITIALIZATION
# ============================================================================

Base.metadata.create_all(bind=engine)

def inject_global_styles():
    ui.add_head_html(f'''
        <style>
            /* Global Reset */
            * {{ 
                margin: 0; 
                padding: 0; 
                box-sizing: border-box; 
            }}
            
            /* Body */
            body {{ 
                font-family: {DS.FONT}; 
                background: {DS.SURFACE_50}; 
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }}
            
            /* Scrollbar */
            ::-webkit-scrollbar {{ 
                width: 8px; 
                height: 8px; 
            }}
            ::-webkit-scrollbar-track {{ 
                background: transparent; 
            }}
            ::-webkit-scrollbar-thumb {{ 
                background: {DS.BORDER}; 
                border-radius: {DS.RADIUS_SM}; 
            }}
            ::-webkit-scrollbar-thumb:hover {{ 
                background: {DS.BORDER_HOVER}; 
            }}
            
            /* Animations */
            @keyframes fadeInUp {{ 
                from {{ 
                    opacity: 0; 
                    transform: translateY(12px); 
                }} 
                to {{ 
                    opacity: 1; 
                    transform: translateY(0); 
                }} 
            }}
            
            @keyframes shimmer {{ 
                0% {{ 
                    background-position: -200% 0; 
                }} 
                100% {{ 
                    background-position: 200% 0; 
                }} 
            }}
        </style>
    ''', shared=True)

if __name__ in {'__main__', '__mp_main__'}:
    inject_global_styles()
    port = int(os.environ.get('PORT', 8080))
    ui.run(
        title='CX Data', 
        favicon='📊', 
        host='0.0.0.0', 
        port=port, 
        storage_secret='cx_secure_key_v7', 
        reload=False
    )
