let tamanhoFonte = 1;
let perguntaAtual = null;
let respostaAtual = '';
let historico = [];
let todasPerguntas = [];
let categorias = [];

const mensagemInicial = 'Escolha um assunto abaixo para começar.';

function criarBotao(texto, classes, icone, aoClicar) {
  const botao = document.createElement('button');
  botao.type = 'button';
  botao.className = classes;
  const elementoIcone = document.createElement('i');
  elementoIcone.className = `bi ${icone}`;
  elementoIcone.setAttribute('aria-hidden', 'true');
  const rotulo = document.createElement('span');
  rotulo.textContent = texto;
  botao.append(elementoIcone, rotulo);
  botao.addEventListener('click', aoClicar);
  return botao;
}

function renderizarMenu() {
  const container = document.getElementById('botoes');
  container.innerHTML = '';
  container.className = 'menu-grid mb-4';

  categorias.forEach((item) => {
    const botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'category-card';
    botao.addEventListener('click', () => fazerPergunta(item.pergunta));

    const icone = document.createElement('i');
    icone.className = `bi ${item.icone} category-icon`;
    icone.setAttribute('aria-hidden', 'true');
    const texto = document.createElement('span');
    texto.className = 'category-copy';
    const titulo = document.createElement('strong');
    titulo.textContent = item.categoria;
    const descricao = document.createElement('small');
    descricao.textContent = item.descricao || item.pergunta;
    texto.append(titulo, descricao);
    botao.append(icone, texto);
    container.appendChild(botao);
  });
}

function restaurarMenuInicial() {
  pararLeitura();
  perguntaAtual = null;
  respostaAtual = '';
  historico = [];
  document.getElementById('progresso').hidden = true;
  document.getElementById('controles-leitura').hidden = true;
  const respostaDiv = document.getElementById('resposta');
  const paragrafo = document.createElement('p');
  paragrafo.textContent = mensagemInicial;
  respostaDiv.replaceChildren(paragrafo);
  respostaDiv.classList.add('mostrar');
  renderizarMenu();
}

function atualizarProgresso(pergunta) {
  document.getElementById('progresso').hidden = false;
  document.getElementById('etapa-atual').textContent = `Etapa ${historico.length + 1}`;
  document.getElementById('pergunta-atual').textContent = pergunta;
}

function renderizarNavegacao(proximas) {
  const container = document.getElementById('botoes');
  container.innerHTML = '';
  container.className = 'flow-actions mb-4';

  proximas.forEach((proxima) => {
    container.appendChild(criarBotao(
      proxima, 'btn btn-lg btn-success', 'bi-arrow-right-circle',
      () => fazerPergunta(proxima)
    ));
  });

  if (historico.length > 0) {
    container.appendChild(criarBotao(
      'Pergunta anterior', 'btn btn-lg btn-outline-light', 'bi-arrow-left-circle',
      voltarPergunta
    ));
  }

  container.appendChild(criarBotao(
    'Voltar ao menu principal', 'btn btn-lg btn-outline-light', 'bi-house-door',
    carregarPerguntas
  ));
}

function fazerPergunta(pergunta, registrarHistorico = true) {
  pararLeitura();
  if (registrarHistorico && perguntaAtual) historico.push(perguntaAtual);

  fetch(`${API_BASE_URL}/responder`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({pergunta})
  })
    .then((res) => {
      if (!res.ok) throw new Error('Resposta indisponível');
      return res.json();
    })
    .then((data) => {
      perguntaAtual = pergunta;
      respostaAtual = data.resposta;
      atualizarProgresso(pergunta);

      const respostaDiv = document.getElementById('resposta');
      respostaDiv.classList.remove('mostrar');
      const paragrafo = document.createElement('p');
      paragrafo.textContent = data.resposta;
      respostaDiv.replaceChildren(paragrafo);

      if (data.imagem_url) {
        const img = document.createElement('img');
        img.src = data.imagem_url;
        img.alt = `Ilustração explicativa para: ${pergunta}`;
        img.className = 'img-fluid mt-3 rounded response-image';
        img.loading = 'lazy';
        respostaDiv.appendChild(img);
      }

      window.setTimeout(() => respostaDiv.classList.add('mostrar'), 50);
      document.getElementById('controles-leitura').hidden = false;
      renderizarNavegacao(Array.isArray(data.proximas) ? data.proximas : []);
      respostaDiv.setAttribute('tabindex', '-1');
      respostaDiv.focus({preventScroll: true});
    })
    .catch(() => {
      document.getElementById('resposta').textContent = 'Erro ao conectar com o servidor. Tente novamente.';
    });
}

