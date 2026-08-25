function adicionarCampoProxima() {
  const container = document.getElementById('proximas-container');
  const grupo = document.createElement('div');
  grupo.className = 'input-group mb-2';

  const input = document.createElement('input');
  input.type = 'text';
  input.className = 'form-control campo-proxima';
  input.placeholder = 'Digite uma próxima pergunta';

  const btnRemover = document.createElement('button');
  btnRemover.type = 'button';
  btnRemover.className = 'btn btn-outline-danger';
  btnRemover.innerText = '−';
  btnRemover.onclick = () => grupo.remove();

  grupo.appendChild(input);
  grupo.appendChild(btnRemover);
  container.appendChild(grupo);
}

document.getElementById('form-adicionar').addEventListener('submit', function (event) {
  event.preventDefault();

  const pergunta = document.getElementById('pergunta').value.trim();
  const resposta = document.getElementById('resposta').value.trim();
  const imagem_url = document.getElementById('imagem_url').value.trim();
  const proximas = Array.from(document.querySelectorAll('.campo-proxima'))
    .map((el) => el.value.trim())
    .filter(Boolean)
    .join('|');

  const form = document.getElementById('form-adicionar');
  const editando = form.dataset.editando === 'true';
  const request = editando
    ? fetch(`${API_BASE_URL}/perguntas_detalhadas`).then((res) => res.json()).then((data) => {
        const original = data.perguntasDetalhadas.find(
          (item) => item.pergunta.toLowerCase() === form.dataset.perguntaOriginal.toLowerCase()
        );
        if (!original) throw new Error('Pergunta não encontrada');
        return fetch(`${API_BASE_URL}/editar/${original.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pergunta, resposta, proxima: proximas, imagem_url }),
        });
      })
    : fetch(`${API_BASE_URL}/adicionar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta, resposta, proxima: proximas, imagem_url }),
      });

  request.then((res) => res.json()).then((data) => {
    document.getElementById('mensagem').innerText = data.mensagem;
    form.reset();
    delete form.dataset.editando;
    delete form.dataset.perguntaOriginal;
    carregarPerguntasCadastradas();
  }).catch(() => {
    document.getElementById('mensagem').innerText = 'Erro ao comunicar com o servidor.';
  });
});

function carregarPerguntasCadastradas() {
  fetch(`${API_BASE_URL}/perguntas`)
    .then((res) => res.json())
    .then((data) => {
      const lista = document.getElementById('perguntas-cadastradas');
      lista.innerHTML = '';
      data.perguntas.forEach((pergunta) => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        const span = document.createElement('span');
        span.textContent = pergunta;
        const btnEditar = document.createElement('button');
        btnEditar.className = 'btn btn-sm btn-warning';
        btnEditar.innerText = 'Editar';
        btnEditar.onclick = () => carregarParaEdicao(pergunta);
        li.appendChild(span);
        li.appendChild(btnEditar);
        lista.appendChild(li);
      });
    });
}

function carregarParaEdicao(pergunta) {
  fetch(`${API_BASE_URL}/responder`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ pergunta }),
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById('pergunta').value = pergunta;
      document.getElementById('resposta').value = data.resposta;
      document.getElementById('imagem_url').value = data.imagem_url || '';
      const container = document.getElementById('proximas-container');
      container.innerHTML = '';
      data.proximas.forEach((prox) => {
        adicionarCampoProxima();
        container.lastElementChild.querySelector('input').value = prox;
      });
      const form = document.getElementById('form-adicionar');
      form.dataset.editando = 'true';
      form.dataset.perguntaOriginal = pergunta;
    });
}

document.addEventListener('DOMContentLoaded', carregarPerguntasCadastradas);
