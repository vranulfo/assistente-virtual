import json
import os
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / 'backend'
DATA_FILE = BACKEND_DIR / 'data' / 'respostas.json'
sys.path.insert(0, str(BACKEND_DIR))

from app import app  # noqa: E402
from models.database import buscar_pergunta, listar_perguntas  # noqa: E402
from models import metrics  # noqa: E402


class RespostasDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.respostas = json.loads(DATA_FILE.read_text(encoding='utf-8'))

    def test_json_tem_registros(self):
        self.assertGreater(len(self.respostas), 0)

    def test_ids_e_perguntas_sao_unicos(self):
        ids = [item['id'] for item in self.respostas]
        perguntas = [item['pergunta'].strip().lower() for item in self.respostas]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(perguntas), len(set(perguntas)))

    def test_campos_obrigatorios(self):
        obrigatorios = {'id', 'pergunta', 'resposta', 'proxima_pergunta', 'imagem'}
        for item in self.respostas:
            with self.subTest(id=item.get('id')):
                self.assertTrue(obrigatorios.issubset(item))
                self.assertTrue(item['pergunta'].strip())
                self.assertTrue(item['resposta'].strip())

    def test_proximas_perguntas_existem(self):
        perguntas = {item['pergunta'].strip().lower() for item in self.respostas}
        for item in self.respostas:
            proximas = item.get('proxima_pergunta', '').split('|')
            for proxima in filter(None, (valor.strip().lower() for valor in proximas)):
                with self.subTest(origem=item['pergunta'], destino=proxima):
                    self.assertIn(proxima, perguntas)

    def test_menu_principal_tem_metadados(self):
        menu = [item for item in self.respostas if item.get('menu_principal')]
        self.assertGreater(len(menu), 0)
        for item in menu:
            with self.subTest(id=item['id']):
                self.assertTrue(item.get('categoria'))
                self.assertTrue(item.get('descricao'))
                self.assertTrue(item.get('icone'))

    def test_imagens_referenciadas_existem(self):
        for item in self.respostas:
            caminho_imagem = item.get('imagem') or ''
            if caminho_imagem.startswith('/img/'):
                imagem = ROOT_DIR / 'frontend' / caminho_imagem.removeprefix('/')
                with self.subTest(id=item['id']):
                    self.assertTrue(imagem.is_file(), imagem)


class DatabaseTest(unittest.TestCase):
    def test_busca_ignora_maiusculas_e_espacos(self):
        resultado = buscar_pergunta('  COMO ABRIR O NAVEGADOR?  ')
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado['id'], 7)

    def test_listagem_do_menu_e_menor_que_listagem_completa(self):
        menu = listar_perguntas(apenas_menu_principal=True)
        todas = listar_perguntas()
        self.assertGreater(len(menu), 0)
        self.assertLess(len(menu), len(todas))


class ApiTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config.update(TESTING=True)

    def setUp(self):
        os.environ['ADMIN_PASSWORD'] = 'senha-de-teste'
        self.client = app.test_client()

    def tearDown(self):
        os.environ.pop('ADMIN_PASSWORD', None)

    def fazer_login(self):
        return self.client.post('/admin/login', json={'senha': 'senha-de-teste'})

    def test_health(self):
        resposta = self.client.get('/health')
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.get_json()['status'], 'ok')
        self.assertEqual(resposta.get_json()['armazenamento'], 'json')

    def test_catalogo(self):
        resposta = self.client.get('/catalogo')
        dados = resposta.get_json()
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(len(dados['categorias']), 7)

    def test_admin_exige_login(self):
        resposta = self.client.get('/admin.html')
        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/login.html', resposta.location)

    def test_login_rejeita_senha_incorreta(self):
        resposta = self.client.post('/admin/login', json={'senha': 'errada'})
        self.assertEqual(resposta.status_code, 401)

    def test_login_libera_admin(self):
        self.assertEqual(self.fazer_login().status_code, 200)
        resposta = self.client.get('/admin.html')
        try:
            self.assertEqual(resposta.status_code, 200)
        finally:
            resposta.close()

    def test_rota_de_edicao_exige_login(self):
        resposta = self.client.post('/adicionar', json={
            'pergunta': 'teste', 'resposta': 'teste',
        })
        self.assertEqual(resposta.status_code, 401)

    def test_responder_pergunta(self):
        resposta = self.client.post(
            '/responder', json={'pergunta': 'como criar uma conta no gmail?'}
        )
        dados = resposta.get_json()
        self.assertEqual(resposta.status_code, 200)
        self.assertTrue(dados['resposta'])
        self.assertGreater(len(dados['proximas']), 0)
        self.assertEqual(dados['imagem_url'], '/img/criar-email.png')

    def test_imagem_e_servida(self):
        resposta = self.client.get('/img/criar-email.png')
        try:
            self.assertEqual(resposta.status_code, 200)
            self.assertEqual(resposta.mimetype, 'image/png')
        finally:
            resposta.close()

    def test_registra_e_lista_tempo_medio(self):
        arquivo_original = metrics.METRICS_FILE
        arquivo_teste = BACKEND_DIR / 'data' / 'metricas-teste.json'
        metrics.METRICS_FILE = arquivo_teste
        try:
            arquivo_teste.write_text('{}\n', encoding='utf-8')
            resposta = self.client.post('/metricas/tempo', json={
                'tela': 'Menu principal', 'duracao_segundos': 10,
            })
            self.assertEqual(resposta.status_code, 201)
            self.client.post('/metricas/tempo', json={
                'tela': 'Menu principal', 'duracao_segundos': 20,
            })
            self.fazer_login()
            dados = self.client.get('/metricas/tempo').get_json()['metricas'][0]
            self.assertEqual(dados['visualizacoes'], 2)
            self.assertEqual(dados['tempo_medio_segundos'], 15)
        finally:
            metrics.METRICS_FILE = arquivo_original
            if arquivo_teste.exists():
                arquivo_teste.unlink()

    def test_rejeita_metrica_invalida(self):
        resposta = self.client.post('/metricas/tempo', json={
            'tela': '', 'duracao_segundos': -1,
        })
        self.assertEqual(resposta.status_code, 400)


if __name__ == '__main__':
    unittest.main()
