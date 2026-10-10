# Avaliação da régua Intra — A-Maze-ing

Este documento compara, item por item, a régua de avaliação do PDF
`Intra Projects A-Maze-ing Edit2.pdf` com o conteúdo atual de
`submission_clone/`. A análise distingue evidência no código, verificações
executadas e verificações que dependem do repositório oficial ou da defesa.

## Resultado resumido

As partes funcionais centrais foram verificadas: lint e mypy passam; os modos
Pac-Man e perfeito geraram resultados aceitos pelo analisador; cinco classes de
configuração inválida encerraram com erro tratado; a seed fixa reproduziu o
mesmo maze; e o wheel recém-construído foi instalado em um virtualenv novo e
usado pela CLI.

**Não é correto afirmar que a nota 100 está garantida.** Há dois pontos
concretos a resolver ou esclarecer antes de marcar todos os itens como “Yes”:

1. O bloco que o README identifica como `config.txt` usa `WIDTH=200`, mas
   [`config.txt`](config.txt) usa `WIDTH=20`. O resultado atual também mede
   20 × 15.
2. A régua diz que chaves em minúsculas também são aceitas; o parser atual é
   sensível a maiúsculas e minúsculas. Uma configuração com `width=20` não
   equivale a `WIDTH=20` para o código.

Além disso, a régua exige avaliar o repositório Git oficial e seu dono. Esta
cópia de trabalho não contém um diretório `.git`, então não foi possível
confirmar remote, branch, commits, titularidade ou que a avaliação está sendo
feita sobre o clone oficial. Esses pontos são procedimentos da defesa, não
propriedades que o código local possa provar.

## Legenda

- **Atende**: critério presente e sustentado por inspeção ou verificação.
- **Ressalva**: há evidência parcial, uma inconsistência ou uma condição a
  confirmar na defesa.
- **Não verificável aqui**: depende do repositório remoto, de uma ação do
  avaliador ou de contexto externo ao código.

As páginas abaixo se referem às páginas do PDF da escala, não à subject anexada
à própria escala.

## Página 1 — conduta e procedimento da avaliação

Esses itens orientam quem avalia e não são funcionalidades do maze.

| Item da régua | Situação no projeto e evidência | Estado |
|---|---|---|
| Manter uma avaliação educada, respeitosa e construtiva | Regra de conduta entre avaliador e equipe; não pode ser medida pelos arquivos. | Não verificável aqui |
| Identificar problemas junto da equipe e discutir as causas | Exige conversa durante a avaliação presencial/remota. Este relatório registra os achados técnicos disponíveis. | Não verificável aqui |
| Manter abertura a interpretações diferentes e atribuir nota honestamente | Julgamento do avaliador, não requisito de implementação. | Não verificável aqui |
| Avaliar somente o conteúdo do repositório Git do estudante/equipe | A pasta `submission_clone/` não contém `.git`; não há como provar que seu conteúdo é o mesmo do remote oficial. | Ressalva |
| Confirmar titularidade do repositório e que pertence ao projeto | O PDF apresenta um endereço Vogsphere, mas a cópia local não informa nem prova a relação entre esse endereço e a equipe. | Não verificável aqui |
| Confirmar clone em diretório vazio e procurar aliases maliciosos | Não há metadados Git nesta cópia para conferir o comando de clone ou aliases. A inspeção dos fontes locais não substitui a conferência do repositório oficial. | Não verificável aqui |
| Conferir scripts usados para facilitar a correção | O analisador `maze_analyzer.py` foi usado nas conferências abaixo. Não foi possível auditar scripts que um avaliador possa trazer à defesa. | Ressalva |
| Avaliador que ainda não concluiu o projeto deve ler a subject inteira | Obrigação individual do avaliador. | Não verificável aqui |
| Aplicar flags para repositório vazio, crash, Norm ou fraude quando cabível | A cópia contém os arquivos e os comandos funcionais passaram nas verificações descritas neste relatório. A decisão sobre flags é do avaliador na defesa. | Ressalva |
| Evitar encerramento inesperado durante a defesa | Cinco configurações inválidas terminaram com erro tratado e sem traceback; os modos válidos e o pacote foram executados. A interação final ainda deve ser demonstrada no ambiente de defesa. | Ressalva |
| Durante a defesa, editar somente a configuração, salvo acordo explícito | É uma regra de procedimento da sessão. Não é verificável por inspeção dos fontes. | Não verificável aqui |

