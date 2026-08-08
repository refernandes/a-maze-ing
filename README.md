<div align="center">
  <img src="https://img.shields.io/badge/École_42-000000?style=for-the-badge&logo=42&logoColor=white" alt="42" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <h1>A-Maze-ing</h1>
  <p><b>Advanced Maze Generator & MLX Visualizer for École 42</b></p>
</div>

---

## 📖 Sobre o Projeto

O **A-Maze-ing** é um projeto do currículo da **École 42** focado no estudo e implementação de algoritmos de geração de grafos e labirintos. 

Nosso objetivo foi além de gerar labirintos matematicamente perfeitos no terminal: nós construímos uma **Engine Completa** equipada com interface gráfica em MiniLibX (MLX), renderização via buffers de memória, resolução automática de caminhos curtos (BFS Pathfinding) e a geração avançada de mapas *Braided* sem becos sem saída, ideais para motores de jogos como o Pac-Man.

### 👥 Autores
- [refernan](https://github.com/refernandes)
- [phkaway-](https://github.com/phkaway)

Repositório Oficial: [https://github.com/refernandes/a-maze-ing.git](https://github.com/refernandes/a-maze-ing.git)

---

## ✨ Features (100% dos Bônus)

- 🎨 **MLX Graphical Renderer:** O labirinto é renderizado com a MiniLibX, manipulando bits diretamente em `memoryview` buffers para performance máxima, garantindo o funcionamento do projeto sem lentidões independentemente do tamanho da matriz.
- 🧩 **Múltiplos Algoritmos de Geração:** A engine permite escolher entre `DFS` (Recursive Backtracker via Stack), `PRIM` (Randomized Prim's), e `KRUSKAL` (via estrutura de dados Union-Find).
- 👻 **Pac-Man Mode (Braiding):** Ao desligar a opção `PERFECT`, o gerador roda uma rotina de *braiding* escaneando a matriz e anulando **100% dos dead-ends** do labirinto para garantir rotas cíclicas perfeitas para jogos de fuga/captura.
- 🔍 **Solucionador Integrado (BFS):** O menor caminho do ponto A ao B é calculado no momento da geração e pode ser desenhado ao vivo apertando `S` na interface visual.
- 🎓 **O Desafio "42":** Um bitmap irremovível contendo o número `42` no formato de digital display é integrado rigidamente ao centro do labirinto respeitando todas as colisões.

---

## 🚀 Como Executar

### Pré-requisitos
Certifique-se de que possui o Python 3.10+ e instale a biblioteca gráfica oficial do MiniLibX-Python:
```bash
pip install mlx
```

### Executando o Labirinto
Navegue até a pasta raiz e rode o entry-point apontando para um arquivo de configuração:
```bash
python3 a_maze_ing.py config.txt
```
*(Caso não possua o pacote `mlx` instalado no seu sistema, o programa rodará de forma segura via Fallback gerando uma arte ASCII diretamente no seu terminal!)*

---

## 🎮 Controles da Interface Gráfica
Assim que a janela da **MiniLibX** abrir, você pode usar os seguintes atalhos:
- `R`: **R**egera dinamicamente um novo labirinto usando a mesma seed/config.
- `S`: Liga/Desliga o traçado do **S**hortest Path (A linha azul mostrando a solução).
- `C`: Troca o **C**olor scheme (Temas: Cyberpunk, Sunset, Neon).
- `ESC` / `Q`: Sai do programa.

---

## ⚙️ Arquivo de Configuração

Os labirintos são guiados por um arquivo padronizado (`.txt`) com pares de `CHAVE=VALOR`.  
Exemplo (`config.txt`):
```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=DFS
```
> **Nota:** As opções `SEED` e `ALGORITHM` (DFS, PRIM, KRUSKAL) são parâmetros extras que adicionamos para estender as capacidades do projeto!

---

## 📚 Material de Estudo e Documentação
Para entender as entranhas do projeto, as lógicas de manipulação binária (*bitwise* maskings) de paredes e como resolver os *edge cases* no Pac-Man Mode, nós consolidamos todo o conhecimento adquirido nos guias da pasta `docs/`.

- [`docs/GUIA_ESTUDO_COMPLETO.md`](docs/GUIA_ESTUDO_COMPLETO.md): O compilado de explicações para dominar o defense!
- [`docs/GUIA_REFAZER_DO_ZERO.md`](docs/GUIA_REFAZER_DO_ZERO.md): Instruções de como a arquitetura das pastas e da classe Generator foi construída do início ao fim.
