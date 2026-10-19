# Correções da auditoria — `submission_v2`

> Estado atual: a entrega usa somente `config.txt`. Para avaliar os dois
> modos, altere `PERFECT` entre `True` e `False` e execute o mesmo comando.
> As referências a `config_pacman.txt` abaixo registram a organização
> anterior e não são instruções atuais.

Cada caixa marcada registra uma correção feita nesta cópia. O motivo foi
mantido ao lado da mudança para que uma revisão futura consiga entender por
que ela existe. A pasta `submission/` original não foi editada.

## Itens corrigidos

- [x] **Adicionar `.gitignore` na raiz.** O subject recomenda ignorar caches,
  bytecode, ambientes virtuais e artefatos de build. Antes, o único arquivo
  estava em `docs/` e não protegia a raiz. Criei `submission_v2/.gitignore`
  com essas regras e removi o arquivo local redundante de `docs/`.
- [x] **Colocar a configuração do flake8 na raiz.** `docs/.flake8` não era
  descoberta quando o comando era executado a partir da raiz. Movi a
  configuração para `submission_v2/.flake8` e removi a cópia dentro de `docs/`.
- [x] **Completar docstrings ausentes.** O subject exige docstrings para
  classes e funções. Documentei `parse_coord` e os callbacks Tkinter que
  estavam sem docstring; também ampliei a documentação dos helpers novos com
  seus parâmetros e resultados.
- [x] **Aceitar nomes de configuração em minúsculas.** A régua diz que o
  formato `KEY=VALUE` também pode usar letras minúsculas. Agora o parser
  converte toda chave para maiúsculas antes de validar e armazenar. Com isso,
  `width=20` equivale a `WIDTH=20`, e chaves duplicadas com capitalizações
  diferentes continuam sendo rejeitadas.
- [x] **Corrigir o comando Pac-Man do guia.** O arquivo fica em
  `docs/config_pacman.txt`; atualizei `docs/APRESENTACAO.md` para usar esse
  caminho a partir da raiz.
- [x] **Dar referências específicas no README.** A régua pede referências
  externas e como foram usadas. Acrescentei links diretos para as
  demonstrações de Jamis Buck e para a documentação Python 3.10 de `random`,
  `deque`, `curses`, Tkinter e setuptools, relacionando cada fonte à parte do
  projeto em que foi usada.
- [x] **Facilitar a leitura do fluxo principal.** A auditoria apontou métodos
  longos e duas implementações de BFS. Extraí o caminho de células para
  `solve_bfs_path()` e fiz o footer obter as direções a partir do mesmo
  resultado; removi o BFS duplicado de `MazeGenerator`. Também separei o
  desenho Tkinter em pequenas funções para colorir células, desenhar paredes,
  marcar entrada/saída e atualizar o canvas. O README ganhou uma sequência de
  leitura em linguagem direta.
- [x] **Não ocultar falhas de inicialização dos renderizadores.** A auditoria
  observou que exceções amplas levavam a um fallback sem explicação. Mantive o
  fallback para terminais sem suporte, mas agora o motivo é escrito em stderr
  antes de trocar para curses ou ASCII.
- [x] **Preservar o histórico sem apresentar o relatório antigo como atual.**
  Mantive `docs/AVALIACAO_RUBRICA.md`, mas acrescentei uma nota inicial que o
  identifica como registro anterior e aponta para este checklist. Assim, as
  razões e conclusões históricas não são apagadas nem confundidas com o estado
  desta cópia.
- [x] **Manter somente DFS para gerar labirintos.** A revisão confirmou que o
  subject exige escolher e explicar um algoritmo; Prim e Kruskal aparecem como
  bônus opcionais. Removi essas implementações, `UnionFind`, o enum `Algorithm`,
  a chave `ALGORITHM` e a seleção correspondente no parser e no gerador. A
  aplicação agora tem um único caminho de geração, usando DFS iterativo. Isso
  reduz código e opções sem retirar um requisito obrigatório. Atualizei README,
  guia de apresentação e guia completo para refletir a implementação atual.
- [x] **Reconstruir as distribuições após a simplificação.** O wheel e o sdist
  foram gerados novamente a partir do pacote com DFS e renderer ASCII. Isso
  evita entregar arquivos instaláveis com algoritmos ou interfaces que o
  código-fonte já não oferece.