## Página 2 — arquivos, Norm, README e execução

### Básicos: arquivos enviados e Norm

| Critério | Evidência em `submission_clone/` | Estado |
|---|---|---|
| `README.md` na raiz | Existe em `submission_clone/README.md`. | Atende |
| `LICENSE.md` com licença de reutilização | Existe; `pyproject.toml` declara MIT e inclui `LICENSE.md` nos metadados do pacote. | Atende |
| `a_maze_ing.py` | Existe na raiz do clone e é a entrada de linha de comando. | Atende |
| Distribuição `mazegen-*.tar.gz` e/ou `.whl` | Os dois arquivos existem. Também foram reconstruídos em uma cópia temporária do projeto. | Atende |
| Arquivo de configuração | `config.txt` existe e contém as seis chaves obrigatórias e a seed opcional. | Atende |
| Todos os elementos necessários para reconstruir o pacote | `pyproject.toml` e o pacote `mazegen/` estão presentes; a reconstrução de wheel e sdist passou. | Atende |
| Norm nos Python e mypy | `make lint` terminou com código 0: flake8 passou e mypy reportou “Success: no issues found in 12 source files”. | Atende |
| Ausência de item obrigatório que zere a avaliação | Nenhum arquivo obrigatório listado acima está ausente na pasta examinada. A inclusão dessa pasta no remote oficial não foi verificada. | Atende na cópia; ressalva de repositório |

### README: presença e conteúdo obrigatório

| Critério | Evidência | Estado |
|---|---|---|
| Primeira linha em itálico com a frase de autoria e os dois logins | A linha 1 de `README.md` está em itálico e segue o formato, com `rfernan` e `phkaway-`. A veracidade dos logins/autoria depende da equipe. | Atende, autoria a confirmar |
| Seção `Description` com propósito e visão geral | Linhas 5–10 descrevem geração, exibição, gravação e módulo reutilizável. | Atende |
| Seção `Instructions` com instalação, compilação/execução | Linhas 12–40 explicam ambiente, instalação, execução, controles, lint e build. | Atende |
| Seção `Resources` com referências externas e explicação de uso | Linhas 152–162 listam livro, documentação Python, subject e analisador, e relacionam as referências a DFS, BFS e controles de terminal. A explicação é concisa; na defesa, a equipe deve conseguir explicar o uso de cada referência. | Atende, confirmar domínio na defesa |
| Descrição completa da configuração | Linhas 42–72 documentam chaves, coordenadas, seed, limites e bordas. Porém, o exemplo anunciado como configuração submetida diverge do arquivo real (`WIDTH=200` no README contra `WIDTH=20` no config). | Ressalva: corrigir a divergência |
| Algoritmo escolhido | Linhas 74–80 nomeiam DFS iterativo/recursive backtracker. | Atende |
| Motivo da escolha do algoritmo | O README explica pilha explícita, leitura simples e ausência do limite de recursão do Python. | Atende |
| Documentação breve do módulo reutilizável | Linhas 94–120 mostram instalação, importação e uso de `MazeGenerator`. | Atende |
| Funções de cada membro | Linhas 135–140 atribuem responsabilidades a ambos os logins. A escala pede os papéis; a divisão factual deve ser confirmada pela equipe. | Atende, confirmar autoria |
| Plano inicial e evolução | Linhas 142–145 registram as etapas e como o plano evoluiu. | Atende |
| O que funcionou e o que poderia melhorar | Linhas 147–150 registram escolhas que funcionaram e apontam testes automatizados e peer review como melhorias. | Atende |
| Ferramentas usadas | Linhas 158–162 listam Python, venv, flake8, mypy, build, curses, Git, peer review e assistência de IA. | Atende |

