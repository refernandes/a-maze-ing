# Guia de leitura do A-Maze-ing

Este guia explica como acompanhar o programa desde a leitura do arquivo de
configuração até a geração, validação, gravação e exibição do labirinto. Ele
descreve o código que está em `submission_clone/` e sugere uma ordem para
entendê-lo sem começar pelo arquivo maior.

Uma revisão de código pode explicar e verificar o comportamento observado, mas
não garante uma nota: a avaliação final depende da banca e dos critérios
aplicados na correção.

## 1. Comece pelo fluxo completo

O comando normal é:

```sh
python3 a_maze_ing.py config.txt
```

O caminho percorrido pelo programa é:

1. `a_maze_ing.py` verifica se foi passado exatamente um argumento.
2. `maze_config.py` abre o arquivo e transforma as opções em um objeto `Config`.
3. `output_path()` confere se `OUTPUT_FILE` é um nome simples e se não aponta
   para um arquivo de configuração, código ou metadados do projeto.
4. `a_maze_ing.py` cria `MazeGenerator` com dimensões, coordenadas, modo e seed.
5. `MazeGenerator.generate()` prepara a grade, grava o padrão 42, abre
   corredores e valida o resultado.
6. `MazeGenerator.save_to_file()` escreve a grade hexadecimal e o rodapé no
   formato da subject.
7. `MazeDisplay.run()` escolhe a interface interativa com `curses` ou a saída
   ASCII, de acordo com o terminal disponível.

Erros de leitura, configuração ou geração são apresentados como mensagem e
encerram o programa com código de saída diferente de zero.

## 2. Ordem recomendada para estudar os arquivos

Leia os módulos nesta sequência. Cada etapa usa ideias introduzidas na etapa
anterior.

### 2.1 `mazegen/constants.py`: como a grade representa paredes

Cada célula guarda um inteiro entre `0` e `15`. Cada bit indica uma parede
fechada:

| Direção | Bit | Valor decimal | Máscara hexadecimal |
|---|---:|---:|---:|
| Norte | 0 | 1 | `1` |
| Leste | 1 | 2 | `2` |
| Sul | 2 | 4 | `4` |
| Oeste | 3 | 8 | `8` |

Uma parede fechada tem seu bit ligado. Uma passagem é aberta limpando o bit
correspondente nos dois lados da fronteira entre células vizinhas. Por exemplo,
abrir a passagem para leste limpa `EAST` na célula atual e `WEST` na célula à
direita. Essa duplicação é necessária para que os dois valores descrevam a
mesma parede.

`15` (`0xF`) significa quatro paredes fechadas; `0` significa quatro paredes
abertas. `MOVE`, `OPPOSITE` e `LETTER` centralizam as relações entre direção,
deslocamento, lado oposto e letra usada no caminho salvo.

O mesmo arquivo contém o desenho do 42 e `pattern_cells()`, que posiciona as
células totalmente fechadas no centro da grade quando há espaço suficiente.

### 2.2 `mazegen/rules.py`: operações locais sobre corredores

Este módulo contém funções pequenas reutilizadas pelo gerador, pelo modo
Pac-Man e pela validação:

- `inside()` verifica limites da grade.
- `can_move()` só considera a passagem aberta se os dois bits opostos
  estiverem limpos.
- `open_neighbours()` conta os corredores que saem de uma célula.
- `centre_cells()` calcula os candidatos ao centro, inclusive grades com
  dimensões pares.
- `safe_closed_walls()` encontra paredes internas que podem ser candidatas a
  abertura sem atravessar o 42.
- `try_open_without_3x3()` abre uma passagem provisoriamente e desfaz a mudança
  se ela criar uma área aberta de 3 por 3.
- `has_open_3x3()` e funções auxiliares detectam essa área.

Ao investigar uma regra de parede, comece por `can_move()` e siga para os
lugares que a chamam. Assim fica claro que uma passagem não deve ser inferida
olhando só um dos lados.

### 2.3 `mazegen/algorithms.py`: criação da estrutura conectada

`carve_depth_first()` implementa busca em profundidade iterativa. A pilha guarda
o caminho atual. A cada passo, o algoritmo escolhe aleatoriamente uma célula
vizinha que ainda não foi visitada e abre a parede entre as duas. Quando não há
vizinho disponível, volta para a célula anterior retirando o topo da pilha.

