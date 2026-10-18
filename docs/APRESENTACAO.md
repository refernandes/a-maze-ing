# Guia de apresentação

Este guia acompanha os comentários do código e serve como roteiro para
explicar o projeto durante a avaliação.

## 1. Caminho completo de uma execução

1. `a_maze_ing.py` verifica que existe exatamente um argumento.
2. `parse_config()` lê `KEY=VALUE`, ignora comentários e rejeita sintaxe ou
   valores inválidos.
3. `MazeGenerator` valida dimensões, coordenadas e entrada/saída.
4. `generate()` cria uma matriz onde cada célula começa com `0xF`, ou seja,
   quatro paredes fechadas.
5. `compute_pattern_cells()` reserva as células do desenho `42`; elas ficam
   isoladas e não participam do grafo jogável.
6. DFS remove paredes para ligar as células caminháveis.
7. Em modo não perfeito, `_braid()` abre paredes de becos sem saída para criar
   rotas alternativas de Pac-Man.
8. A validação final confirma conectividade, coerência de paredes, bordas
   fechadas, número de loops, spawns e ausência de área aberta 3x3.
9. `save_to_file()` serializa cada máscara como hexadecimal e chama BFS para
   escrever a solução mais curta no footer.
10. `MazeRenderer` mostra o labirinto em ASCII interativo no terminal; sem
    teclado interativo, imprime uma versão ASCII estática.

## 2. Como explicar a representação hexadecimal

Uma célula é um inteiro de quatro bits:

| Bit | Valor | Parede |
|---:|---:|---|
| 0 | 1 | norte |
| 1 | 2 | leste |
| 2 | 4 | sul |
| 3 | 8 | oeste |

Por exemplo, `A` é `1010`: paredes leste e oeste fechadas. Quando o gerador
abre uma passagem, ele sempre limpa o bit nos dois vizinhos. Por isso a parede
leste de uma célula e a parede oeste da próxima permanecem coerentes.

## 3. Por que DFS?

- DFS é o único algoritmo de geração porque a exigência obrigatória pede um
  algoritmo escolhido e explicado; múltiplos algoritmos são um bônus.
- A busca usa uma pilha explícita: avança para uma célula vizinha ainda não
  visitada e volta quando não há outra opção. Isso é simples de acompanhar e
  evita recursão.

O `random.Random(seed)` torna o resultado reproduzível para a mesma
configuração. Uma nova chamada de `generate()` continua podendo criar outro
labirinto.

## 4. Por que BFS para a solução?

O custo de cada movimento é igual. BFS visita o grafo em camadas: a primeira
vez que encontra o exit é necessariamente o menor número de movimentos. O
mesmo resultado é usado no arquivo e na visualização, evitando soluções
divergentes.

## 5. Diferença entre os modos

No modo perfeito, o grafo normal deve satisfazer `arestas = vértices - 1`,
portanto `E - V + 1 = 0` loops. No modo Pac-Man, a validação exige pelo menos
dois loops independentes, confirma os quatro cantos e um centro utilizável e
remove becos sem saída sempre que possível.

O `42` é a exceção prevista pelo enunciado: suas células são totalmente
fechadas, mas não contam como corredores desconectados.

## 6. Demonstração rápida

```bash
make lint-strict
python3 a_maze_ing.py config.txt
python3 a_maze_ing.py config_pacman.txt
make build
```

Durante a interface terminal:

- `R` gera outro resultado;
- `S` mostra o caminho BFS;
- `C` altera a cor das paredes;
- `Q` encerra sem traceback.

## 7. Perguntas que podem aparecer

**Por que começar com todas as paredes fechadas?**  DFS só precisa decidir
quais passagens abrir; isso torna a borda, o `42` e a coerência das duas faces
de cada passagem fáceis de validar.

**Por que usar uma pilha em DFS em vez de recursão?**  O comportamento é o
mesmo, mas uma pilha explícita evita `RecursionError` em mapas grandes.

**O que acontece se a configuração for impossível?**  O parser ou a validação
levanta `ValueError`; o programa imprime uma mensagem curta e termina com
status diferente de zero, sem traceback inesperado.

**O que é reutilizável?**  O pacote `mazegen` contém `MazeGenerator`, DFS, BFS,
tipos e o padrão. A CLI e o renderer apenas consomem sua API.