O README cumpre a estrutura solicitada, mas o exemplo de configuração não deve
ser chamado de “configuração submetida” enquanto divergir do arquivo real.

### Uso padrão: exibição

| Critério | Evidência e conferência | Estado |
|---|---|---|
| Executar `a_maze_ing.py` com uma configuração padrão | A CLI foi executada usando um wheel recém-construído e uma configuração de 20 × 15. | Atende |
| Gerar um maze aleatório | `carve_depth_first()` usa um `random.Random`; a seed 42 repetiu o mesmo resultado e a seed 43 gerou um diferente. | Atende |
| Exibir no terminal ou janela gráfica dedicada | `MazeDisplay.run()` seleciona curses em TTY e ASCII sem TTY. As execuções sem TTY exibiram ASCII. | Atende |
| Oferecer interação com o programa | `maze_display.py` contém o loop de teclas, regeneração, solução, cor e rolagem. Os controles foram exercitados em terminal interativo nas conferências anteriores desta sessão. | Atende; demonstrar na defesa |

### Uso padrão: menu interativo

| Interação obrigatória | Implementação | Estado |
|---|---|---|
| Gerar outro maze | `maze_display.py`, linhas 76–79: tecla `R` chama `generate()` e salva de novo. | Atende |
| Alternar exibição do menor caminho | Linhas 80–81 alternam `show_solution`; o desenho consulta o caminho do gerador. | Atende |
| Trocar a cor das paredes | Linhas 82–84 alternam a paleta e atualizam o par de cores do curses. | Atende |
| Interações extras | Setas rolam a visualização; `Q` e `Esc` encerram o loop. | Atende |

## Página 3 — configuração, tratamento de erros, saída e geração

### Arquivo de configuração: formato

| Critério | Evidência e conferência | Estado |
|---|---|---|
| Comentários começam com `#` | `parse_config()` ignora linhas vazias e linhas cujo conteúdo, após `strip()`, começa com `#`. `config.txt` usa esse formato. | Atende |
| Linhas usam `KEY=VALUE` | O parser exige `=` e divide a linha na primeira ocorrência. Uma linha sem `=` foi testada e retornou erro tratado. | Atende |
| Chaves minúsculas também são aceitas | A busca por chaves é sensível a maiúsculas: só os nomes `WIDTH`, `HEIGHT`, etc. são reconhecidos. A régua permite explicitamente minúsculas. | Ressalva: possível falha de conformidade |
| As chaves esperadas existem | O parser exige `WIDTH`, `HEIGHT`, `ENTRY`, `EXIT`, `OUTPUT_FILE` e `PERFECT`; `SEED` é opcional. Todas as obrigatórias estão em `config.txt`. | Atende |

### Tratamento de erros solicitado pela escala

Cada caso foi executado em arquivo temporário por meio da CLI instalada. Nos
cinco casos, a execução retornou código 1, exibiu erro e não imprimiu traceback.

| Alteração solicitada na régua | Comportamento conferido | Estado |
|---|---|---|
| Remover uma chave obrigatória | `parse_config()` informa as chaves ausentes. | Atende |
| Adicionar linha fora do formato `KEY=VALUE` | O parser informa o número da linha e exige o formato. | Atende |
| Trocar números por letras | Conversões de dimensão/seed/coordenada geram `ValueError` tratado. | Atende |
| Booleano inválido para `PERFECT` | Apenas `true` e `false`, sem distinção de caixa, são aceitos. | Atende |
| Tupla `ENTRY` ou `EXIT` mal formatada | `_coordinate()` exige dois inteiros separados por vírgula; dimensões e limites são verificados pelo construtor. | Atende |
| Arquivo de configuração ausente ou erro de leitura | `parse_config()` transforma `OSError` em mensagem de configuração inválida; a CLI trata `ValueError`. | Atende por inspeção |

### Arquivo de saída