O resultado é uma árvore de corredores: todas as células visitadas ficam
conectadas e não há ciclos nessa etapa. O algoritmo é iterativo para não
depender do limite de recursão do Python. A aleatoriedade vem do objeto `rng`
recebido como argumento, em vez de usar o gerador global do módulo `random`.

### 2.4 `mazegen/pacman.py`: preparação do modo não perfeito

Quando `PERFECT=False`, o gerador primeiro parte da árvore criada pelo DFS.
`remove_dead_ends()` percorre as células com uma única saída e tenta abrir uma
parede segura para criar rotas alternativas. A abertura também respeita a
regra que impede blocos abertos de 3 por 3. O processo para quando uma passada
completa deixa a grade sem mudanças.

`open_spawn_cells()` verifica os quatro cantos e as células centrais. Se um
ponto exigido estiver isolado, `_open_corridor()` tenta criar uma saída segura.
Depois, `validation.py` confere que os pontos exigidos são corredores.

### 2.5 `mazegen/validation.py`: barreiras de correção

`validate_maze()` rejeita uma grade antes que ela seja considerada pronta se:

- nem todas as células jogáveis puderem ser alcançadas a partir da entrada;
- paredes compartilhadas discordarem entre duas células;
- alguma parede externa estiver aberta;
- existir uma área totalmente aberta de 3 por 3;
- o modo perfeito tiver ciclos ou o modo Pac-Man tiver menos de dois ciclos;
- o modo Pac-Man tiver mais de duas saídas sem saída ou não tiver os pontos de
  canto e centro acessíveis.

Para contar ciclos, o código usa `E - V + 1`, válido para a região conectada,
onde `V` é o número de células jogáveis e `E` é o número de passagens. Uma
árvore perfeita tem zero ciclos. O modo Pac-Man exige no mínimo dois. As células
do desenho 42 são excluídas da contagem da região jogável.

As verificações de parede são independentes da aparência do desenho: uma
parede norte/sul externa precisa continuar fechada, e os valores de cada par
de células precisam concordar sobre sua fronteira compartilhada.

### 2.6 `mazegen/solver.py`: rota mais curta e rodapé

`shortest_path()` usa busca em largura (BFS), com uma fila `deque`. A BFS visita
primeiro as células a uma passagem de distância, depois as que estão a duas,
e assim por diante. Por isso, em uma grade em que cada movimento tem o mesmo
custo, a primeira rota encontrada até a saída é uma rota mais curta.

O solver devolve coordenadas. `path_directions()` transforma cada passo em
`N`, `E`, `S` ou `W`, que são as letras esperadas no rodapé do arquivo.

### 2.7 `mazegen/generator.py`: API e coordenação

`MazeGenerator` é a fachada pública que reúne as etapas anteriores. O
construtor valida dimensões, limite de células, coordenadas e distinção entre
entrada e saída; também cria um gerador aleatório local com a seed recebida.

O método `generate()` coordena a ordem principal:

1. inicializa todas as células com as quatro paredes fechadas;
2. calcula e reserva as células do 42;
3. abre a árvore DFS a partir da entrada;
4. verifica se todas as células fora do 42 foram alcançadas;
5. no modo Pac-Man, reduz becos sem saída e prepara os cantos e o centro;
6. chama a validação completa.

Os métodos `get_grid()` e `get_pattern_cells()` devolvem cópias, para que um
consumidor não altere acidentalmente os dados internos ao receber esses
valores. `get_solution_path()` calcula a rota da entrada à saída. Chame
`generate()` antes de pedir a grade, o caminho ou salvar o resultado.

`save_to_file()` escreve uma linha hexadecimal por linha da grade, uma linha em
branco e, em seguida, entrada, saída e direções do caminho.

### 2.8 `maze_config.py` e `a_maze_ing.py`: entrada e execução

`parse_config()` aceita linhas `KEY=VALUE`, comentários começando com `#` e
linhas vazias. Exige `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE` e
`PERFECT`; `SEED` é opcional. Ela verifica formato e valores básicos. A validação
das dimensões e coordenadas da grade também é feita pelo construtor de
`MazeGenerator`.

Em `a_maze_ing.py`, `main()` liga configuração, API, arquivo e tela. A função
`output_path()` limita a saída da interface de linha de comando ao diretório
atual, bloqueia links simbólicos e protege arquivos do projeto contra
sobrescrita acidental. Essa proteção pertence à CLI; quem chama
`MazeGenerator.save_to_file()` diretamente escolhe e administra o próprio
caminho.

