# Corridas Amorim

Jogo de corrida 2D feito em Python com Pygame. Desvie do tráfego, colete moedas, compre carros na garagem e bata o próprio recorde.

## Requisitos

- Python 3.10 ou superior
- pip

## Como rodar

1. Clone o repositório:

   ```bash
   git clone git@github.com:bielamorimc/corrida-morim.git
   cd corrida-morim
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Inicie o jogo:

   ```bash
   python main.py
   ```

## Controles

- **Setas / W A S D**: navegar menus e desviar (esquerda/direita) durante a corrida
- **Enter / Espaço**: confirmar seleção
- **P**: pausar / continuar
- **Esc**: voltar / sair

## Estrutura do projeto

- `main.py` — ponto de entrada do jogo
- `states.py` — máquina de estados (menu, garagem, corrida, pause, game over)
- `entities.py` — carros inimigos, moedas e spawners
- `cars.py` — catálogo de carros disponíveis
- `road.py` — desenho da pista
- `ui.py` — componentes de interface
- `audio.py` — gerenciamento de sons
- `storage.py` — perfil do jogador (moedas, carros, recorde)
- `settings.py` — constantes do jogo
- `assets/` — sons e demais recursos
- `tools/gen_sounds.py` — utilitário para gerar os efeitos sonoros

## Progresso

O progresso (moedas, recorde e carro selecionado) é salvo em `profile.json` na raiz do projeto.