| Critério | Evidência e conferência | Estado |
|---|---|---|
| Primeiro maze também é salvo | `main()` gera e chama `save_to_file()` antes de iniciar a tela. | Atende |
| Exatamente `HEIGHT` linhas de `WIDTH` caracteres | `save_to_file()` percorre cada linha da grade e escreve um dígito hexadecimal por célula. O analisador leu o artefato atual como 20 × 15. | Atende |
| Linha vazia após a grade | `save_to_file()` escreve `\n` adicional antes do rodapé. | Atende |
| Entrada e saída no rodapé | O arquivo inclui as duas coordenadas em `x,y`. O analisador leu `(0,0)` e `(19,14)` no maze atual. | Atende |
| Menor caminho com `N`, `E`, `S`, `W` | BFS calcula o caminho; `path_directions()` converte cada passo para uma dessas letras. O arquivo é produzido pelo mesmo `MazeGenerator` que fornece a rota à tela. | Atende por implementação |
| Usar `maze_analyzer.py` para parede e modo | O artefato Pac-Man recebeu “Wall coherence: OK” e veredito `Pac-Man-USABLE`. Uma geração nova de cada modo também passou: `Pac-Man-USABLE` e `PERFECT`. | Atende |
| Caminho salvo corresponde ao exibido | A serialização e a tela consultam `get_solution_path()`; a tela marca as mesmas coordenadas retornadas pelo solver. | Atende por rastreamento do código |

### Módulo gerador: geração do maze

| Critério | Evidência e conferência | Estado |
|---|---|---|
| Geração aleatória, usando módulo padrão se desejado | `generator.py` cria `random.Random(seed)` e o DFS usa `rng.choice()`. | Atende |
| Parâmetros inconsistentes tratados (coordenadas, dimensões) | Dimensões positivas, limite de 100.000 células, entrada/saída distintas e dentro da grade são exigidos. Coordenadas que colidem com o 42 também são rejeitadas. A CLI transforma esses erros em mensagem. | Atende |
| Todas as células alcançáveis, exceto as do 42 | O gerador compara o conjunto visitado ao conjunto jogável; `validation.py` repete a checagem por busca. No maze atual: 278 alcançáveis, zero corredores inalcançáveis; as células do padrão são excluídas. | Atende |
| Paredes ao redor do maze | `_validate_borders()` exige as quatro bordas externas fechadas. O analisador confirma coerência das paredes compartilhadas do arquivo atual. | Atende |
| Nenhuma área aberta 3 × 3 ou maior | `try_open_without_3x3()` reverte uma abertura que produziria bloco 3 × 3; `validate_maze()` rejeita o resultado se encontrar algum. Bloco maior também conteria um bloco 3 × 3. | Atende por implementação |
| Padrão 42, ou mensagem se a grade for pequena | `constants.py` contém o bitmap central; `pattern_cells()` o omite com aviso no stderr quando não cabe. `generator.py` preserva as células como totalmente fechadas. | Atende por implementação |
| `PERFECT=True`: maze perfeito, uma rota entre células e zero ciclos | O modo não aplica o braiding; a validação exige `E - V + 1 == 0`. Uma geração nova foi aceita pelo analisador com veredito `PERFECT`. | Atende |
| `PERFECT=False`: conectividade Pac-Man, cantos/centro abertos e rotas independentes | `remove_dead_ends()`, `open_spawn_cells()` e `validate_maze()` implementam esses requisitos. O analisador atual encontrou 278 células jogáveis conectadas, cantos e centro alcançáveis e 31 ciclos. | Atende |
| Poucos becos sem saída; nenhum é o ideal | Validador permite até dois. O artefato atual tem zero becos sem saída reais; o analisador também foi executado com `--max-dead-ends 0` e manteve o veredito Pac-Man-USABLE/bonus-grade. | Atende; bônus elegível |
| Repetibilidade com seed idêntica | Duas instâncias com seed 42 produziram grades iguais; seed 43 produziu uma grade diferente. | Atende |
| Gerar os dois modos e executar o analisador em ambos | Feito com CLI e wheel recém-construído: modo padrão `Pac-Man-USABLE`; modo perfeito `PERFECT`. | Atende |

