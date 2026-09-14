document.getElementById('form-login').addEventListener('submit', (evento) => {
  evento.preventDefault();
  const mensagem = document.getElementById('mensagem-login');
  const botao = evento.currentTarget.querySelector('button[type="submit"]');
  mensagem.textContent = '';
  botao.disabled = true;

  fetch(`${API_BASE_URL}/admin/login`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({senha: document.getElementById('senha').value}),
  })
    .then(async (resposta) => {
      const dados = await resposta.json();
      if (!resposta.ok) throw new Error(dados.mensagem || 'Não foi possível entrar.');
      window.location.href = 'admin.html';
    })
    .catch((erro) => {
      mensagem.textContent = erro.message;
      document.getElementById('senha').select();
    })
    .finally(() => { botao.disabled = false; });
});