- [x] **Remover extras de exibição e animação.** O subject permite escolher
  ASCII ou interface gráfica, e lista animação como bônus. Mantive apenas a
  exibição ASCII interativa: ela oferece regeneração, solução liga/desliga e
  mudança de cor das paredes. Retirei o Tkinter e a animação por etapa para
  manter um caminho de interface e eliminar callbacks extras. O `42` continua
  visível, e a saída sem teclado continua mostrando um desenho ASCII estático.

## Verificações da revisão anterior

- [x] **Reconstruir e conferir as distribuições.** Recriei wheel e sdist a
  partir dos fontes revisados. Comparei os bytes de cada `mazegen/*.py` nos
  dois pacotes com os arquivos fonte; não há divergências.
- [x] **Executar a CLI com chaves em minúsculas e saída temporária.** A CLI
  gerou um arquivo válido usando uma configuração temporária com todas as
  chaves minúsculas. A saída foi gravada em `/tmp`, fora da cópia submetida.
- [x] **Repetir flake8 e mypy após os ajustes.** Flake8 passou; mypy passou
  com as flags obrigatórias e também com `--strict`. Uma análise AST confirmou
  que nenhuma classe ou função Python ficou sem docstring.
- [x] **Instalar e executar o wheel separado do código-fonte.** Instalei o
  wheel reconstruído em um virtualenv em `/tmp`, executei o CLI numa pasta sem
  `mazegen/` e confirmei a criação do arquivo de saída.
- [x] **Conferir os dois modos com o analisador do subject.** Executei o
  analisador oficial nos arquivos temporários gerados pela CLI. O modo perfeito
  reportou zero loops e paredes coerentes; o modo Pac-Man reportou 34 loops,
  zero becos sem saída reais, conectividade e cantos/centro acessíveis.

## Registro das verificações anteriores

Os resultados acima descrevem a revisão antes da simplificação mais recente.
Depois dela, o pacote foi reconstruído. A verificação interativa atual usa
somente curses e precisa ser demonstrada em um terminal TTY.

## Checagens da versão simplificada

- [x] `flake8 --jobs 1 .` passou. O modo paralelo de `make lint-strict` não
  inicia neste sandbox por uma restrição de processos; o mesmo lint em processo
  único passou.
- [x] `mypy . --strict` passou sem erros.
- [x] Wheel e sdist foram reconstruídos com `python3 -m build --no-isolation`
  para não depender de acesso à rede neste ambiente.
- [x] Os controles `R`, `S`, `C` e `Q` foram percorridos em um pseudo-terminal
  com dimensões suficientes.

## Ajustes de distribuição e terminal

- [x] **Avisar quando o terminal não comporta o labirinto.** Antes, o desenho
  era cortado sem explicar o motivo. O renderer agora calcula o espaço exigido
  pela largura e altura configuradas, mostra o tamanho necessário e o tamanho
  atual, e tenta redesenhar após uma tecla. Não há limite artificial para o
  tamanho válido do labirinto.
- [x] **Manter os materiais de estudo fora dos arquivos enviados.** A pasta
  `docs/` guarda guias locais e foi adicionada ao `.gitignore`; o README de
  entrega não a lista nem aponta para ela. A configuração Pac-Man e suas
  saídas ficam na raiz, junto de `config.txt` e `maze.txt`, para que os
  comandos funcionem a partir da raiz do projeto.

## Verificação funcional da versão final

- [x] Executei os dois arquivos de configuração da raiz com a CLI final e
  analisei as saídas com `maze_analyzer.py`: `PERFECT=True` teve 0 loops;
  `PERFECT=False` teve 34 loops e 0 becos sem saída reais. Em ambos, o
  analisador confirmou conectividade, cantos/centro acessíveis e paredes
  coerentes. As saídas atuais foram gravadas em `maze.txt` e
  `maze_pacman.txt`.
- [x] Repeti os dois modos em uma configuração personalizada de 25x18. O
  analisador confirmou os mesmos critérios; portanto, a mudança de dimensões
  funciona além dos valores padrão.
- [x] Percorri a interface em pseudo-terminal de 120x50 com `S`, `C`, `R` e
  `Q`; ela encerrou com código 0. Também rodei em 40x10: o aviso exibiu as
  dimensões necessárias e atuais, e `Q` encerrou com código 0. Encurtei as
  instruções do aviso após notar que eram cortadas nessa largura.
