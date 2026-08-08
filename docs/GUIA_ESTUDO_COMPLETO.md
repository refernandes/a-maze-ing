# Guia de Estudo Definitivo: A-Maze-ing (École 42)

Este guia foi elaborado para garantir que você passe na avaliação (defense) com facilidade, entendendo toda a teoria por trás da geração de labirintos, o funcionamento do seu código, e todos os edge-cases envolvidos.

## 1. O Essencial: Como o Labirinto é Representado na Memória

A grande "sacada" do seu projeto é a **representação bitwise** (manipulação de bits). Em vez de criar matrizes gigantescas cheias de strings (como `"#"` e `" "`), cada célula é apenas um número inteiro, e os 4 primeiros bits desse número indicam se a parede está fechada ou não.

- **Norte** (cima) = Bit 0 (Valor `1`)
- **Leste** (direita) = Bit 1 (Valor `2`)
- **Sul** (baixo) = Bit 2 (Valor `4`)
- **Oeste** (esquerda) = Bit 3 (Valor `8`)

**O que isso significa na prática?**
- Uma célula que começa com TODAS as paredes fechadas tem o valor `15` (1 + 2 + 4 + 8).
- Se quisermos quebrar a parede do Leste, subtraímos `2`. A célula vira `13`.
- **Como o código faz isso:** `grid[y][x] &= ~(1 << d)`
  - Isso significa: "Pegue o número atual e passe a tesoura (bitwise AND com NOT) exatamente no bit da direção `d`".

## 2. Algoritmos de Geração (Teoria e Diferenças)

Seu projeto é robusto e possui **3 algoritmos distintos**. É vital saber explicar a diferença entre eles para o avaliador.

### A. DFS Recursivo via Stack (Recursive Backtracker)
- **Como funciona:** Ele começa em um ponto e sai "cavando" o labirinto aleatoriamente até ficar preso (dead-end). Quando fica preso, ele faz *backtrack* (volta pelos passos anteriores) usando uma pilha (Stack) até achar uma célula com vizinhos não visitados, e recomeça a cavar.
- **Por que Stack e não recursividade pura?** Recursividade pura causa `RecursionError` no Python se o labirinto for muito grande. Usar um `list` como pilha resolve isso.
- **Visual do labirinto:** Corredores muito longos, rios sinuosos, poucos dead-ends curtos.

### B. Randomized Prim
- **Como funciona:** Cresce o labirinto a partir do centro, mantendo uma "lista de paredes fronteiriças". Ele escolhe uma parede aleatória dessa lista. Se ela divide uma célula já visitada de uma não-visitada, a parede é quebrada.
- **Visual do labirinto:** Muitos caminhos curtos e incontáveis dead-ends. Muito ramificado.

### C. Kruskal (Union-Find)
- **Como funciona:** Coloca todas as paredes possíveis do labirinto numa lista gigante e as embaralha. Ele tenta quebrar as paredes uma por uma. Para não criar ciclos (loops), ele usa a estrutura de dados **Union-Find**, que diz instantaneamente se a célula A já está conectada à célula B. Se já estiverem, ele não quebra a parede.
- **Visual do labirinto:** Muito simétrico e perfeitamente balanceado, difícil de resolver para humanos.

## 3. O Modo Pac-Man (PERFECT = False)

O modo Pac-Man (Braided Maze) não permite "caminhos sem saída" (dead-ends).

- **O que é um Dead-end?** É uma célula que tem exatamente 3 paredes fechadas e apenas 1 aberta (ou seja, você entra, mas tem que voltar pelo mesmo caminho).
- **Como o código resolve (Braiding):** 
  Ele escaneia a matriz inteira. Se acha um dead-end, ele procura vizinhos válidos ao redor, sorteia um deles, e *quebra a parede* de ligação. Isso transforma o beco sem saída num corredor ou interseção.
- **Corner Case Resolvido:** Se ele quebrasse uma parede para o lado de *fora* do mapa, o Pac-Man fugiria da tela. Por isso, a verificação `0 <= nx < width` garante que ele só quebre paredes para o lado de dentro.
- **Garantia de Fluxo:** Para garantir que os fantasmas fluam pelo mapa, o código quebra paredes forçadamente nos 4 cantos e no centro.

## 4. O Bônus do Padrão "42"

Colocar o padrão 42 no meio do mapa parece fácil, mas esconde *Edge Cases* brutais:

- **Edge Case 1: Isolamento Perfeito.** O padrão "42" são células que não fazem parte do labirinto. Elas NUNCA podem ser escavadas. Nós resolvemos isso populando um `set` com essas coordenadas e instruindo os algoritmos (DFS, Kruskal, Prim, e Braiding) a ignorá-las sumariamente (como se fossem buracos negros na matriz).
- **Edge Case 2: Conectividade.** Se o algoritmo rodasse ignorando o 42 e passasse perto dele, ele poderia criar becos sem saída encostados no 42. Para piorar, no modo Pac-Man, o script de *Braiding* tentaria quebrar a parede do beco sem saída para dentro do "42"! Nossa regra resolve isso garantindo que os vizinhos não façam parte do 42 na hora do Braiding.
- **O Fallback de Tamanho:** Se o mapa pedido no `config.txt` for menor que o próprio desenho do "42" (ex: um labirinto 5x5), o código detecta a falta de espaço e omite o desenho para não causar Index Out Of Bounds.

## 5. Solucionador BFS (O Caminho Azul)

Para encontrar o caminho da Entrada até a Saída (para gravar no `.txt` e desenhar a linha no MLX):
- Foi usado **Breadth-First Search (BFS)** porque ele garante matematicamente o caminho mais curto.
- Ele usa a fila `collections.deque` por ter complexidade `O(1)` para remover itens do começo (muito mais rápido que `list.pop(0)` que é `O(N)`).

## 6. MiniLibX e Arquitetura do Software

- O MLX original é terrível em performance no Python usando `mlx_pixel_put` porque fazer uma chamada no C para desenhar 1 pixel por vez estrangula a CPU.
- **A Sacada:** O código usa `mlx_get_data_addr`. Isso pega a memória bruta da imagem (como se fosse um array de bytes C), e o Python escreve a tela toda na memória local. Uma vez por frame, ele joga esse buffer inteiro para a tela do X11 de uma vez só (`mlx_put_image_to_window`).
- **Arquitetura Limpa:** O gerador (`mazegen`) não sabe que o MLX existe. O MLX (`renderer.py`) não sabe como o labirinto foi gerado. Se o X11 não funcionar no PC do avaliador, o `try/except` vai interceptar o erro e exibir um labirinto em ASCII no terminal sem quebrar (crash).

## Checklist de Edge Cases que você cobre 100%:
- [x] Mapa gigante (100x100+): O DFS Stack evita *RecursionError*.
- [x] Instalação do MLX corrompida: Fallback para ASCII Preview.
- [x] Labirinto sem saída encostado no bloco 42: Filtrado no Braiding.
- [x] Labirintos pequenos demais para o 42: O 42 não é renderizado, impedindo *Out of Bounds*.
- [x] Entrada ou Saída definidas coladas na parede ou nos cantos: A abertura correta das portas externas garante o acesso (portas são ignoradas no pathfinding interno para não dar *Out of Bounds* no vizinho).

Você tem tudo em mãos para a avaliação! Mantenha a calma e explique como o bitwise facilitou sua vida e salvou memória!
