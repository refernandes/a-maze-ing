# Guia do código: função por função

Este guia acompanha a versão final do projeto. Ele explica o que cada arquivo,
classe, função e método faz, incluindo os trechos que compõem cada método. A
ordem começa na execução pelo terminal e segue os dados até a geração, a
validação, a solução, o arquivo de saída e a exibição.

Os nomes em inglês foram mantidos iguais aos nomes no código. Assim, é possível
usar este documento junto dos arquivos abertos no editor.

## 1. Visão geral do caminho

Ao executar:

```bash
python3 a_maze_ing.py config.txt
```

o projeto segue esta sequência:

1. `a_maze_ing.py` chama `main()`.
2. `main()` pede a `parse_config()` que leia e valide o arquivo de configuração.
3. `main()` cria um `MazeGenerator` com as dimensões, os pontos, o modo e a
   semente lidos.
4. `MazeGenerator.generate()` cria a grade, coloca o padrão 42, abre os
   corredores com DFS, aplica as regras do modo Pac-Man quando necessário e
   valida o resultado.
5. `MazeGenerator.save_to_file()` calcula a solução mais curta e grava a grade
   e os dados do percurso.
6. `main()` cria `MazeRenderer`, que mostra o resultado e responde às teclas.
7. Se a pessoa pressionar `R`, uma função local chamada `regenerate()` gera,
   valida e salva outro labirinto antes de atualizar a tela.

Há **um algoritmo de geração de labirintos**: DFS iterativo, implementado em
`generate_dfs()`. O modo Pac-Man abre passagens adicionais depois da árvore
inicial; esse processo é chamado de *braiding* e é uma etapa de ajuste da
grade. O projeto também usa BFS para encontrar o caminho mais curto. BFS é o
algoritmo de solução, não um segundo algoritmo de geração.

## 2. Representação que os arquivos compartilham

Antes de ler as funções, é útil entender como uma célula guarda suas paredes.
Cada célula é um inteiro de quatro bits:

| Direção | Valor | Bit ligado significa |
|---|---:|---|
| Norte | 1 | Parede norte fechada |
| Leste | 2 | Parede leste fechada |
| Sul | 4 | Parede sul fechada |
| Oeste | 8 | Parede oeste fechada |

Um bit desligado significa passagem aberta. A célula `15`, ou `0xF`, tem os
quatro bits ligados e começa completamente fechada. A grade é uma lista de
linhas: o acesso é `grid[y][x]`, embora as coordenadas públicas sejam escritas
como `(x, y)`.

Quando uma passagem é aberta, os dois lados da mesma parede precisam ser
atualizados. Por exemplo, abrir a parede leste de `(x, y)` também abre a parede
oeste de `(x + 1, y)`. Essa regra é compartilhada pelo gerador, pelo solver e
pelas validações.

## 3. Entrada do programa: `a_maze_ing.py`

### `main()`

É o ponto de entrada da aplicação e faz a ligação entre configuração,
geração, arquivo e interface. A função não implementa o algoritmo do
labirinto; ela coordena os módulos responsáveis por cada tarefa.

#### 3.1 Conferência dos argumentos

```python
if len(sys.argv) != 2:
    print("Usage: python3 a_maze_ing.py config.txt")
    sys.exit(1)
```

O programa espera exatamente um argumento depois do nome do script: o caminho
do arquivo de configuração. Se faltar o caminho ou houver argumentos extras,
ele mostra como deve ser executado e encerra com código de erro.

#### 3.2 Leitura da configuração

```python
try:
    config = parse_config(sys.argv[1])
except (FileNotFoundError, ValueError, OSError) as exc:
    print(f"Error: {exc}")
    sys.exit(1)
```

O caminho fornecido vai para `parse_config()`. Erros de sintaxe, valores
inválidos, arquivo ausente ou falha de leitura são apresentados como uma
mensagem e encerram a aplicação. A geração ainda não começou nessa parte.

#### 3.3 Criação, geração e gravação inicial

Dentro do segundo `try`, `main()` passa cada campo do dicionário `config` ao
construtor `MazeGenerator(...)`. Em seguida:

```python
gen.generate()
gen.save_to_file(config["output_file"])
```

