# Pathfind Algorithms

This project was develop for practicing some interesting pathfinding algorithms in a matrix graph with one start and multiple ordered goals.
The last version has the following implemented algorithms:

1. A*(A start)
2. Dijkstra's Algorithm

## Demo

![Demonstration of the program running GIF](https://imgur.com/xaBFiaK.gif)

## How to run it

### First install the dependencies used

```bash
pip3 install -r requirements.txt
```

### Then run the program

```bash
    python3 pathfinder/main.py
```

### What each button mean

1. The **pathfinding algorithms** come in cian icons and are listed using indo-arabic numbers.(Only one can be chosen per run)

    1. A* Algorithm
    2. Dijkstra's Algorithm

2. The brown icons with roman numbers represent the **obstacles algorithms**.
    1. (I) Manually click on the border to add or remove obstacles.
    2. (II) Randomly place obstacles around the border.
    3. (III) Randomly generate more terrain-like obstacles(Using perlin noise generator)

3. The **flag icon** enables the start quare mode. To do set a square as first square after enabling this mode, just click on the desired square. To change to another square just click on other square on the board. When the flag icon is activated it's not possible to manually put obstacles. To do so just click again on the flag icon to disable it.
4. The **target icon** enables the goal square mode. It's possible to add
multiple goals. Their order will be the same as the one they're created.To create a goal just click on a square that's not a start square. To remove a goal just click on it again.
5. The **play icon** start the game if the board has at least one start and one goal. While the algorithm is running it's not possible to change modes or to click other buttons. After each run the board will be clean.
6. The **restart icon** returns the board the initial blank state.
7. The **power icon** is used to close the application.