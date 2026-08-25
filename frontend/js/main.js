let tamanhoFonte = 1;
const mensagemInicial = 'Clique em uma pergunta acima para ver a resposta.';

function restaurarMenuInicial() {
  speechSynthesis.cancel();
  const respostaDiv = document.getElementById('resposta');
  respostaDiv.innerHTML = `<p>${mensagemInicial}</p>`;
  respostaDiv.classList.add('mostrar');
}

function fazerPergunta(pergunta) {
  fetch(`${API_BASE_URL}/responder`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({pergunta})
  })
  .then(res => res.json())
  .then(data => {
    const respostaDiv = document.getElementById('resposta');
    respostaDiv.classList.remove('mostrar');
    respostaDiv.innerHTML = `<p>${data.resposta}</p>`;

    if (data.imagem_url) {
      const img = document.createElement('img');
      img.src = data.imagem_url;
      img.alt = 'Imagem explicativa';
      img.className = 'img-fluid mt-3 mb-2 rounded';
      respostaDiv.appendChild(img);
    }

    lerResposta(data.resposta);

    setTimeout(() => {
      respostaDiv.classList.add('mostrar');
    }, 50);

    const container = document.getElementById('botoes');
    container.innerHTML = '';

    if (Array.isArray(data.proximas) && data.proximas.length > 0) {
      data.proximas.forEach(proxima => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-lg btn-success m-2';
        btn.innerHTML = `<i class="bi bi-arrow-right-circle"></i> ${proxima}`;
        btn.onclick = () => fazerPergunta(proxima);
        container.appendChild(btn);
      });
    }

    const btnVoltar = document.createElement('button');
    btnVoltar.className = 'btn btn-outline-light m-2';
    btnVoltar.innerHTML = `<i class="bi bi-arrow-counterclockwise"></i> Voltar ao menu principal`;
    btnVoltar.onclick = carregarPerguntas;
    container.appendChild(btnVoltar);
  })
  .catch(() => {
    document.getElementById('resposta').innerText = 'Erro ao conectar com o servidor.';
  });
}

function carregarPerguntas() {
  fetch(`${API_BASE_URL}/perguntas`)
    .then(res => res.json())
    .then(data => {
      const container = document.getElementById('botoes');
      container.innerHTML = '';

      data.perguntas.forEach(pergunta => {
        const btn = document.createElement('button');
        btn.className = 'btn btn-lg btn-primary m-2';
        btn.innerText = pergunta;
        btn.onclick = () => fazerPergunta(pergunta);
        container.appendChild(btn);
      });

      restaurarMenuInicial();
    });
}



function aumentarFonte() {
  tamanhoFonte += 0.2;
  document.querySelector('#resposta').style.fontSize = `${tamanhoFonte}rem`;

  // Se quiser aplicar aos botões também:
  document.querySelectorAll('button').forEach(btn => {
    btn.style.fontSize = `${tamanhoFonte}rem`;
  });
}

function diminuirFonte() {
  tamanhoFonte = Math.max(0.8, tamanhoFonte - 0.2);
  document.querySelector('#resposta').style.fontSize = `${tamanhoFonte}rem`;

  document.querySelectorAll('button').forEach(btn => {
    btn.style.fontSize = `${tamanhoFonte}rem`;
  });
}

function alternarContraste() {
  document.body.classList.toggle('alto-contraste');
}

function resetarAcessibilidade() {
  tamanhoFonte = 1;
  document.querySelector('#resposta').style.fontSize = '1rem';
  document.querySelectorAll('button').forEach(btn => {
    btn.style.fontSize = '1.2rem';
  });
  document.body.classList.remove('alto-contraste');
}

function lerResposta(texto) {
  // Interrompe qualquer fala anterior
  speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(texto);
  utterance.lang = 'pt-BR';
  speechSynthesis.speak(utterance);
}