`generate()` monta e valida a grade. Só depois de uma geração bem-sucedida,
`save_to_file()` escreve o arquivo configurado. A mensagem `Maze saved to ...`
confirma qual caminho foi usado.

#### 3.4 Função local `regenerate()`

`regenerate()` fica definida dentro de `main()`. Ela reaproveita o mesmo objeto
`gen` quando o usuário pede outro resultado:

1. chama `gen.generate()` para começar uma nova geração;
2. grava o novo labirinto no mesmo `OUTPUT_FILE`;
3. devolve uma cópia da grade e o caminho calculado.

Por estar dentro de `main()`, a função usa `gen` e `config` sem precisar
recebê-los como argumentos. O renderer recebe `regenerate` como callback e o
chama ao detectar `R`.

#### 3.5 Criação do renderer e tratamento final de erros

`MazeRenderer(...)` recebe a grade, dimensões, entrada, saída, solução, células
do padrão 42 e o callback. `renderer.run()` inicia a interface. A exceção
abrangente do segundo `try` transforma falhas de geração, gravação ou
renderização em uma mensagem `Error: ...` seguida de encerramento com código
de erro.

Por fim, o bloco:

```python
if __name__ == "__main__":
    main()
```

chama `main()` quando o arquivo é executado diretamente. Ao importar
`a_maze_ing.py` como módulo, esse bloco não inicia a aplicação.

## 4. Tipos e API pública: `mazegen/types.py` e `mazegen/__init__.py`

### `Direction`

`Direction` é um `IntEnum`: cada nome de direção tem um valor inteiro que
corresponde à posição do bit da parede. Por exemplo, `Direction.NORTH` vale 0,
e a máscara da parede norte é calculada como `1 << Direction.NORTH`, isto é,
1. Usar nomes torna o restante do código mais claro do que espalhar números
soltos.

### `MazeConfig`

`MazeConfig` é um `TypedDict`, ou seja, descreve o formato do dicionário
produzido pelo parser. Ele declara os tipos de `width`, `height`, `entry`,
`exit_pos`, `perfect`, `output_file` e `seed`. Não cria um objeto de
configuração em tempo de execução nem realiza validação por conta própria.

### Constantes compartilhadas

- `ALL_WALLS` vale `0x0F`: os quatro bits de parede ligados.
- `DELTA` associa cada direção ao deslocamento `(dx, dy)` usado para chegar à
  célula vizinha. Norte diminui `y`; leste aumenta `x`.
- `OPPOSITE` associa cada direção à direção contrária. É usada para manter
  coerência quando uma parede compartilhada é aberta ou conferida.
- `DIRECTION_CHARS` associa as direções às letras `N`, `E`, `S` e `W` gravadas
  no rodapé do arquivo.

### `mazegen/__init__.py`

O pacote importa `MazeGenerator`, `Direction` e `MazeConfig` no nível superior.
`__version__` informa a versão `1.0.0`; `__all__` declara os nomes que formam
a API pública. Por isso, um consumidor pode escrever
`from mazegen import MazeGenerator` sem importar o módulo interno diretamente.

## 5. Leitura e validação da configuração: `mazegen/parser.py`

### `parse_config(filename)`

Lê o texto do arquivo e devolve um `MazeConfig`. Sua execução pode ser dividida
em etapas.

#### 5.1 Verificar e abrir o arquivo

Primeiro, `os.path.exists(filename)` verifica se o caminho existe. Depois,
`open(..., encoding="utf-8")` lê o arquivo com a codificação definida. Se o
caminho não existir, o parser levanta `ValueError`; falhas de acesso podem
levantar `OSError`, que `main()` apresenta.

#### 5.2 Transformar as linhas em pares

O `for` enumera as linhas começando pelo número 1, para que mensagens de erro
possam apontar a linha correta. `strip()` remove espaços ao redor. Linhas
vazias e linhas cujo primeiro caractere não branco é `#` são ignoradas.

Cada outra linha precisa conter `=`. `split("=", 1)` divide apenas na primeira
ocorrência: assim, o valor pode conter outros sinais de igual. A chave é
removida de espaços e convertida para maiúsculas; o valor é removido de espaços
e guardado como texto. Chave vazia e chave repetida são rejeitadas.