function voltarPergunta() {
  const anterior = historico.pop();
  if (anterior) fazerPergunta(anterior, false);
}

function carregarPerguntas() {
  document.getElementById('busca').value = '';
  document.getElementById('limpar-busca').hidden = true;
  document.getElementById('status-busca').textContent = '';
  restaurarMenuInicial();
}

function normalizarTexto(texto) {
  return texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
}

function pesquisarPerguntas(termo) {
  const termoNormalizado = normalizarTexto(termo.trim());
  const status = document.getElementById('status-busca');
  document.getElementById('limpar-busca').hidden = !termoNormalizado;

  if (!termoNormalizado) {
    status.textContent = '';
    restaurarMenuInicial();
    return;
  }

  const resultados = todasPerguntas.filter((pergunta) =>
    normalizarTexto(pergunta).includes(termoNormalizado)
  );
  const plural = resultados.length === 1 ? '' : 's';
  status.textContent = `${resultados.length} resultado${plural} encontrado${plural}.`;
  const container = document.getElementById('botoes');
  container.innerHTML = '';
  container.className = 'search-results mb-4';

  resultados.forEach((pergunta) => {
    container.appendChild(criarBotao(
      pergunta, 'btn btn-lg btn-primary text-start', 'bi-search',
      () => {
        historico = [];
        perguntaAtual = null;
        fazerPergunta(pergunta);
      }
    ));
  });
}

function aumentarFonte() {
  tamanhoFonte = Math.min(1.8, tamanhoFonte + 0.15);
  document.documentElement.style.setProperty('--font-scale', tamanhoFonte);
}

function diminuirFonte() {
  tamanhoFonte = Math.max(0.85, tamanhoFonte - 0.15);
  document.documentElement.style.setProperty('--font-scale', tamanhoFonte);
}

function alternarContraste() {
  document.body.classList.toggle('alto-contraste');
}

function alternarMovimento() {
  document.body.classList.toggle('reduzir-movimento');
}

function resetarAcessibilidade() {
  tamanhoFonte = 1;
  document.documentElement.style.setProperty('--font-scale', 1);
  document.body.classList.remove('alto-contraste', 'reduzir-movimento');
  document.getElementById('velocidade-voz').value = '1';
  pararLeitura();
}

function lerResposta() {
  if (!respostaAtual || !('speechSynthesis' in window)) return;
  pararLeitura();
  const utterance = new SpeechSynthesisUtterance(respostaAtual);
  utterance.lang = 'pt-BR';
  utterance.rate = Number(document.getElementById('velocidade-voz').value);
  window.speechSynthesis.speak(utterance);
}

function pararLeitura() {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
}

function inicializarAssistente() {
  Promise.all([
    fetch(`${API_BASE_URL}/catalogo`).then((res) => res.json()),
    fetch(`${API_BASE_URL}/perguntas`).then((res) => res.json())
  ])
    .then(([catalogo, perguntas]) => {
      categorias = catalogo.categorias || [];
      todasPerguntas = perguntas.perguntas || [];
      restaurarMenuInicial();
    })
    .catch(() => {
      document.getElementById('resposta').textContent = 'Não foi possível carregar o assistente. Atualize a página para tentar novamente.';
    });

  document.getElementById('busca').addEventListener('input', (evento) => pesquisarPerguntas(evento.target.value));
  document.getElementById('limpar-busca').addEventListener('click', carregarPerguntas);
  document.getElementById('ouvir-resposta').addEventListener('click', lerResposta);
  document.getElementById('parar-leitura').addEventListener('click', pararLeitura);
  window.addEventListener('beforeunload', pararLeitura);
}
