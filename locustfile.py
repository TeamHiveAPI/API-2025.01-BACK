from locust import HttpUser, task, between
from random import randint
import uuid

class UsuarioSimulado(HttpUser):
    wait_time = between(1, 1.5)

    def on_start(self):
        """
        Cria um novo usuário e armazena o token JWT para autenticação.
        """
        self.email = f"usuario_{uuid.uuid4().hex[:8]}@teste.com"
        self.senha = "123456"
        self.nome = f"Usuário {uuid.uuid4().hex[:4]}"

        resposta = self.client.post("/usuarios", json={
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha
        })

        if resposta.status_code == 200:
            dados = resposta.json()
            self.token = dados["access_token"]
            self.headers = {
                "Authorization": f"Bearer {self.token}"
            }
            self.user_id = dados["user_id"]
        else:
            self.token = None
            self.headers = {}
            self.user_id = None
            print("Erro ao criar usuário:", resposta.text)

    @task(3)
    def listar_usuarios(self):
        page = randint(1, 10)
        self.client.get(f"/usuarios/?page={page}", headers=self.headers)


    @task(2)
    def ver_perfil(self):
        self.client.get("/usuarios/me", headers=self.headers)

    @task(1)
    def ver_usuario_por_id(self):
        if self.user_id:
            self.client.get(f"/usuarios/{self.user_id}", headers=self.headers)

    @task(1)
    def atualizar_usuario(self):
        if self.user_id:
            novo_nome = f"{self.nome}_editado"
            self.client.put(f"/usuarios/{self.user_id}", headers=self.headers, json={
                "nome": novo_nome
            })