#### 5.3 Exigir as chaves obrigatórias

O parser confere a presença de `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`,
`OUTPUT_FILE` e `PERFECT`. `SEED` é opcional. Uma chave obrigatória ausente
gera uma mensagem que identifica seu nome.

#### 5.4 Converter dimensões

`int()` transforma `WIDTH` e `HEIGHT` em inteiros. Letras ou outros valores
não numéricos causam um `ValueError` com uma mensagem mais clara. Depois, o
parser rejeita zero e valores negativos. A verificação de limites de entrada e
saída depende também das dimensões e é feita por `MazeGenerator`.

#### 5.5 Função interna `parse_coord(s)`

Essa função recebe uma coordenada de texto, como `19,14`. `split(",")` deve
produzir exatamente duas partes. Cada parte é limpa e convertida para `int`,
e o resultado é uma tupla `(x, y)`. A função é interna porque só é necessária
para interpretar `ENTRY` e `EXIT` neste parser.

As duas chamadas ficam dentro de um `try`: um formato inválido é apresentado
como erro de `ENTRY` ou `EXIT`. Depois, o parser rejeita coordenadas iguais.
O limite superior ainda não é conferido aqui, pois o parser verifica apenas o
formato; o gerador conhece as dimensões e consegue fazer essa validação.

#### 5.6 Converter modo, saída e semente

`PERFECT` é convertido para maiúsculas e só aceita `TRUE` ou `FALSE`. O
resultado é um `bool`. `OUTPUT_FILE` precisa ter algum conteúdo. Se existir
`SEED`, o parser o converte para inteiro; se não existir ou estiver vazio, o
valor retornado será `None`.

Ao final, o dicionário devolvido usa nomes internos em minúsculas. Isso separa
a forma escrita no arquivo (`WIDTH`) dos nomes usados no Python (`width`).

## 6. Desenho isolado “42”: `mazegen/pattern42.py`

### `get_pattern_42()`

Define o desenho como uma lista de strings. `#` representa uma célula que
participa do desenho; `.` e espaços são apenas posições vazias dentro do
retângulo do padrão. Dois loops transformam cada caractere em `1` ou `0`,
produzindo uma matriz de inteiros. A função descreve o bitmap, sem conhecer o
tamanho do labirinto nem alterar uma grade.

### `compute_pattern_cells(grid_width, grid_height)`

Obtém o bitmap e calcula suas dimensões. A margem mínima é 2 células em cada
lado. Se a grade for pequena demais, imprime uma mensagem de erro em inglês no
`stderr` e devolve um conjunto vazio. Isso segue a regra que permite omitir o
padrão quando a grade não comporta o desenho.

Quando há espaço, `start_x` e `start_y` posicionam o bitmap no centro. Dois
loops percorrem suas linhas e colunas; só as posições marcadas com `1` são
transformadas em coordenadas `(x, y)` e incluídas no conjunto retornado.

### `stamp_pattern_42(grid, pattern_cells)`

Recebe a grade e as coordenadas calculadas. Para cada `(x, y)`, define
`grid[y][x] = 15`. Assim, as células do desenho ficam com todas as paredes
fechadas. O DFS recebe essas coordenadas como bloqueadas e não as transforma
em corredores.

## 7. Geração inicial: `mazegen/algorithms.py`

### `generate_dfs(...)`

Implementa busca em profundidade iterativa. Ela recebe a grade, dimensões,
célula inicial, conjunto de células bloqueadas e um objeto `random.Random`.
O objeto aleatório é fornecido pelo gerador para que a semente controle as
escolhas.

#### 7.1 Início e pilha

Se a posição inicial estiver bloqueada pelo padrão, a função retorna. Caso
contrário, cria `visited` com a célula inicial e uma pilha que começa nela.
Essa pilha substitui a recursão: a última célula colocada é a próxima que a
busca examina.

#### 7.2 Escolha de vizinhos

Enquanto a pilha não estiver vazia, a função olha a célula no topo. Para cada
direção em `DELTA`, calcula `(nx, ny)` e mantém apenas vizinhos que estejam
dentro da grade, não pertençam ao padrão e ainda não tenham sido visitados.