### 2.9 `maze_display.py`: leitura visual e comandos

`MazeDisplay` não gera as regras do labirinto; ele consome `MazeGenerator`.
`_maze_lines()` transforma os bits das paredes em linhas ASCII alinhadas e
marca entrada, saída, 42 e, quando solicitado, o caminho.

Se a saída for um terminal interativo, `_run_curses()` mostra o trecho visível
da grade e aceita `R` para gerar e salvar outra grade, `S` para alternar o
caminho, `C` para trocar a cor, setas para rolar e `Q` ou `Esc` para sair. Sem
TTY, `_print_ascii()` imprime uma visualização estática.

## 3. Estrutura de diretórios

```text
submission_clone/
├── a_maze_ing.py          # entrada da CLI e sequência da aplicação
├── maze_config.py         # leitura e validação do arquivo de configuração
├── maze_display.py        # ASCII, curses e controles de teclado
├── mazegen/
│   ├── __init__.py        # exporta MazeGenerator como API pública
│   ├── constants.py       # bits, movimentos e padrão 42
│   ├── rules.py           # movimentos, aberturas seguras e regra 3x3
│   ├── algorithms.py      # árvore inicial com DFS iterativo
│   ├── pacman.py          # rotas alternativas e pontos de spawn
│   ├── validation.py      # conectividade, paredes, bordas e modos
│   ├── solver.py          # caminho mínimo e direções de saída
│   └── generator.py       # classe pública que coordena a geração
├── config.txt             # configuração de exemplo usada pela CLI
├── pyproject.toml         # metadados e configuração do pacote
├── Makefile               # comandos de instalação, execução e lint
└── README.md              # requisitos e instruções do projeto
```

O wheel e o arquivo-fonte compactado `mazegen-*.whl` e `mazegen-*.tar.gz`
empacotam o módulo reutilizável. `LICENSE.md` contém a licença. `maze.txt` é
um resultado gerado localmente, não a fonte das regras do gerador.

## 4. Como usar a API em outro código

O pacote exporta `MazeGenerator` em `mazegen/__init__.py`. Um consumidor pode
criar uma grade sem iniciar a CLI ou importar a visualização:

```python
from mazegen import MazeGenerator

maze = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_pos=(19, 14),
    perfect=False,
    seed=42,
)
maze.generate()

grid = maze.get_grid()                    # indexação: grid[y][x]
route = maze.get_solution_path()          # lista de coordenadas (x, y)
maze.save_to_file("maze.txt")
```

Com uma seed fixa e uma mesma configuração, a sequência inicial gerada é
reproduzível. Para o jogo futuro, a grade fornece topologia e paredes. O
consumidor ainda terá de associar posições a pellets, energizadores, jogador,
fantasmas e demais regras próprias do jogo; essas entidades não fazem parte
desta API.

## 5. Comandos de projeto e conferência

O `Makefile` concentra os comandos previstos:

```sh
make install   # instala ferramentas de desenvolvimento
make run       # executa usando config.txt
make debug     # inicia pelo pdb
make lint      # executa flake8 e mypy
make build     # monta wheel e source distribution
make clean     # remove caches e artefatos de build
```

O analisador disponibilizado na raiz deste workspace pode conferir um arquivo
gerado a partir da raiz do projeto:

```sh
python3 maze_analyzer.py submission_clone/maze.txt
```

O analisador confirma propriedades do resultado salvo. Para entender por que
elas são garantidas pelo código, acompanhe `generator.py`, `rules.py` e
`validation.py` conforme a ordem deste guia.

## 6. Duas distinções úteis ao apresentar o projeto

1. “Pac-Man” aqui significa o conjunto de regras de labirinto descrito na
   subject: conectividade, rotas alternativas, becos sem saída raros e cantos
   e centro utilizáveis. A API não implementa o jogo Pac-Man nem posiciona
   seus personagens ou itens.
2. O padrão 42 é desenhado com células completamente fechadas. Essas células
   são intencionalmente excluídas da região de corredores conectados.

Há uma divergência documental a conferir: o bloco de configuração do README
mostra `WIDTH=200`, enquanto o `config.txt` atual e o arquivo gerado têm largura
20. Este guia descreve a configuração executável atual (`20 × 15`).
