#!/usr/bin/env python3
"""
Script para configurar o sistema de roles e permissões no banco de dados Taiglo MVP
"""

import psycopg2
import os
from datetime import datetime

# Configurações do banco de dados
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'taiglo_db'),
    'user': os.getenv('DB_USER', 'taiglo_user'),
    'password': os.getenv('DB_PASSWORD', 'taiglo_password')
}

def execute_sql_file(conn, file_path):
    """Executa um arquivo SQL"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        with conn.cursor() as cursor:
            cursor.execute(sql_content)
            conn.commit()
        
        print(f"✅ Arquivo {file_path} executado com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar {file_path}: {str(e)}")
        conn.rollback()
        return False

def create_admin_user(conn, email, password_hash, first_name, last_name):
    """Cria um usuário administrador"""
    try:
        with conn.cursor() as cursor:
            # Verificar se o usuário já existe
            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                user_id = existing_user[0]
                print(f"⚠️  Usuário {email} já existe. Atualizando para admin...")
            else:
                # Criar novo usuário
                cursor.execute("""
                    INSERT INTO users (email, password_hash, first_name, last_name, is_verified)
                    VALUES (%s, %s, %s, %s, TRUE)
                    RETURNING id
                """, (email, password_hash, first_name, last_name))
                user_id = cursor.fetchone()[0]
                print(f"✅ Usuário {email} criado com sucesso")
            
            # Adicionar role de admin
            cursor.execute("""
                INSERT INTO user_roles (user_id, role_id)
                SELECT %s, id FROM roles WHERE name = 'admin'
                ON CONFLICT (user_id, role_id) DO NOTHING
            """, (user_id,))
            
            conn.commit()
            print(f"✅ Role 'admin' atribuído ao usuário {email}")
            return user_id
            
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {str(e)}")
        conn.rollback()
        return None

def verify_system(conn):
    """Verifica se o sistema de roles está funcionando"""
    try:
        with conn.cursor() as cursor:
            # Verificar roles
            cursor.execute("SELECT name, description FROM roles WHERE is_active = TRUE")
            roles = cursor.fetchall()
            print(f"📋 Roles encontrados: {len(roles)}")
            for role in roles:
                print(f"  - {role[0]}: {role[1]}")
            
            # Verificar permissões
            cursor.execute("SELECT name, resource, action FROM permissions")
            permissions = cursor.fetchall()
            print(f"🔐 Permissões encontradas: {len(permissions)}")
            
            # Verificar usuários admin
            cursor.execute("""
                SELECT u.email, u.first_name, u.last_name
                FROM users u
                JOIN user_roles ur ON u.id = ur.user_id
                JOIN roles r ON ur.role_id = r.id
                WHERE r.name = 'admin' AND r.is_active = TRUE
            """)
            admins = cursor.fetchall()
            print(f"👑 Usuários admin: {len(admins)}")
            for admin in admins:
                print(f"  - {admin[0]} ({admin[1]} {admin[2]})")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar sistema: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🎯 Taiglo MVP - Configuração do Sistema de Roles")
    print("=" * 50)
    
    try:
        # Conectar ao banco de dados
        print("🔌 Conectando ao banco de dados...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conexão estabelecida")
        
        # Executar schema de roles
        print("\n📋 Configurando sistema de roles...")
        if execute_sql_file(conn, 'database/roles_schema.sql'):
            print("✅ Sistema de roles configurado")
        else:
            print("❌ Falha ao configurar sistema de roles")
            return
        
        # Criar usuário admin
        print("\n👑 Criando usuário administrador...")
        admin_email = "admin@taiglo.com"
        admin_password_hash = "$2b$10$rOzJqQZ8kVx.QxMxQxMxQx"  # senha: admin123
        admin_first_name = "Administrador"
        admin_last_name = "Taiglo"
        
        user_id = create_admin_user(conn, admin_email, admin_password_hash, admin_first_name, admin_last_name)
        
        if user_id:
            print(f"✅ Usuário admin criado/atualizado com ID: {user_id}")
        else:
            print("❌ Falha ao criar usuário admin")
        
        # Verificar sistema
        print("\n🔍 Verificando sistema...")
        if verify_system(conn):
            print("✅ Sistema verificado com sucesso")
        else:
            print("❌ Falha na verificação do sistema")
        
        # Fechar conexão
        conn.close()
        print("\n📚 Próximos passos:")
        print("1. Execute o script create_admin_user.py para testar o login")
        print("2. Acesse o frontend e faça login com admin@taiglo.com / admin123")
        print("3. Verifique se o Painel Admin está disponível no menu")
        print("4. Teste as funcionalidades de upload e edição de experiências")
        
    except psycopg2.Error as e:
        print(f"❌ Erro de banco de dados: {str(e)}")
        print("💡 Verifique se o PostgreSQL está rodando e as credenciais estão corretas")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main()
