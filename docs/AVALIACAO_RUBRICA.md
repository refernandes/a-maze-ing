# Auditoria da régua de avaliação — A-Maze-ing

Data da auditoria: 2026-09-27

Este documento avalia o conteúdo de `submission/` como se ele fosse a raiz do
repositório entregue. A auditoria do vínculo com o Git oficial, do login do
grupo e de aliases maliciosos não é possível neste workspace: não há metadados
`.git` disponíveis.

## Veredito curto

Tecnicamente, o código atende à parte obrigatória e os três bônus explícitos
do enunciado foram encontrados e testados:

- gerador padrão não perfeito sem dead-end real;
- três algoritmos de geração;
- animação de geração no renderer Tkinter.

Portanto, a expectativa defensável é **100/100 na parte obrigatória + 15/25
em bônus = 115/125**, antes de o avaliador decidir se aceita bônus adicionais.
**125/125 não é garantido**: seriam necessários cinco bônus avaliados com nota
5/5, e alguns itens da régua são discricionários.

O README foi atualizado para incluir os dois logins (`rfernan` e `phkaway-`),
os papéis, uma seção explícita “What could be improved” e o passo a passo do
virtualenv. A equipe deve confirmar que a divisão de papéis documentada
corresponde à contribuição histórica real antes de entregar.

## Resultados executados

Os seguintes testes foram executados contra `submission/`:

| Verificação | Resultado observado |
|---|---|
| `python3 a_maze_ing.py config.txt` | exit 0; gera e exibe o labirinto |
| `python3 a_maze_ing.py config_pacman.txt` | exit 0; gera e exibe o modo Pac-Man |
| `maze_analyzer.py submission/maze.txt` | perfeito; 0 loops; paredes coerentes |
| `maze_analyzer.py submission/maze_pacman.txt` | 34 loops; 0 dead-ends reais; paredes coerentes |
| `flake8 --jobs 1 .` | passou |
| `mypy . --strict` | passou: 9 arquivos, sem erros |
| mypy com as flags obrigatórias + `--no-incremental` | passou |
| reconstrução com `python3 -m build --no-isolation` | gerou wheel e sdist |
| instalação do wheel em virtualenv novo | passou; o CLI instalado gerou `maze.txt` |
| 18 combinações de modo, algoritmo e seed | passaram; mesma seed reproduziu a mesma grade |
| configurações inválidas solicitadas pela régua | todas terminaram com exit 1 e mensagem clara |
| caminho do footer | conferido contra BFS e contra a movimentação no grid |

O `flake8 .` normal foi bloqueado neste sandbox ao tentar criar processos
paralelos (`PermissionError` do ambiente), não por erro de lint. O comando
single-process passou. O primeiro `mypy` obrigatório também encontrou um erro
interno da versão instalada; repetido sem cache incremental passou, e o
`mypy --strict` passou.

## Respostas item a item

### Basics e Norm

**Arquivos obrigatórios — YES, tratando `submission/` como raiz.** Existem:

- `README.md`;
- `a_maze_ing.py`;
- `mazegen-1.0.0.tar.gz`;
- `mazegen-1.0.0-py3-none-any.whl`;
- `config.txt`;
- `pyproject.toml`, `Makefile`, `mazegen/` e `LICENSE.md` para reconstrução.

Evidência: [lista de arquivos da submission](.).

**Norm e mypy — YES, com ressalva ambiental.** O código passou `flake8` em
single-process e `mypy --strict`. O `Makefile` contém exatamente as regras
obrigatórias `install`, `run`, `debug`, `clean` e `lint`.

Resposta sugerida na defesa:

> “O lint obrigatório está no Makefile. Executei flake8 e mypy; também rodei
> mypy strict. O erro que apareceu no comando paralelo foi limitação do
> ambiente, não erro reportado nos arquivos.”

### README.md

**Conteúdo — YES após a atualização.** O README agora lista os logins
`rfernan` e `phkaway-`, documenta ambos os papéis, possui “What could be
improved” e explica a execução completa, incluindo virtualenv e instalação do
package.

