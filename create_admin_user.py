#!/usr/bin/env python3
"""
Script para criar um usuário administrador no sistema Taiglo MVP
"""

import requests
import json
import sys

# Configurações
API_BASE_URL = "http://localhost:3000/api"
ADMIN_EMAIL = "admin@taiglo.com"
ADMIN_PASSWORD = "admin123"
ADMIN_FIRST_NAME = "Administrador"
ADMIN_LAST_NAME = "Taiglo"

def create_admin_user():
    """Cria um usuário administrador"""
    
    print("🔧 Criando usuário administrador...")
    
    # Dados do usuário admin
    user_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
        "first_name": ADMIN_FIRST_NAME,
        "last_name": ADMIN_LAST_NAME
    }
    
    try:
        # Registrar usuário
        response = requests.post(
            f"{API_BASE_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Usuário administrador criado com sucesso!")
            print(f"📧 Email: {ADMIN_EMAIL}")
            print(f"🔑 Senha: {ADMIN_PASSWORD}")
            print(f"🎫 Token: {result.get('access_token', 'N/A')}")
            
            # Adicionar role de admin
            add_admin_role(result.get('access_token'))
            
        elif response.status_code == 409:
            print("⚠️  Usuário já existe. Tentando fazer login...")
            
            # Tentar fazer login
            login_data = {
                "email": ADMIN_EMAIL,
                "password": ADMIN_PASSWORD
            }
            
            login_response = requests.post(
                f"{API_BASE_URL}/auth/login",
                json=login_data,
                headers={"Content-Type": "application/json"}
            )
            
            if login_response.status_code == 200:
                result = login_response.json()
                user = result.get('user', {})
                
                # Verificar se já tem role de admin
                roles = user.get('roles', [])
                has_admin_role = any(role.get('name') == 'admin' for role in roles)
                
                if has_admin_role:
                    print("✅ Login realizado com sucesso!")
                    print(f"👤 Usuário: {user.get('first_name')} {user.get('last_name')}")
                    print(f"🔑 Roles: {[role.get('name') for role in roles]}")
                    print(f"🎫 Token: {result.get('access_token', 'N/A')}")
                else:
                    print("❌ Usuário existe mas não é admin. Adicionando role...")
                    add_admin_role(result.get('access_token'))
            else:
                print(f"❌ Erro no login: {login_response.text}")
                
        else:
            print(f"❌ Erro ao criar usuário: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão. Verifique se o API Gateway está rodando em http://localhost:3000")
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")

def add_admin_role(token):
    """Adiciona role de admin ao usuário"""
    try:
        # Primeiro, obter o ID do usuário atual
        me_response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if me_response.status_code == 200:
            user_data = me_response.json().get('user', {})
            user_id = user_data.get('id')
            
            # Adicionar role de admin
            role_data = {"role": "admin"}
            role_response = requests.post(
                f"{API_BASE_URL}/auth/users/{user_id}/roles",
                json=role_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"
                }
            )
            
            if role_response.status_code == 200:
                print("✅ Role 'admin' adicionado com sucesso!")
                result = role_response.json()
                print(f"🔑 Roles atualizados: {[role.get('name') for role in result.get('roles', [])]}")
            else:
                print(f"❌ Erro ao adicionar role: {role_response.text}")
        else:
            print(f"❌ Erro ao obter dados do usuário: {me_response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao adicionar role: {str(e)}")

def test_admin_access():
    """Testa o acesso às rotas de admin"""
    
    print("\n🧪 Testando acesso às rotas de admin...")
    
    try:
        # Fazer login
        login_data = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        
        login_response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            user = login_response.json().get('user', {})
            
            print(f"✅ Login realizado como: {user.get('first_name')} {user.get('last_name')}")
            print(f"🔑 Roles: {[role.get('name') for role in user.get('roles', [])]}")
            print(f"🔐 Permissões: {len(user.get('permissions', []))} permissões")
            
            # Testar rota de template
            template_response = requests.get(
                f"{API_BASE_URL}/admin/experiences/template",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if template_response.status_code == 200:
                print("✅ Acesso às rotas de admin funcionando!")
                template_data = template_response.json()
                print(f"📋 Template disponível com {len(template_data.get('columns', []))} colunas")
            else:
                print(f"❌ Erro ao acessar template: {template_response.status_code}")
                print(f"   Resposta: {template_response.text}")
                
        else:
            print(f"❌ Erro no login: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Erro no teste: {str(e)}")

def main():
    """Função principal"""
    
    print("🎯 Taiglo MVP - Criador de Usuário Administrador")
    print("=" * 50)
    
    # Verificar se o API Gateway está rodando
    try:
        health_response = requests.get(f"{API_BASE_URL.replace('/api', '')}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ API Gateway não está respondendo corretamente")
            return
    except:
        print("❌ API Gateway não está rodando em http://localhost:3000")
        print("💡 Execute: docker-compose up api-gateway")
        return
    
    # Criar usuário admin
    create_admin_user()
    
    # Testar acesso
    test_admin_access()
    
    print("\n📚 Documentação:")
    print("- Admin Features: ADMIN_FEATURES.md")
    print("- Swagger UI: http://localhost:3000/apidocs/")
    print("- Frontend: http://localhost:5173")
    print("\n🚀 Próximos passos:")
    print("1. Execute: python setup_roles_system.py (se ainda não executou)")
    print("2. Acesse o frontend e faça login")
    print("3. Verifique se o Painel Admin está disponível no menu")

if __name__ == "__main__":
    main()