Se não houver vizinhos válidos, remove a célula do topo. Isso é o
retrocesso: a busca volta à célula anterior. Se houver opções, `rng.choice()`
escolhe uma ao acaso. A função desliga os bits de parede nos dois lados da
passagem, marca o vizinho como visitado e o empilha.

Esse processo constrói uma árvore de passagens: cada nova célula é conectada à
parte já visitada por uma aresta, sem abrir ciclos durante essa etapa.

#### 7.3 Segunda varredura depois das células bloqueadas

O desenho 42 pode dividir o espaço livre em regiões. Depois do primeiro DFS,
uma varredura procura células livres que ainda não foram visitadas. Se uma
delas tocar uma célula visitada, abre a passagem entre as duas, marca a célula
e percorre a região com a mesma estratégia de pilha e escolhas aleatórias.
Essa etapa procura ligar as regiões transitáveis separadas pelo padrão, sem
abrir as próprias células bloqueadas.

## 8. Gerador e regras: `mazegen/generator.py`

### Classe `MazeGenerator`

É o centro da lógica reutilizável. A classe recebe os parâmetros do labirinto,
constrói a grade, coordena o algoritmo, aplica regras, verifica o resultado,
expõe cópias dos dados e grava o arquivo. Ela não lê `config.txt` nem desenha a
tela.

### `__init__(...)`

O construtor verifica se largura e altura são positivas, se entrada e saída
são diferentes e se ambas estão dentro dos limites. Se algo estiver errado,
levanta `ValueError` antes de reservar a grade.

Depois, guarda os parâmetros em atributos privados, cria `random.Random(seed)`
e inicializa a matriz com `ALL_WALLS`. Cada linha contém `width` células e há
`height` linhas. O conjunto do padrão começa vazio; `generate()` o calcula.

### `generate()`

É o caminho principal para criar uma nova versão do labirinto. Cada chamada
reinicia a grade para que `R` não continue trabalhando sobre a geração
anterior.

1. recria todas as células fechadas;
2. calcula e marca as células do padrão 42;
3. rejeita entrada ou saída dentro desse padrão isolado;
4. chama `generate_dfs()` a partir da entrada;
5. se `perfect` for falso, chama `_braid()` e `_ensure_pacman_layout()`;
6. fecha as bordas externas com `_validate_borders()`;
7. valida a grade final com `_validate_generated_maze()`.

No modo perfeito, a árvore criada pelo DFS é mantida sem a etapa de abrir
ciclos. No modo Pac-Man, o pós-processamento acrescenta rotas alternativas e
ajusta posições de jogo antes das validações finais.

### `_braid()`

Procura becos sem saída, definidos como células transitáveis com exatamente
uma passagem para um vizinho interno. Células do padrão são puladas. Para cada
beco, reúne paredes fechadas que poderiam ser abertas sem sair da grade nem
invadir o 42.

`_rng.shuffle()` muda a ordem das tentativas sem perder a reprodutibilidade da
semente. Cada opção é passada para `_try_open_edge()`. O método repete a busca
enquanto ainda encontra becos e consegue mudar a contagem. Se todas as
aberturas possíveis violarem a regra de áreas 3x3, ele para; manter uma
restrição válida é mais importante que prometer zero becos em todos os
formatos.

### `_ensure_pacman_layout()`

Monta as quatro coordenadas de canto e a coordenada central inteira `(width //
2, height // 2)`. Para cada posição, ignora células fora da grade e células
bloqueadas pelo 42. Conta as passagens internas abertas. Se a posição ainda
estiver cercada por pelo menos duas paredes, reúne paredes internas que podem
ser abertas e tenta cada uma por `_try_open_edge()`.

Essa função tenta dar acesso aos cantos e ao centro. A checagem final mais
completa é feita por `_validate_pacman_spawn_cells()`, que também trata o
centro geométrico de grades com dimensões pares.

### `_try_open_edge(x, y, direction)`

É a única etapa que abre uma parede adicional no braiding e no ajuste das
posições Pac-Man. Primeiro calcula o vizinho e rejeita coordenadas fora da
grade ou células do 42. Depois guarda os dois valores antigos da grade e
desliga os bits correspondentes nos dois lados da parede.