O arquivo tem a primeira linha em itálico, `Description`, `Instructions`,
`Resources`, configuração completa, algoritmo, justificativa, documentação
do pacote, planejamento, ferramentas e uso de IA. As evidências estão em
[README.md](README.md), especialmente nas seções de configuração, algoritmo,
pacote e gestão.

O único ponto a confirmar é se os papéis descritos refletem exatamente o que
cada integrante fez, pois essa informação não pode ser deduzida com certeza
apenas do código.

### Standard usage / Display

**YES.** O comando é:

```bash
python3 a_maze_ing.py config.txt
```

O programa gera, salva e exibe o labirinto. Em TTY usa curses; com display
gráfico disponível tenta Tkinter; com stdout redirecionado usa um fallback
ASCII que não fica esperando entrada.

Resposta sugerida:

> “A execução padrão abre o renderer interativo e salva a primeira grade no
> OUTPUT_FILE. O mesmo código também tem fallback ASCII para terminal sem
> curses ou execução automatizada.”

### Interactive menu

**YES.** As três interações obrigatórias estão implementadas em
`mazegen/renderer.py`:

- `R`: gera e salva outro labirinto;
- `S`: mostra/esconde o caminho BFS;
- `C`: troca o tema/cor das paredes.

Também existem `Q`/`Esc`, toggle do `42` e toggle de animação. No Tkinter as
mesmas ações aparecem como botões.

Para demonstrar: executar em terminal real, pressionar `R`, depois `S`,
`C` e `Q`. Se houver display gráfico, demonstrar os botões.

### Configuration file — format

**YES para o formato padrão.** `config.txt` usa comentários iniciados por `#`
e linhas `KEY=VALUE`, contendo `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`,
`OUTPUT_FILE` e `PERFECT`. `SEED` e `ALGORITHM` são opcionais.

**Risco menor:** o parser exige as chaves em maiúsculas. A régua permite que o
avaliador aceite nomes em minúsculas, mas não exige necessariamente que o
programa aceite uma configuração escrita em minúsculas. Para eliminar essa
ambiguidade, usar a configuração entregue em maiúsculas ou adaptar o parser
antes da defesa.

### Error Management

**YES.** Foram testados:

- chave obrigatória removida: mensagem `Missing required key`;
- linha sem `=`: mensagem `expected KEY=VALUE`;
- `WIDTH`/`HEIGHT` com letras: mensagem de inteiros;
- `PERFECT=maybe`: mensagem de booleano;
- `ENTRY=zero`: mensagem de tupla inválida;
- coordenada fora dos limites: mensagem `Entry must be within bounds`.

Todas terminaram com status 1 e sem traceback. O parser e o `main` tratam
também arquivo inexistente, dimensões não positivas, entrada/saída iguais,
algoritmo desconhecido, seed inválida e parâmetros impossíveis.

### Output file — format

**YES.** A execução produz `HEIGHT` linhas com `WIDTH` dígitos hexadecimais,
uma linha vazia e as três linhas de footer: entrada, saída e caminho.

Em `submission/maze.txt` foram conferidos 15 x 20 cells, footer `0,0`,
`19,14` e caminho `N/E/S/W`. Em `submission/maze_pacman.txt` a mesma estrutura
foi conferida. O caminho escrito é exatamente o resultado do BFS e foi
reproduzido passo a passo até o exit.

As paredes são coerentes porque cada abertura limpa o bit dos dois lados. O
analisador fornecido pelo projeto reportou `Wall coherence: OK` nos dois
arquivos.

### Maze Generator module — generation

**YES.** A resposta sugerida é:

> “Começamos todas as cells com as quatro paredes fechadas. O gerador usa um
> `random.Random(seed)` e abre arestas com DFS iterativo, Prim ou Kruskal. A
> cada abertura os dois lados da parede são atualizados. Depois validamos
> conectividade, bordas, coerência, loops, spawns do Pac-Man e áreas abertas
> 3x3.”

Checklist técnico:

