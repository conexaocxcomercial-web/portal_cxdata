"""
CX Data - Enterprise Analytics Platform
============================================
Product-grade B2B SaaS Dashboard Portal
Fix 4.0: Separação de HTML e JS para corrigir erro "HTML elements must not contain <script>"
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
    PRIMARY = '#6366f1'
    PRIMARY_HOVER = '#4f46e5'
    PRIMARY_LIGHT = '#eef2ff'
    PRIMARY_BORDER = '#c7d2fe'
    SURFACE = '#ffffff'
    SURFACE_50 = '#fafbfc'
    SURFACE_100 = '#f7f8fa'
    SURFACE_HOVER = '#f3f4f6'
    BORDER = '#e5e7eb'
    BORDER_LIGHT = '#f3f4f6'
    BORDER_DARK = '#d1d5db'
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
    
    SHADOW_XS = '0 1px 2px 0 rgb(0 0 0 / 0.05)'
    SHADOW_SM = '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)'
    SHADOW_MD = '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)'
    SHADOW_LG = '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)'
    SHADOW_XL = '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)'
    
    FONT = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
    
    RADIUS_SM = '6px'
    RADIUS_MD = '8px'
    RADIUS_LG = '12px'
    RADIUS_XL = '16px'
    
    TRANSITION_FAST = '150ms cubic-bezier(0.4, 0, 0.2, 1)'
    TRANSITION_BASE = '200ms cubic-bezier(0.4, 0, 0.2, 1)'
    TRANSITION_SLOW = '300ms cubic-bezier(0.4, 0, 0.2, 1)'

# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

class LayoutComponents:
    @staticmethod
    def page_container(max_width: str = '1600px', padding: str = '40px'):
        return ui.column().classes('w-full').style(f'padding: {padding}; max-width: {max_width}; margin: 0 auto;')
    
    @staticmethod
    def page_header(title: str, subtitle: Optional[str] = None, actions: Optional[Callable] = None):
        with ui.column().classes('w-full gap-4 mb-8'):
            with ui.column().classes('gap-2'):
                ui.label(title).classes('text-3xl font-bold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.03em; font-family: {DS.FONT};')
                if subtitle: ui.label(subtitle).classes('text-base').style(f'color: {DS.TEXT_SECONDARY}; line-height: 1.6;')
            if actions:
                with ui.row().classes('items-center gap-3 mt-2'): actions()
    
    @staticmethod
    def section_header(title: str, subtitle: Optional[str] = None, badge: Optional[str] = None):
        with ui.row().classes('w-full items-center justify-between mb-6'):
            with ui.column().classes('gap-1'):
                with ui.row().classes('items-center gap-3'):
                    ui.label(title).classes('text-xl font-semibold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.02em;')
                    if badge: ui.label(badge).classes('text-xs font-semibold').style(f'color: {DS.PRIMARY}; background: {DS.PRIMARY_LIGHT}; padding: 4px 10px; border-radius: {DS.RADIUS_SM}; letter-spacing: 0.05em;')
                if subtitle: ui.label(subtitle).classes('text-sm').style(f'color: {DS.TEXT_TERTIARY}; line-height: 1.5;')
    
    @staticmethod
    def empty_state(icon: str, title: str, description: str, cta_text: Optional[str] = None, cta_action: Optional[Callable] = None):
        with ui.column().classes('w-full items-center justify-center').style('padding: 80px 20px;'):
            with ui.column().classes('items-center gap-6 max-w-md text-center'):
                with ui.column().classes('items-center justify-center').style(f'width: 80px; height: 80px; background: {DS.SURFACE_100}; border-radius: {DS.RADIUS_XL}; border: 1px solid {DS.BORDER};'):
                    ui.icon(icon, size='40px').style(f'color: {DS.TEXT_DISABLED};')
                with ui.column().classes('gap-3'):
                    ui.label(title).classes('text-xl font-semibold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.02em;')
                    ui.label(description).classes('text-base').style(f'color: {DS.TEXT_SECONDARY}; line-height: 1.6;')
                if cta_text and cta_action:
                    UIComponents.primary_button(cta_text, on_click=cta_action)

# ============================================================================
# UI COMPONENTS
# ============================================================================

class UIComponents:
    @staticmethod
    def input_field(label: str, password: bool = False, placeholder: str = '', icon: Optional[str] = None):
        with ui.column().classes('w-full gap-2'):
            ui.label(label).classes('text-sm font-medium').style(f'color: {DS.TEXT_SECONDARY}; letter-spacing: -0.01em;')
            with ui.row().classes('w-full items-center relative'):
                if icon: ui.icon(icon, size='20px').classes('absolute left-3 z-10').style(f'color: {DS.TEXT_TERTIARY}; pointer-events: none;')
                input_field = ui.input(placeholder=placeholder, password=password).classes('w-full').props('outlined borderless').style(f'background: {DS.SURFACE}; border: 1.5px solid {DS.BORDER}; border-radius: {DS.RADIUS_MD}; font-size: 15px; font-family: {DS.FONT}; color: {DS.TEXT_PRIMARY}; transition: all {DS.TRANSITION_FAST}; padding-left: {"40px" if icon else "16px"};')
                input_field.on('focus', lambda: input_field.style(f'border-color: {DS.PRIMARY}; box-shadow: 0 0 0 3px {DS.PRIMARY_LIGHT};'))
                input_field.on('blur', lambda: input_field.style(f'border-color: {DS.BORDER}; box-shadow: none;'))
                return input_field
    
    @staticmethod
    def primary_button(text: str, on_click=None, full_width: bool = False, icon: Optional[str] = None):
        button = ui.button(text, on_click=on_click).props('no-caps flat').style(f'background: {DS.PRIMARY}; color: white; border-radius: {DS.RADIUS_MD}; padding: 11px 24px; font-size: 15px; font-weight: 600; font-family: {DS.FONT}; letter-spacing: -0.01em; border: none; box-shadow: {DS.SHADOW_SM}; transition: all {DS.TRANSITION_FAST}; cursor: pointer; {"width: 100%;" if full_width else ""}')
        if icon: button.props(f'icon={icon}')
        button.on('mouseenter', lambda: button.style(f'background: {DS.PRIMARY_HOVER}; box-shadow: {DS.SHADOW_MD}; transform: translateY(-1px);'))
        button.on('mouseleave', lambda: button.style(f'background: {DS.PRIMARY}; box-shadow: {DS.SHADOW_SM}; transform: translateY(0);'))
        button.on('mousedown', lambda: button.style('transform: translateY(0) scale(0.98);'))
        button.on('mouseup', lambda: button.style('transform: translateY(-1px) scale(1);'))
        return button
    
    @staticmethod
    def ghost_button(text: str, on_click=None, icon: Optional[str] = None):
        button = ui.button(text, on_click=on_click).props('no-caps flat').style(f'background: transparent; color: {DS.TEXT_SECONDARY}; border: 1.5px solid {DS.BORDER}; border-radius: {DS.RADIUS_MD}; padding: 8px 16px; font-size: 14px; font-weight: 500; font-family: {DS.FONT}; transition: all {DS.TRANSITION_FAST}; cursor: pointer;')
        if icon: button.props(f'icon={icon}')
        button.on('mouseenter', lambda: button.style(f'background: {DS.SURFACE_HOVER}; border-color: {DS.BORDER_DARK};'))
        button.on('mouseleave', lambda: button.style(f'background: transparent; border-color: {DS.BORDER};'))
        return button
    
    @staticmethod
    def icon_button(icon: str, on_click=None, tooltip: str = ''):
        button = ui.button(icon=icon, on_click=on_click).props('flat round dense').style(f'background: transparent; color: {DS.TEXT_SECONDARY}; border: none; min-width: 36px; padding: 8px; transition: all {DS.TRANSITION_FAST};')
        if tooltip: button.tooltip(tooltip)
        button.on('mouseenter', lambda: button.style(f'background: {DS.SURFACE_HOVER}; color: {DS.TEXT_PRIMARY};'))
        button.on('mouseleave', lambda: button.style(f'background: transparent; color: {DS.TEXT_SECONDARY};'))
        return button
    
    @staticmethod
    def status_badge(text: str, status_type: str = 'success'):
        colors = {'success': {'bg': DS.SUCCESS_BG, 'text': DS.SUCCESS}, 'warning': {'bg': DS.WARNING_BG, 'text': DS.WARNING}, 'error': {'bg': DS.ERROR_BG, 'text': DS.ERROR}, 'info': {'bg': DS.INFO_BG, 'text': DS.INFO}}
        color = colors.get(status_type, colors['success'])
        with ui.row().classes('items-center gap-2 px-3 py-1.5').style(f'background: {color["bg"]}; border-radius: {DS.RADIUS_MD};'):
            ui.icon('check_circle', size='16px').style(f'color: {color["text"]};')
            ui.label(text).classes('text-xs font-semibold').style(f'color: {color["text"]}; letter-spacing: 0.02em;')
    
    @staticmethod
    def breadcrumb(items: List[Dict[str, Any]]):
        with ui.row().classes('items-center gap-2 mb-4'):
            for i, item in enumerate(items):
                label = ui.label(item['label']).classes('text-sm').style(f'color: {DS.TEXT_SECONDARY if i < len(items) - 1 else DS.TEXT_PRIMARY}; font-weight: {500 if i == len(items) - 1 else 400}; cursor: {"pointer" if "onClick" in item else "default"}; transition: color {DS.TRANSITION_FAST};')
                if 'onClick' in item:
                    label.on('click', item['onClick'])
                    label.on('mouseenter', lambda e: e.sender.style(f'color: {DS.PRIMARY};'))
                    label.on('mouseleave', lambda e, idx=i: e.sender.style(f'color: {DS.TEXT_SECONDARY if idx < len(items) - 1 else DS.TEXT_PRIMARY};'))
                if i < len(items) - 1: ui.icon('chevron_right', size='16px').style(f'color: {DS.TEXT_DISABLED};')

# ============================================================================
# SKELETON LOADER
# ============================================================================

class SkeletonLoader:
    @staticmethod
    def create(height: str = '400px'):
        ui.html(f'''
            <div style="width: 100%; height: {height}; background: linear-gradient(90deg, {DS.SURFACE_100} 0%, {DS.SURFACE_HOVER} 50%, {DS.SURFACE_100} 100%); background-size: 200% 100%; animation: shimmer 2s ease-in-out infinite; border-radius: {DS.RADIUS_LG};"></div>
            <style>@keyframes shimmer {{ 0% {{ background-position: -200% 0; }} 100% {{ background-position: 200% 0; }} }}</style>
        ''', sanitize=False)

# ============================================================================
# DATABASE
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
# BUSINESS LOGIC
# ============================================================================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def autenticar_usuario(email: str, password: str) -> Optional[User]:
    db = SessionLocal()
    try:
        password_hash = hash_password(password)
        return db.query(User).filter(User.email == email, User.password_hash == password_hash).first()
    finally: db.close()

def obter_dashboards_autorizados(cliente_id: int, perfil: str) -> List[Dashboard]:
    db = SessionLocal()
    try:
        return db.query(Dashboard).join(DashboardPermissao).filter(Dashboard.cliente_id == cliente_id, DashboardPermissao.perfil == perfil).distinct().all()
    finally: db.close()

# ============================================================================
# APP STATE
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
        try: return db.query(User).filter(User.email == self.user_email).first()
        finally: db.close()

# ============================================================================
# PAGES
# ============================================================================

@ui.page('/login')
def page_login():
    """Enterprise Login Experience"""
    state = app.storage.user.get('state', AppState())
    if state.user_email: ui.navigate.to('/'); return

    with ui.column().classes('w-full h-screen items-center justify-center').style(f'background: linear-gradient(135deg, {DS.SURFACE_50} 0%, {DS.PRIMARY_LIGHT} 100%); position: relative; overflow: hidden;'):
        ui.html(f'<div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-image: radial-gradient(circle at 20px 20px, rgba(99, 102, 241, 0.03) 1px, transparent 0); background-size: 40px 40px; pointer-events: none;"></div>', sanitize=False)
        
        with ui.column().classes('w-full max-w-md px-8 relative z-10').style('gap: 48px;'):
            with ui.column().classes('items-center gap-4'):
                with ui.column().classes('items-center justify-center').style(f'width: 56px; height: 56px; background: linear-gradient(135deg, {DS.PRIMARY} 0%, {DS.PRIMARY_HOVER} 100%); border-radius: {DS.RADIUS_LG}; box-shadow: {DS.SHADOW_LG};'):
                    ui.icon('analytics', size='32px', color='white')
                ui.label('CX Data').classes('text-3xl font-bold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.03em; font-family: {DS.FONT};')
                ui.label('Enterprise Analytics Platform').classes('text-sm font-medium').style(f'color: {DS.TEXT_TERTIARY}; letter-spacing: 0.01em;')
            
            with ui.column().classes('w-full gap-6').style(f'background: {DS.SURFACE}; border: 1px solid {DS.BORDER_LIGHT}; border-radius: {DS.RADIUS_XL}; padding: 40px; box-shadow: {DS.SHADOW_XL}; backdrop-filter: blur(10px);'):
                with ui.column().classes('gap-2 mb-2'):
                    ui.label('Welcome back').classes('text-xl font-semibold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.02em;')
                    ui.label('Sign in to your workspace').classes('text-sm').style(f'color: {DS.TEXT_SECONDARY};')
                
                email = UIComponents.input_field('Email address', icon='mail', placeholder='you@company.com')
                senha = UIComponents.input_field('Password', password=True, icon='lock', placeholder='Enter your password')
                erro_container = ui.row().classes('w-full items-center gap-2 hidden').style(f'background: {DS.ERROR_BG}; border: 1px solid {DS.ERROR}; border-radius: {DS.RADIUS_MD}; padding: 12px 16px;')
                with erro_container:
                    ui.icon('error', size='20px').style(f'color: {DS.ERROR};')
                    erro_label = ui.label('').classes('text-sm font-medium').style(f'color: {DS.ERROR};')
                
                loading_state = {'is_loading': False}
                def try_login():
                    if loading_state['is_loading']: return
                    if not email.value.strip() or not senha.value:
                        erro_label.text = 'Please fill in all fields'
                        erro_container.classes(remove='hidden')
                        ui.timer(3, lambda: erro_container.classes(add='hidden'), once=True)
                        return
                    loading_state['is_loading'] = True
                    login_btn.set_text('Signing in...')
                    login_btn.props('disable')
                    def finish_login():
                        user = autenticar_usuario(email.value.strip(), senha.value)
                        if user:
                            state.login(user) 
                            app.storage.user['state'] = state
                            ui.navigate.to('/')
                        else:
                            erro_label.text = 'Invalid credentials. Please try again.'
                            erro_container.classes(remove='hidden')
                            login_btn.set_text('Sign in')
                            login_btn.props(remove='disable')
                            loading_state['is_loading'] = False
                            ui.timer(3, lambda: erro_container.classes(add='hidden'), once=True)
                    ui.timer(0.4, finish_login, once=True)
                
                login_btn = UIComponents.primary_button('Sign in', on_click=try_login, full_width=True, icon='arrow_forward')
                senha.on('keydown.enter', try_login)
                with ui.row().classes('w-full justify-center mt-2'):
                    forgot_link = ui.label('Forgot your password?').classes('text-sm cursor-pointer').style(f'color: {DS.TEXT_TERTIARY}; transition: color {DS.TRANSITION_FAST};')
                    forgot_link.on('mouseenter', lambda e: e.sender.style(f'color: {DS.PRIMARY};'))
                    forgot_link.on('mouseleave', lambda e: e.sender.style(f'color: {DS.TEXT_TERTIARY};'))
            
            with ui.row().classes('w-full justify-center gap-1'): ui.label('© 2024 CX Data. All rights reserved.').classes('text-xs').style(f'color: {DS.TEXT_DISABLED};')

@ui.page('/')
def page_home():
    """Enterprise Dashboard Hub"""
    state = app.storage.user.get('state', AppState())
    if not state or not state.user_email: ui.navigate.to('/login'); return
    user = state.get_user_completo()
    if not user: state.logout(); ui.navigate.to('/login'); return
    db = SessionLocal()
    cliente = db.query(Cliente).filter(Cliente.id == user.cliente_id).first()
    dashboards = obter_dashboards_autorizados(user.cliente_id, user.perfil)
    db.close()

    with ui.row().classes('w-full h-screen').style(f'background: {DS.SURFACE_50}; margin: 0; padding: 0; font-family: {DS.FONT};'):
        with ui.column().classes('h-screen').style(f'width: 260px; background: {DS.SURFACE}; border-right: 1px solid {DS.BORDER}; padding: 24px 16px; display: flex; flex-direction: column; gap: 32px;'):
            with ui.row().classes('items-center gap-3 px-3'):
                with ui.column().classes('items-center justify-center').style(f'width: 36px; height: 36px; background: linear-gradient(135deg, {DS.PRIMARY} 0%, {DS.PRIMARY_HOVER} 100%); border-radius: {DS.RADIUS_MD}; box-shadow: {DS.SHADOW_SM};'):
                    ui.icon('analytics', size='20px', color='white')
                with ui.column().classes('gap-0'):
                    ui.label('CX Data').classes('text-base font-semibold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.01em;')
                    ui.label('Analytics').classes('text-xs font-medium').style(f'color: {DS.TEXT_TERTIARY};')
            with ui.column().classes('gap-1 flex-1'):
                with ui.row().classes('items-center gap-3 px-3 py-2.5 cursor-pointer').style(f'background: {DS.PRIMARY_LIGHT}; border-radius: {DS.RADIUS_MD};'):
                    ui.icon('dashboard', size='20px').style(f'color: {DS.PRIMARY};')
                    ui.label('Workspaces').classes('text-sm font-medium').style(f'color: {DS.PRIMARY};')
            with ui.column().classes('gap-3'):
                ui.separator().style(f'background: {DS.BORDER_LIGHT};')
                with ui.row().classes('items-center gap-3 px-3 py-2').style(f'background: {DS.SURFACE_100}; border-radius: {DS.RADIUS_MD};'):
                    iniciais = ''.join([palavra[0].upper() for palavra in cliente.nome.split()[:2]])
                    with ui.column().classes('items-center justify-center').style(f'width: 36px; height: 36px; background: linear-gradient(135deg, {DS.PRIMARY} 0%, {DS.PRIMARY_HOVER} 100%); border-radius: {DS.RADIUS_MD}; color: white; font-weight: 600;'): ui.label(iniciais)
                    with ui.column().classes('gap-0 flex-1'):
                        ui.label(cliente.nome).classes('text-sm font-medium truncate').style(f'color: {DS.TEXT_PRIMARY}; max-width: 140px;')
                        ui.label(user.email).classes('text-xs truncate').style(f'color: {DS.TEXT_TERTIARY}; max-width: 140px;')

        with ui.column().classes('flex-1 h-screen overflow-auto').style('padding: 0;'):
            with ui.row().classes('w-full items-center justify-between').style(f'padding: 20px 40px; background: {DS.SURFACE}; border-bottom: 1px solid {DS.BORDER}; min-height: 72px;'):
                with ui.column().classes('gap-1'):
                    ui.label('YOUR WORKSPACE').classes('text-xs font-medium').style(f'color: {DS.TEXT_TERTIARY}; letter-spacing: 0.05em;')
                    ui.label(cliente.nome).classes('text-lg font-semibold').style(f'color: {DS.TEXT_PRIMARY}; letter-spacing: -0.02em;')
                with ui.row().classes('items-center gap-3'):
                    UIComponents.status_badge('Active', 'success')
                    def logout_action(): state.logout(); app.storage.user['state'] = state; ui.navigate.to('/login')
                    UIComponents.ghost_button('Sign out', on_click=logout_action, icon='logout')
            
            with LayoutComponents.page_container():
                LayoutComponents.page_header(title='Your analytics workspace', subtitle='Access real-time insights and data visualizations across your organization')
                if dashboards:
                    LayoutComponents.section_header(title='Active workspaces', badge=f'{len(dashboards)} available')
                    with ui.grid(columns='repeat(auto-fill, minmax(360px, 1fr))').classes('w-full').style('gap: 24px;'):
                        for idx, dash in enumerate(dashboards):
                            tipo_themes = {'financeiro': {'color': DS.SUCCESS, 'bg': DS.SUCCESS_BG, 'icon': 'account_balance_wallet', 'gradient': f'linear-gradient(135deg, {DS.SUCCESS} 0%, #059669 100%)'}, 'rh': {'color': DS.PRIMARY, 'bg': DS.PRIMARY_LIGHT, 'icon': 'people', 'gradient': f'linear-gradient(135deg, {DS.PRIMARY} 0%, {DS.PRIMARY_HOVER} 100%)'}, 'comercial': {'color': DS.WARNING, 'bg': DS.WARNING_BG, 'icon': 'storefront', 'gradient': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'}, 'operacional': {'color': '#8b5cf6', 'bg': '#faf5ff', 'icon': 'settings', 'gradient': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)'}}
                            theme = tipo_themes.get(dash.tipo.lower(), {'color': DS.TEXT_SECONDARY, 'bg': DS.SURFACE_100, 'icon': 'dashboard', 'gradient': f'linear-gradient(135deg, {DS.TEXT_SECONDARY} 0%, {DS.TEXT_TERTIARY} 100%)'})
                            card = ui.column().classes('cursor-pointer group').style(f'background: {DS.SURFACE}; border: 1px solid {DS.BORDER}; border-radius: {DS.RADIUS_LG}; overflow: hidden; transition: all {DS.TRANSITION_BASE}; box-shadow: {DS.SHADOW_SM}; opacity: 0; animation: fadeInUp 0.5s ease-out forwards; animation-delay: {idx * 0.05}s;')
                            with card:
                                with ui.row().classes('items-center justify-between w-full').style(f'padding: 24px; background: {theme["bg"]}; border-bottom: 1px solid {DS.BORDER_LIGHT};'):
                                    with ui.column().classes('items-center justify-center').style(f'width: 48px; height: 48px; background: {theme["gradient"]}; border-radius: {DS.RADIUS_MD}; box-shadow: {DS.SHADOW_MD};'): ui.icon(theme['icon'], size='24px', color='white')
                                    ui.label(dash.tipo.upper()).classes('text-xs font-bold').style(f'color: {theme["color"]}; background: {DS.SURFACE}; padding: 4px 10px; border-radius: {DS.RADIUS_SM}; letter-spacing: 0.08em;')
                                with ui.column().classes('gap-4').style('padding: 24px;'):
                                    with ui.column().classes('gap-2'):
                                        ui.label(dash.nome).classes('text-lg font-semibold').style(f'color: {DS.TEXT_PRIMARY}; line-height: 1.4;')
                                        ui.label('Real-time analytics and insights for your team').classes('text-sm').style(f'color: {DS.TEXT_SECONDARY}; line-height: 1.5;')
                                    with ui.row().classes('items-center gap-2 mt-2'):
                                        ui.label('Open workspace').classes('text-sm font-medium').style(f'color: {theme["color"]};')
                                        ui.icon('arrow_forward', size='18px').style(f'color: {theme["color"]};')
                            card.on('mouseenter', lambda e, c=card: c.style(f'border-color: {DS.PRIMARY}; box-shadow: {DS.SHADOW_XL}; transform: translateY(-4px) scale(1.02);'))
                            card.on('mouseleave', lambda e, c=card: c.style(f'border-color: {DS.BORDER}; box-shadow: {DS.SHADOW_SM}; transform: translateY(0) scale(1);'))
                            card.on('click', lambda d=dash: ui.navigate.to(f'/dashboard/{d.id}'))
                else: LayoutComponents.empty_state(icon='analytics', title='No workspaces available', description='Your analytics workspaces will appear here once they\'re assigned to your account.', cta_text='Contact support', cta_action=lambda: None)

@ui.page('/dashboard/{dash_id}')
def page_dashboard(dash_id: int):
    """Enterprise Workspace Viewer"""
    state = app.storage.user.get('state', AppState())
    if not state or not state.user_email: ui.navigate.to('/login'); return
    user = state.get_user_completo()
    if not user: ui.navigate.to('/login'); return
    db = SessionLocal()
    dash = db.query(Dashboard).filter(Dashboard.id == dash_id).first()
    cliente = db.query(Cliente).filter(Cliente.id == user.cliente_id).first()
    db.close()

    if not dash:
        with ui.column().classes('w-full h-screen items-center justify-center').style(f'background: {DS.SURFACE_50};'):
            LayoutComponents.empty_state(icon='error_outline', title='Workspace not found', description='The workspace you\'re looking for doesn\'t exist.', cta_text='Return to home', cta_action=lambda: ui.navigate.to('/'))
        return

    fullscreen_state = {'active': False}
    last_updated = datetime.now() - timedelta(minutes=random.randint(1, 30))
    time_ago = f"{(datetime.now() - last_updated).seconds // 60}m ago"
    
    with ui.column().classes('w-full h-screen').style(f'background: {DS.SURFACE_50}; margin: 0; padding: 0; font-family: {DS.FONT};'):
        header = ui.row().classes('w-full items-center justify-between').style(f'padding: 16px 32px; background: {DS.SURFACE}; border-bottom: 1px solid {DS.BORDER}; min-height: 64px; z-index: 100; transition: all {DS.TRANSITION_SLOW};')
        with header:
            with ui.row().classes('items-center gap-4'):
                UIComponents.icon_button('arrow_back', on_click=lambda: ui.navigate.to('/'), tooltip='Back to workspaces')
                ui.separator().classes('h-6').style(f'background: {DS.BORDER};')
                UIComponents.breadcrumb([{'label': 'Home', 'onClick': lambda: ui.navigate.to('/')}, {'label': 'Workspaces', 'onClick': lambda: ui.navigate.to('/')}, {'label': dash.nome}])
            with ui.row().classes('items-center gap-2'):
                with ui.row().classes('items-center gap-2 px-3 py-1.5').style(f'background: {DS.SURFACE_100}; border-radius: {DS.RADIUS_MD};'):
                    ui.icon('schedule', size='16px').style(f'color: {DS.TEXT_TERTIARY};')
                    ui.label(f'Updated {time_ago}').classes('text-xs font-medium').style(f'color: {DS.TEXT_SECONDARY};')
                ui.separator().classes('h-6').style(f'background: {DS.BORDER};')
                with ui.row().classes('items-center gap-1.5 px-3 py-1.5').style(f'background: {DS.SUCCESS_BG}; border-radius: {DS.RADIUS_MD};'):
                    ui.html(f'<div style="width: 6px; height: 6px; background: {DS.SUCCESS}; border-radius: 50%; animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;"></div><style>@keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}</style>', sanitize=False)
                    ui.label('Live').classes('text-xs font-semibold').style(f'color: {DS.SUCCESS};')
                ui.separator().classes('h-6').style(f'background: {DS.BORDER};')
                refresh_btn = UIComponents.icon_button('refresh', tooltip='Refresh workspace')
                def refresh_dashboard():
                    refresh_btn.props('loading')
                    ui.timer(1.2, lambda: refresh_btn.props(remove='loading'), once=True)
                refresh_btn.on('click', refresh_dashboard)
                UIComponents.icon_button('open_in_new', tooltip='Open in new tab')
                fullscreen_btn = UIComponents.icon_button('fullscreen', tooltip='Enter focus mode')
                def toggle_fullscreen():
                    fullscreen_state['active'] = not fullscreen_state['active']
                    if fullscreen_state['active']:
                        header.style(f'transform: translateY(-100%); opacity: 0; pointer-events: none;')
                        fullscreen_btn.props('icon=fullscreen_exit')
                        exit_btn.classes(remove='hidden')
                    else:
                        header.style(f'transform: translateY(0); opacity: 1; pointer-events: auto;')
                        fullscreen_btn.props('icon=fullscreen')
                        exit_btn.classes(add='hidden')
                fullscreen_btn.on('click', toggle_fullscreen)
        
        with ui.column().classes('w-full flex-1').style(f'padding: 20px; background: {DS.SURFACE_50}; position: relative;'):
            exit_btn = ui.button(icon='fullscreen_exit', on_click=toggle_fullscreen).props('no-caps flat').classes('hidden').style(f'position: absolute; top: 32px; right: 32px; z-index: 1000; background: {DS.SURFACE}; color: {DS.TEXT_PRIMARY}; border: 1px solid {DS.BORDER}; padding: 8px 16px; box-shadow: {DS.SHADOW_LG};')
            exit_btn.set_text('Exit focus mode')
            
            embed_wrapper = ui.column().classes('w-full h-full').style(f'background: {DS.SURFACE}; border-radius: {DS.RADIUS_XL}; border: 1px solid {DS.BORDER}; overflow: hidden; box-shadow: {DS.SHADOW_XL}; position: relative;')
            
            with embed_wrapper:
                loading_overlay = ui.column().classes('w-full h-full items-center justify-center absolute top-0 left-0 z-50').style(f'background: {DS.SURFACE}; transition: opacity {DS.TRANSITION_SLOW}, transform {DS.TRANSITION_SLOW};')
                with loading_overlay:
                    with ui.column().classes('w-full h-full').style('padding: 40px;'):
                        SkeletonLoader.create('100%')
                        with ui.column().classes('items-center gap-2 absolute').style('top: 50%; left: 50%; transform: translate(-50%, -50%);'):
                            ui.html(f'<div style="width: 48px; height: 48px; border: 3px solid {DS.BORDER}; border-top-color: {DS.PRIMARY}; border-radius: 50%; animation: spin 1s linear infinite;"></div><style>@keyframes spin {{ to {{ transform: rotate(360deg); }} }}</style>', sanitize=False)
                            ui.label('Preparing your workspace...').classes('text-base font-medium mt-4').style(f'color: {DS.TEXT_PRIMARY};')
                
                error_overlay = ui.column().classes('w-full h-full items-center justify-center absolute top-0 left-0 z-40 hidden').style(f'background: {DS.SURFACE};')
                with error_overlay:
                    LayoutComponents.empty_state(icon='error_outline', title='Failed to load workspace', description='Please check your connection and try again.', cta_text='Reload workspace', cta_action=lambda: ui.navigate.reload())
                    with ui.row().classes('gap-3 mt-4'): UIComponents.ghost_button('Go back', on_click=lambda: ui.navigate.to('/'))
                
                iframe_id = f'workspace-iframe-{dash_id}'
                
                # 1. RENDERIZA APENAS O HTML DO IFRAME (SEM SCRIPTS)
                ui.html(f'''
                <iframe 
                    id="{iframe_id}" 
                    src="{dash.link_embed}" 
                    style="width: 100%; height: 100%; border: none; display: block; background: white; opacity: 0; transition: opacity {DS.TRANSITION_SLOW};" 
                    allowfullscreen 
                    loading="lazy">
                </iframe>
                ''', sanitize=False)

                # 2. EXECUTA O JAVASCRIPT SEPARADAMENTE
                ui.run_javascript(f'''
                    (function() {{
                        const iframe = document.getElementById('{iframe_id}');
                        const loadingOverlay = iframe.parentElement.querySelector('.absolute.z-50');
                        const errorOverlay = iframe.parentElement.querySelector('.absolute.z-40');
                        
                        // Timeout for error
                        const timeoutId = setTimeout(() => {{
                            loadingOverlay.style.opacity = '0';
                            loadingOverlay.style.transform = 'translateY(-20px)';
                            setTimeout(() => {{
                                loadingOverlay.classList.add('hidden');
                                errorOverlay.classList.remove('hidden');
                            }}, 300);
                        }}, 15000);
                        
                        iframe.addEventListener('load', function() {{
                            clearTimeout(timeoutId);
                            loadingOverlay.style.opacity = '0';
                            loadingOverlay.style.transform = 'translateY(-20px)';
                            setTimeout(() => {{
                                loadingOverlay.classList.add('hidden');
                                iframe.style.opacity = '1';
                            }}, 300);
                        }});
                        
                        iframe.addEventListener('error', function() {{
                            clearTimeout(timeoutId);
                            loadingOverlay.style.opacity = '0';
                            setTimeout(() => {{
                                loadingOverlay.classList.add('hidden');
                                errorOverlay.classList.remove('hidden');
                            }}, 300);
                        }});
                    }})();
                ''')

# ============================================================================
# GLOBAL STYLES
# ============================================================================

def inject_global_styles():
    ui.add_head_html(f'''
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: {DS.FONT}; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }}
            ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
            ::-webkit-scrollbar-track {{ background: {DS.SURFACE_50}; }}
            ::-webkit-scrollbar-thumb {{ background: {DS.BORDER}; border-radius: 4px; }}
            ::-webkit-scrollbar-thumb:hover {{ background: {DS.BORDER_DARK}; }}
            @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            @keyframes fadeIn {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
            @keyframes shimmer {{ 0% {{ background-position: -200% 0; }} 100% {{ background-position: 200% 0; }} }}
            *:focus-visible {{ outline: 2px solid {DS.PRIMARY}; outline-offset: 2px; }}
        </style>
    ''', shared=True)

# ============================================================================
# INITIALIZATION
# ============================================================================

Base.metadata.create_all(bind=engine)

if __name__ in {'__main__', '__mp_main__'}:
    inject_global_styles()
    port = int(os.environ.get('PORT', 8080))
    ui.run(title='CX Data - Enterprise Analytics', favicon='📊', host='0.0.0.0', port=port, storage_secret='cx_enterprise_2024_secure', reload=False)