Com a abertura provisória, chama `_contains_open_3x3_area()`. Se surgir uma
área totalmente aberta de 3x3, restaura os dois valores antigos e retorna
`False`. Caso contrário, deixa a passagem aberta e retorna `True`. Guardar os
valores torna o desfazer simples e evita alterar apenas um lado da parede.

### `_validate_borders()`

Percorre a primeira e a última linha para fechar norte e sul. Depois percorre
as colunas laterais para fechar oeste e leste. Usa OR bit a bit para ligar os
bits externos sem mudar as paredes internas. A entrada e a saída continuam
sendo células dentro do quadro; não são aberturas para fora da grade.

### `_open_neighbours(cell)`

Devolve as coordenadas dos vizinhos que podem ser alcançados por uma passagem.
Para cada direção, verifica limites, parede da célula atual e parede oposta do
vizinho. Só retorna a posição se os dois bits indicarem passagem aberta.
Assim, uma parede inconsistente de um só lado não vira uma conexão válida nas
checagens de conectividade.

### `_validate_generated_maze()`

Cria `normal_cells` com todas as posições da grade exceto as células isoladas
do 42. Em seguida, chama `_validate_connectivity()` e
`_validate_wall_consistency()`. Conta os ciclos com `_count_loops()`:

- no modo perfeito, a contagem precisa ser zero;
- no modo Pac-Man, precisa ser pelo menos dois.

O modo Pac-Man também chama `_validate_pacman_spawn_cells()`. Por fim,
`_contains_open_3x3_area()` precisa retornar falso. Qualquer violação levanta
`ValueError` em vez de salvar uma grade inválida.

### `_validate_connectivity(normal_cells)`

Faz uma busca em largura começando na entrada. Mantém uma fila `deque` e um
conjunto `reachable`. Para cada célula retirada da fila, usa
`_open_neighbours()` e adiciona à fila os vizinhos ainda não visitados.

Quando a fila termina, compara `reachable` com `normal_cells`. Se houver
diferença, informa quantas células não foram alcançadas. Também verifica
explicitamente a saída. As células do desenho 42 são a exceção prevista: não
são corredores e por isso não entram no conjunto transitável esperado.

### `_validate_wall_consistency()`

Percorre cada célula e compara somente as arestas leste e sul. Essa escolha
confere cada parede interna uma vez: a parede leste é comparada com o oeste do
vizinho, e a sul com o norte da célula abaixo. Se os dois bits de uma parede
compartilhada discordarem, levanta um erro.

### `_count_loops(normal_cells)`

Conta arestas abertas entre células transitáveis. Examina apenas leste e sul
para não contar cada passagem duas vezes. Como a conectividade já foi
validada, o número de ciclos independentes é `edges - vertices + 1`, onde
`vertices` é o número de células normais. Uma árvore tem zero ciclos; cada
passagem adicional que fecha um circuito aumenta a contagem em um.

### `_validate_pacman_spawn_cells()`

Confere se cada canto está fora do padrão e tem ao menos um vizinho aberto.
Para o centro, cria conjuntos de linhas e colunas centrais. Em uma dimensão
ímpar, há uma posição central; em uma dimensão par, há duas candidatas mais
próximas do centro. O produto desses conjuntos forma as células centrais a
conferir. Basta uma candidata livre do padrão e conectada para o centro ser
considerado utilizável.

### `_contains_open_3x3_area()`

Percorre todas as posições possíveis de um bloco 3x3. Para cada bloco, testa
as passagens horizontais entre suas colunas e as verticais entre suas linhas.
`horizontal_open` só é verdadeiro quando todas as paredes horizontais internas
estão abertas; `vertical_open` faz o equivalente para as paredes verticais.
Se ambos forem verdadeiros, aquele bloco não tem nenhuma parede interna e a
função retorna `True`. Se nenhum bloco satisfizer as duas condições, retorna
`False`.

### `save_to_file(filename)`

Calcula a solução chamando `solve_bfs()` sobre a grade final. É importante
calcular depois do braiding: uma passagem adicional pode mudar qual é o
caminho mais curto.

