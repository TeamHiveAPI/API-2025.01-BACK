# locustfile.py
from locust import HttpUser, task, between, events
from random import randint
import uuid
import time
from datetime import datetime, timedelta, timezone
import base64
import json
import logging

# Configuração de logging para o Locust
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)


class WebsiteUser(HttpUser):
    wait_time = between(1, 1.5)
    host = "http://localhost:8000" # Mantenha ou ajuste para a URL da sua API

    def on_start(self):
        """
        Cria um novo usuário e armazena o token JWT e refresh token.
        """
        self.email = f"locust_user_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "password123" # Senha genérica, ajuste se necessário
        self.name = f"Locust User {uuid.uuid4().hex[:4]}"

        logger.info(f"Iniciando usuário Locust: {self.name} com email: {self.email}")

        # 1. Tentar criar o usuário (esta rota NÃO deve exigir autenticação)
        try:
            create_response = self.client.post("/usuarios/", json={
                "nome": self.name,
                "email": self.email,
                "senha": self.password
            }, name="/usuarios [POST]") # Nome para o relatório do Locust
            
            if create_response.status_code == 201:
                create_data = create_response.json()
                self.access_token = create_data["access_token"]
                self.refresh_token = create_data.get("refresh_token") # Pode ser None se não implementado ainda
                self.user_id = create_data["user_id"]
                self.user_email = create_data["user_email"]
                self.user_nivel = create_data["user_nivel"]
                
                # Decodificar o access_token para pegar a expiração (exp)
                try:
                    payload_encoded = self.access_token.split('.')[1]
                    payload_encoded += '=' * (-len(payload_encoded) % 4) # Adiciona padding
                    payload = json.loads(base64.urlsafe_b64decode(payload_encoded).decode('utf-8'))
                    self.access_token_exp = payload.get("exp") # UNIX timestamp
                    self.access_token_expires_at = datetime.fromtimestamp(self.access_token_exp, tz=timezone.utc)
                    logger.info(f"Access Token para {self.user_email} expira em: {self.access_token_expires_at}")
                except Exception as e:
                    logger.warning(f"Erro ao decodificar token JWT no on_start para {self.user_email}: {e}. Definindo expiração padrão.")
                    self.access_token_exp = None
                    # Fallback para uma expiração segura se a decodificação falhar
                    self.access_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=30) 
                
                self.set_auth_headers()
                logger.info(f"Usuário {self.email} criado e token obtido com sucesso.")
            else:
                logger.error(f"Falha ao criar usuário inicial ({create_response.status_code}): {create_response.text}")
                # Reporta a falha para o Locust UI
                create_response.failure(f"Falha na criação do usuário: {create_response.text}")
                # Encerra o usuário virtual se a configuração inicial falhar
                self.environment.runner.quit() 
        except Exception as e:
            logger.critical(f"Exceção inesperada durante a criação do usuário no on_start: {e}")
            self.environment.runner.quit()


    def set_auth_headers(self):
        """Define os cabeçalhos de autorização com o token atual."""
        if self.access_token:
            self.headers = {"Authorization": f"Bearer {self.access_token}"}
        else:
            self.headers = {}
            logger.warning(f"Cabeçalhos de autenticação não definidos para {self.user_email}: access_token é None.")

    def should_refresh_token(self) -> bool:
        """Verifica se o token de acesso está prestes a expirar."""
        if not self.access_token_exp or not self.refresh_token:
            return False # Se não temos expiração ou refresh token, não podemos refrescar

        # Tentar refrescar se o token expirar em menos de 5 minutos (ajuste conforme necessário)
        # Usamos uma margem de tempo para evitar que o token expire *durante* uma requisição
        current_time_utc = datetime.now(timezone.utc)
        time_until_expiry = (self.access_token_expires_at - current_time_utc).total_seconds()
        
        # logger.debug(f"Tempo até expiração para {self.user_email}: {time_until_expiry:.2f} segundos.")
        return time_until_expiry < (5 * 60) # Menos de 5 minutos


    def refresh_access_token(self):
        """Tenta obter um novo token de acesso usando o refresh token."""
        if not self.refresh_token:
            logger.warning(f"Não há refresh token disponível para atualizar para {self.user_email}. Pulando refresh.")
            self.access_token = None # Garante que o token atual seja invalidado
            self.set_auth_headers()
            return

        logger.info(f"Tentando refrescar token para o usuário {self.user_email}...")
        try:
            refresh_response = self.client.post("/auth/refresh_token", json={
                "refresh_token": self.refresh_token
            }, catch_response=True, name="/auth/refresh_token [POST]")

            with refresh_response as response:
                if response.status_code == 200:
                    refresh_data = response.json()
                    self.access_token = refresh_data["access_token"]
                    # ATENÇÃO: Se sua rota de refresh no backend ROTACIONA o refresh token,
                    # DESCOMENTE a linha abaixo para usar o refresh token mais recente:
                    # self.refresh_token = refresh_data.get("refresh_token", self.refresh_token) 
                    
                    # Decodificar o NOVO access_token para pegar a nova expiração
                    try:
                        payload_encoded = self.access_token.split('.')[1]
                        payload_encoded += '=' * (-len(payload_encoded) % 4)
                        payload = json.loads(base64.urlsafe_b64decode(payload_encoded).decode('utf-8'))
                        self.access_token_exp = payload.get("exp")
                        self.access_token_expires_at = datetime.fromtimestamp(self.access_token_exp, tz=timezone.utc)
                        logger.info(f"NOVO Access Token para {self.user_email} expira em: {self.access_token_expires_at}")
                    except Exception as e:
                        logger.warning(f"Erro ao decodificar NOVO token JWT para {self.user_email}: {e}. Definindo expiração padrão.")
                        self.access_token_exp = None
                        self.access_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

                    self.set_auth_headers()
                    response.success() # Marca como sucesso no relatório do Locust
                    logger.info(f"Token de acesso refrescado com sucesso para {self.user_email}.")
                else:
                    logger.error(f"Falha ao refrescar token para {self.user_email} ({response.status_code}): {response.text}")
                    self.access_token = None # Invalida o token para não tentar de novo com um token ruim
                    self.set_auth_headers()
                    response.failure(f"Falha no refresh token: {response.text}")
        except Exception as e:
            logger.critical(f"Exceção inesperada durante o refresh token para {self.user_email}: {e}")
            self.access_token = None
            self.set_auth_headers()


    # Decorador de tarefa para garantir que o token esteja atualizado antes da execução
    # A função `authed_task` não é um método da classe, mas sim um decorador que é aplicado.
    def authed_task(func): # <-- Corrigido: 'func' é o único argumento
        def wrapper(self, *args, **kwargs): # <-- 'self' é passado para esta função interna
            # Primeiro, tenta refrescar se necessário
            if self.access_token and self.should_refresh_token():
                self.refresh_access_token()
            
            # Se ainda houver um token válido (ou foi recém-refrescado), executa a tarefa
            if self.access_token:
                func(self, *args, **kwargs)
            else:
                logger.warning(f"Usuário {self.user_email} sem token válido, pulando tarefa {func.__name__}")
                # O Locust automaticamente registrará como "skipped" se a requisição não for feita
        return wrapper # <-- Corrigido: Retorna a função wrapper


    @task(3) # <--- Este é o decorador do Locust
    @authed_task # <--- Este é o seu decorador customizado
    def listar_usuarios(self):
        page = randint(1, 10)
        self.client.get(f"/usuarios/?page={page}", headers=self.headers, name="/usuarios?page=[page]")

    @task(2)
    @authed_task
    def ver_perfil(self):
        self.client.get("/usuarios/me", headers=self.headers)

    @task(1)
    @authed_task
    def ver_usuario_por_id(self):
        if self.user_id: # Apenas tenta se o user_id foi obtido
            self.client.get(f"/usuarios/{self.user_id}", headers=self.headers, name="/usuarios/[id]")
        else:
            logger.warning("user_id não disponível para ver_usuario_por_id, pulando.")

    @task(1)
    @authed_task
    def atualizar_usuario(self):
        if self.user_id: # Apenas tenta se o user_id foi obtido
            novo_nome = f"{self.name}_edited_{uuid.uuid4().hex[:2]}" # Adicionado random para evitar cache
            self.client.put(f"/usuarios/{self.user_id}", headers=self.headers, json={
                "nome": novo_nome
            }, name="/usuarios/[id] [PUT]")
        else:
            logger.warning("user_id não disponível para atualizar_usuario, pulando.")