- aleatoriedade e seed: `random.Random(seed)`;
- dimensões, entry e exit inválidos: rejeitados;
- todas as cells normais alcançáveis: verificado por BFS de validação;
- bordas externas fechadas: validado;
- áreas abertas 3x3: `_contains_open_3x3_area()` rejeita;
- padrão `42`: 22 cells totalmente fechadas no mapa 20 x 15;
- mapa pequeno: imprime erro e omite o padrão, conforme o enunciado;
- `PERFECT=True`: loops devem ser zero;
- `PERFECT=False`: pelo menos dois loops, cantos e centro utilizáveis;
- mesma seed e mesmos parâmetros: mesma grade reproduzida nos 18 casos;
- DFS, Prim e Kruskal: os três foram executados com modo perfeito e Pac-Man.

O analisador observou:

- default perfeito: 278 cells alcançáveis, 0 loops, paredes coerentes;
- default Pac-Man: 278 cells alcançáveis, 34 loops, 0 dead-ends reais,
  cantos/centro alcançáveis e paredes coerentes.

### Reusable module

**YES.** `mazegen.MazeGenerator` é a classe pública. O README documenta
instanciação, parâmetros customizados, seed, `get_grid()`,
`get_solution_path()` e `save_to_file()`.

Foi reconstruído um wheel e um sdist a partir dos fontes, instalado o wheel em
um virtualenv novo e executado o `a_maze_ing.py` fora da pasta que contém o
package fonte. A execução instalada terminou com exit 0 e escreveu o arquivo
de saída.

Resposta sugerida:

> “A CLI não contém a lógica do labirinto. Ela chama `MazeGenerator`; o pacote
> pode ser instalado por pip e expõe a grade e a solução, então pode ser usado
> por um projeto futuro sem importar o renderer.”

### Bonuses

Somente os bônus devem ser avaliados depois de todos os itens anteriores.

| Bônus | Evidência | Nota defensável |
|---|---|---:|
| Pac-Man sem dead-end real | `maze_analyzer.py submission/maze_pacman.txt` reportou 0 dead-ends reais | 5/5 |
| Múltiplos algoritmos | `DFS`, `PRIM` e `KRUSKAL` no parser, package e configuração; 18 casos passaram | 5/5 |
| Animação | callback de passos no gerador e botão `Animation: ON` no Tkinter | 5/5 |
| Dois renderers | Tkinter e curses/ASCII, além do fallback sem TTY | possível 3–5/5, decisão do avaliador |
| Toggle do `42` / fallback ASCII | interações extras e execução robusta sem TTY | possível 2–5/5, decisão do avaliador |

Os três primeiros são os bônus expressamente exemplificados pelo subject e
justificam **15 pontos**. O PDF permite até cinco bônus, mas não define dois
bônus adicionais obrigatórios. Para chegar a 125, seria necessário o
avaliador aceitar mais dois trabalhos relevantes com 5/5, ou a equipe
implementar mais dois bônus claros antes da avaliação. Os dois últimos da
tabela são funcionalidades extras defensáveis, mas não devem ser prometidos
como 125: o peer pode considerá-las parte da visualização obrigatória ou não
aceitar cada uma como “fair amount of work”.

## Ordem recomendada para a defesa

1. Confirmar que o clone oficial foi feito em uma pasta vazia e que a raiz
   contém diretamente os arquivos hoje dentro de `submission/`.
2. Revisar os papéis no README e confirmar que correspondem à contribuição de
   `rfernan` e `phkaway-`.
3. Rodar `make lint-strict` e `python3 a_maze_ing.py config.txt`.
4. Abrir `config_pacman.txt`, explicar `PERFECT=False` e rodar o analisador.
5. Demonstrar `R`, `S`, `C` e `Q` em TTY.
6. Alterar temporariamente cada erro de configuração solicitado, sempre
   mostrando a mensagem e o exit status sem traceback.
7. Rodar `make build`, instalar o wheel em outro virtualenv e importar
   `MazeGenerator` pelo exemplo do README.

Não alegar que o projeto “é 125” como fato consumado. A formulação honesta é:

> “A parte funcional obrigatória está coberta e temos três bônus verificáveis,
> então a projeção é 115/125. Se o avaliador aceitar os dois extras de
> visualização, pode chegar a 125/125.”