Depois escreve uma linha por linha da grade. `f"{c:X}"` converte cada máscara
para um dígito hexadecimal maiúsculo. Uma linha vazia separa a grade do rodapé;
depois vêm coordenadas da entrada, coordenadas da saída e a sequência de
direções separadas por vírgula.

### `get_grid()`

Devolve uma nova lista externa e novas listas para cada linha (`row[:]`). Assim,
quem usa a API pode ler ou alterar a cópia sem alterar diretamente a grade
interna do gerador.

### `get_solution_path()`

Chama `solve_bfs_path()` com a grade e os pontos guardados. Devolve a rota como
uma lista de coordenadas começando na entrada e terminando na saída.

### `get_pattern_cells()`

Devolve uma cópia do conjunto de coordenadas do padrão. A cópia impede que um
consumidor remova ou acrescente células no conjunto mantido pelo gerador.

## 9. Busca pelo caminho mais curto: `mazegen/solver.py`

As funções de solver tratam cada corredor como uma aresta de mesmo custo. Por
isso BFS encontra uma rota com o menor número de movimentos. Elas leem a grade
e não abrem paredes.

### `solve_bfs_path(...)`

É a função central do solver e devolve coordenadas. Primeiro confere se início
e fim estão dentro dos limites; fora da grade, devolve uma lista vazia.

Em seguida cria uma fila com `start`, um conjunto `visited` e um dicionário
`parent`. A fila processa primeiro as células descobertas há mais tempo. Para
cada célula, a função para quando chega a `end`; caso contrário, examina cada
direção cuja parede esteja aberta. Também confere a parede oposta no vizinho,
para ignorar ligações inconsistentes.

Ao descobrir um vizinho, marca-o antes de enfileirar e registra de qual célula
veio em `parent`. Isso impede visitas repetidas e guarda informação suficiente
para reconstruir o percurso. Se a busca acabar sem encontrar o destino, retorna
lista vazia. Se encontrar, percorre `parent` do fim até o início, acrescenta
cada coordenada, depois inverte a lista.

### `solve_bfs_directions(...)`

Usa `solve_bfs_path()` e compara cada par consecutivo de coordenadas. A
diferença `(dx, dy)` identifica o movimento feito. A tabela `DELTA` encontra a
direção correspondente e `DIRECTION_CHARS` a transforma em `N`, `E`, `S` ou
`W`. O resultado é uma lista de letras.

### `solve_bfs(...)`

É um adaptador para o formato de texto. Chama `solve_bfs_directions()` e junta
as letras com `", "`. É essa versão que `save_to_file()` usa no rodapé.

## 10. Renderização e controles: `mazegen/renderer.py`

### Classe `MazeRenderer`

Guarda os dados já gerados e cuida da apresentação. Não gera corredores por
conta própria: para isso usa o callback recebido no construtor.

### `__init__(...)`

Guarda grade, dimensões, pontos, solução, células 42 e callback. Inicializa
`show_solution` como falso para esconder a solução no primeiro desenho e
`theme_idx` como zero para escolher a primeira cor da lista.

### `run()`

É a entrada pública do renderer. Encaminha a execução para
`_run_curses_or_ascii()` sem expor os detalhes da escolha de interface a
`main()`.

### `_run_curses_or_ascii()`

Verifica `sys.stdout.isatty()`. Se a saída não estiver ligada a um terminal,
chama `_ascii_fallback()` e termina; não há teclado interativo nesse caso.

Com um terminal, importa `curses` e executa `_curses_main()` por meio de
`curses.wrapper()`. O wrapper prepara o terminal e restaura o estado ao sair.
Se a inicialização do curses falhar, a função escreve a causa em `stderr` e
mostra a versão ASCII estática.

### `_curses_main(stdscr)`

Configura o terminal e mantém o ciclo de desenho e leitura de teclas.

#### Preparação e função local `put()`

Tenta esconder o cursor, ativa a leitura de teclas especiais com `keypad`, e
inicializa cores. A função local `put(row, column, text, attr)` chama
`stdscr.addstr()`. Se o curses rejeitar uma escrita na borda da janela, ela
ignora `curses.error` para que o renderer não encerre por causa de um caractere
fora da tela.

