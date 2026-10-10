# Guia Passo a Passo: Refazendo o A-Maze-ing do Zero

Este guia documenta o processo arquitetural e de implementação necessário para construir o projeto **A-Maze-ing** do zero, alcançando 100% de conformidade com os requisitos da 42, além de gabaritar os bônus.

## Fase 1: Setup do Projeto e Arquitetura

1. **Estrutura de Diretórios:**
   Separe o script CLI da lógica de negócios criando um pacote independente.
   ```text
   submission/
   ├── a_maze_ing.py
   ├── Makefile
   ├── pyproject.toml
   ├── setup.cfg
   └── mazegen/
       ├── __init__.py
       ├── types.py
       ├── algorithms.py
       ├── pattern42.py
       ├── solver.py
       ├── generator.py
       ├── parser.py
       └── renderer.py
   ```
2. **Ambiente Virtual e Linting:**
   Utilize `flake8` para o estilo de código (PEP-8) e `mypy --strict` para tipagem estática.
   O arquivo `setup.cfg` centraliza a configuração, ignorando pacotes sem stubs (como o `mlx`).

## Fase 2: Domínio e Parsing

1. **Definições de Tipos (`types.py`):**
   Utilize bitmasks para representar paredes!
   - `NORTH = 1`, `EAST = 2`, `SOUTH = 4`, `WEST = 8`.
   - Células isoladas começam com valor `15` (todas as paredes fechadas).
2. **Parser Seguro (`parser.py`):**
   Crie uma função robusta para extrair as variáveis do `config.txt`. Certifique-se de validar a conversão de `ENTRY` e `EXIT` (x,y) e capturar exceções, prevenindo que o sistema caia de forma abrupta.

## Fase 3: Geração de Labirintos Perfeitos (Engine Base)

1. **Algoritmos (`algorithms.py`):**
   Implemente algoritmos baseados na quebra de paredes (bit operations):
   - `grid[y][x] &= ~(1 << Direction)`
   - Implemente o **DFS Iterativo (Backtracker)** utilizando uma Stack (`list`) para evitar `RecursionError` em grades gigantes.
   - Bônus: Adicione implementações do algoritmo de Prim e Kruskal (usando Union-Find).
2. **O Padrão 42 (`pattern42.py`):**
   Crie um bitmap estático `get_pattern_42()` contendo os caracteres `4` e `2`.
   Centralize na grid e demarque essas células retornando um conjunto de tuplas (`set[tuple[int, int]]`).
   Estas células NUNCA podem ser visitadas nem ter paredes abertas (são blocos maciços).

## Fase 4: O Modo Pac-Man (Braiding)

Para o modo `PERFECT=False` (Pac-Man), o labirinto **não pode ter dead-ends** (caminhos sem saída).
1. **Braiding (`generator.py`):**
   Faça um loop que escaneia toda a grid buscando células com exatamente 1 passagem aberta.
   - Para cada dead-end, identifique os vizinhos válidos.
   - Escolha aleatoriamente e derrube a parede.
   - *Cuidado:* Não quebre paredes que levam para o limite da matriz (out-of-bounds) e muito menos para dentro do padrão 42. Repita o processo até que a contagem de dead-ends caia para zero.
2. **Bordas e Centro (`_ensure_pacman_layout`):**
   Force a abertura de corredores nos quatro cantos da matriz e no centro geográfico, permitindo fluxo constante sem engarrafamentos.

## Fase 5: Solucionador (BFS)

1. **Shortest Path (`solver.py`):**
   Para salvar no arquivo e para renderização visual, calcule o caminho mais curto usando Breadth-First Search (BFS) em uma `collections.deque`.
   Armazene os "parents" (pais) das células visitadas para conseguir reconstruir o caminho de trás para frente.

## Fase 6: Renderização Gráfica com MiniLibX

1. **A Interface `mlx` (`renderer.py`):**
   Como o MLX usa bindings primitivos, utilizar `mlx_pixel_put` célula por célula é muito lento (gargalo de CPU).
   - *Solução Otimizada:* Crie uma imagem (`mlx_new_image`) do tamanho exato da janela.
   - Obtenha o endereço de memória (`mlx_get_data_addr`) que retorna um `memoryview`.
   - Calcule o byte offset e modifique diretamente os pixels via Python manipulando os bits BGRA (Blue, Green, Red, Alpha).
   - Ao terminar a iteração de desenho, jogue o buffer final pra tela em uma única chamada usando `mlx_put_image_to_window`.
2. **Fallback:**
   Proteja os imports do `mlx` num bloco `try/except`. Caso o avaliador rode o script sem o X11 ativo (ou sem a `libmlx` compilada), desenhe o labirinto em preview ASCII no próprio terminal (`█` para paredes, `E` para entrada e `X` para saída).

## Conclusão e Testes Finais

Rode `maze_analyzer.py --max-dead-ends 0` no seu labirinto gerado.
1. Se as regras de coerência falharem, revise as operações bitwise (o bit NORTE da célula atual precisa quebrar junto com o bit SUL do vizinho de cima).
2. Se o lint falhar, valide se adicionou typehints (ex: `list[tuple[int, int]]`) a todas as coleções do projeto e garantiu `return type` e docstrings.