## Página 4 — pacote reutilizável e bônus

### Módulo reutilizável

| Critério | Evidência e conferência | Estado |
|---|---|---|
| Reconstruir `mazegen-*.tar.gz` e/ou `.whl` | `python3 -m build --no-isolation --wheel --sdist` gerou os dois artefatos em pasta temporária a partir de uma cópia limpa do projeto. | Atende |
| Instalar o pacote reconstruído em virtualenv separado | O wheel recém-gerado foi instalado em um virtualenv novo, sem rede e sem dependências externas. | Atende |
| Usar o pacote instalado com `a_maze_ing.py` e configuração | A CLI e seus módulos de interface foram executados fora da árvore do pacote, usando o módulo instalado no virtualenv. Os dois modos produziram arquivos aceitos pelo analisador. | Atende |
| Confirmar que tudo funciona | Build, instalação, CLI Pac-Man, CLI perfeito e análise dos dois resultados terminaram sem erro. O sdist foi reconstruído; a instalação de verificação foi feita pelo wheel. | Atende para a rota wheel exigida pela escala |

### Bônus

| Ideia da escala | Evidência | Situação |
|---|---|---|
| Maze padrão sem becos sem saída | O maze atual tem zero becos reais. O comando com `--max-dead-ends 0` manteve `Pac-Man-USABLE` e informou `bonus-grade`. | Bônus demonstrado |
| Múltiplos algoritmos | O pacote atual implementa DFS; não oferece Prim e Kruskal. | Não reivindicado |
| Animação durante a geração | A visualização mostra o maze pronto; não há callback/animação passo a passo no gerador atual. | Não reivindicado |

O bônus sem becos sem saída é evidência de um bônus funcional. A quantidade de
pontos de bônus e a avaliação geral de 0 a 5 continuam sendo decisões do
avaliador. Os exemplos de bônus da régua não significam que todos sejam
obrigatórios para cumprir os critérios básicos.

## Conferências executadas para este relatório

- `make lint`: passou; flake8 sem saída de erro e mypy sem problemas em 12
  arquivos.
- `python3 maze_analyzer.py submission_clone/maze.txt`: `Pac-Man-USABLE`, 278
  alcançáveis, zero corredores inalcançáveis, 31 ciclos, zero becos reais,
  cantos e centro alcançáveis e paredes coerentes.
- O mesmo analisador foi executado com `--max-dead-ends 0`: permaneceu
  `Pac-Man-USABLE` e informou bônus.
- Geração nova nos modos Pac-Man e perfeito pelo wheel instalado: ambos os
  resultados passaram pelo analisador.
- Configuração inválida em cinco variantes: todas encerraram com mensagem e
  código 1, sem traceback.
- Reprodutibilidade: seed 42 repetiu o grid; seed 43 variou o resultado.
- Build novo de wheel e sdist, instalação do wheel em virtualenv limpo e
  execução da CLI usando esse ambiente: passaram.

Essas conferências não alteraram os fontes, a configuração ou o maze
submetido. A avaliação só acrescenta este relatório ao clone.

## Conclusão prática

**A implementação central está forte e as verificações funcionais principais
passaram. Ainda não marcaria todos os critérios como 100% sem ressalvas.** Antes
da defesa, os pontos objetivos a resolver são:

1. alinhar o `WIDTH` do exemplo no README ao `config.txt` real;
2. decidir, à luz da leitura literal da escala, se o parser deve aceitar nomes
   de chave em minúsculas — hoje não aceita;
3. confirmar no Vogsphere que a pasta examinada corresponde ao repositório,
   equipe e estado que serão avaliados;
4. garantir que os dois membros consigam explicar a geração, as regras de
   paredes, a validação e o pacote durante a defesa.

Os itens 1 e 2 são pequenos, mas verificáveis pelo avaliador. Os itens 3 e 4
dependem da equipe e do contexto da avaliação. Este relatório não modifica
nenhum deles; apenas registra a comparação com a régua.