#### Conferência do tamanho do terminal

No começo de cada ciclo, `getmaxyx()` fornece altura e largura disponíveis. A
grade precisa de `4 * width + 4` colunas e `2 * height + 4` linhas: cada célula
usa quatro posições horizontais e duas linhas verticais, além das margens do
desenho.

Se não couber, o renderer mostra as dimensões exigidas e atuais e pede que a
pessoa aumente a janela ou reduza o labirinto. `Q` encerra; outra tecla volta
ao início do ciclo para conferir o tamanho de novo. O gerador não impõe um
limite máximo de grade por causa dessa tela.

#### Desenho e cores

Com espaço suficiente, o renderer escreve título e controles. Chama
`_ascii_lines()` para desenhar as paredes. Depois percorre cada célula e usa
`_cell_marker()` para decidir se deve desenhar entrada, saída, padrão ou
solução. Entrada e saída recebem cores próprias; células da solução recebem
azul; as paredes usam a cor do tema atual.

#### Leitura das teclas

Depois de atualizar a tela, `getch()` espera uma tecla:

- `Q`, `q` ou `Esc`: encerra;
- `R` ou `r`: chama o callback, substitui grade e solução;
- `S` ou `s`: alterna `show_solution`;
- `C` ou `c`: avança o índice de cor e atualiza a cor das paredes.

### `_cell_marker(position, solution)`

Escolhe o texto de três caracteres para uma célula. A ordem dá prioridade a
entrada e saída, depois ao padrão 42 e, por fim, ao caminho quando ele está
visível. Células sem marcador retornam três espaços; o desenho de paredes
continua vindo das outras funções.

### `_horizontal_line(row)`

Monta uma linha de junções `+` e segmentos `---` ou espaços. Na primeira linha
usa as paredes norte; na última usa sul; nas linhas internas usa as paredes
sul da linha de células acima. A máscara determina se o segmento fica fechado
ou aberto.

### `_middle_line(row, solution)`

Monta uma linha de conteúdo das células. Começa com a parede oeste da primeira
célula. Para cada célula, acrescenta o marcador; depois desenha a parede leste
se a célula atual ou a seguinte indicar que a parede compartilhada está
fechada. O resultado mantém os marcadores alinhados com `_horizontal_line()`.

### `_ascii_lines(show_solution)`

Constrói toda a imagem como lista de strings. Para cada linha da grade,
acrescenta uma linha horizontal e uma linha de conteúdo. No final acrescenta a
borda inferior. Se `show_solution` for verdadeiro, cria o conjunto da rota e
passa-o aos marcadores.

### `_ascii_fallback()`

Imprime cabeçalho e legenda, depois imprime as linhas de
`_ascii_lines(show_solution=True)`. Mostrar a solução no modo estático permite
ver o percurso quando não há teclado para alterná-la.

## 11. Uma leitura completa, do comando à tela

Este resumo junta as responsabilidades sem misturar os módulos:

```text
terminal
  -> a_maze_ing.main()
  -> parser.parse_config()
  -> MazeGenerator(...)
  -> MazeGenerator.generate()
       -> pattern42.compute_pattern_cells()
       -> pattern42.stamp_pattern_42()
       -> algorithms.generate_dfs()
       -> [modo Pac-Man: _braid() e _ensure_pacman_layout()]
       -> validações de grade e regras
  -> MazeGenerator.save_to_file()
       -> solver.solve_bfs()
            -> solve_bfs_directions()
                 -> solve_bfs_path()
  -> MazeRenderer.run()
       -> curses ou ASCII estático
       -> [R: callback regenerate() volta à geração]
```

## 12. Exemplo de uso da API reutilizável

Um projeto futuro pode usar o gerador sem chamar a CLI:

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_pos=(19, 14),
    perfect=True,
    seed=42,
)
generator.generate()

grid = generator.get_grid()
solution = generator.get_solution_path()
pattern = generator.get_pattern_cells()
generator.save_to_file("maze.txt")
```

O consumidor escolhe dimensões, entrada, saída, modo e semente. Depois de
`generate()`, pode acessar a grade, o caminho e o padrão, ou pedir ao gerador
que salve o formato de arquivo do projeto.
