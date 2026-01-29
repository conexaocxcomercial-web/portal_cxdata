from cxdata_app import SessionLocal, Cliente, User, hash_password, Base, engine

def criar_usuario_inicial():
    # 1. Garante que as tabelas existem
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Verifica se já existe algum cliente
        if db.query(Cliente).first():
            print("Já existem dados no banco. Operação cancelada para evitar duplicidade.")
            return

        print("Criando dados iniciais...")

        # 2. Cria o Cliente (Tenant) da sua própria empresa ou cliente piloto
        primeiro_cliente = Cliente(nome="Empresa Admin")
        db.add(primeiro_cliente)
        db.commit()
        db.refresh(primeiro_cliente)

        # 3. Cria o Usuário Admin
        admin_user = User(
            email="admin@cxdata.com",  # <--- TROQUE PELO SEU EMAIL DE LOGIN
            password_hash=hash_password("admin123"), # <--- TROQUE PELA SENHA INICIAL
            cliente_id=primeiro_cliente.id,
            perfil="admin"
        )
        db.add(admin_user)
        db.commit()

        print(f"Sucesso! Cliente '{primeiro_cliente.nome}' e Usuário '{admin_user.email}' criados.")
        print("Agora você pode fazer login no sistema.")

    except Exception as e:
        print(f"Erro ao criar dados: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    criar_usuario_inicial()