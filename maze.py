
print('''
Дан лабиринт
Весь периметр огражден стеной
Непроходимые участки - 1
Доступные участки - 0
Старт - х
Финиш - #
Гарантируется что путь существует.

1. найти любой путь от старта до финиша
2. найти кратчайший путь от старта до финиша''')

from queue import Queue

neighbours = ((-1, 0), (0, -1), (0, +1), (+1, 0))

maze = '''111111111111111111
1x0010000000000001
111011101111111101
101010000100000001
101011010101111111
101000010100001001
100011110101111101
101110010100000001
100000000101101111
101101111100100001
101001000000101001
101101111111101001
101000000000001001
101011110100101001
101000010111111001
111011110100000001
101000000101111111
101011110101010101
1000000101000000#1
111111111111111111'''.split('\n')

print('\n'.join(maze))

start_pos = (None, None)

was_in_queue = {}

for irow, row in enumerate(maze):
    if 'x' in row:
        start_pos = (irow, row.index('x'))
    if '#' in row:
        finish_pos = (irow, row.index('#'))

print('start position: {}'.format(start_pos))
print('exit position: {}'.format(finish_pos))

# bfs
q = Queue()
q.put(start_pos)
was_in_queue[start_pos] = (-1, -1)  # has no parent
finish = False
while not finish and not q.empty():
    current_x, current_y = q.get()
    # print(current_x, current_y)

    for dx, dy in neighbours:
        new_pos = (current_x + dx, current_y + dy)
        # print(new_pos)

        if maze[new_pos[0]][new_pos[1]] == '1' or new_pos in was_in_queue:
            continue
        q.put(new_pos)
        was_in_queue[new_pos] = (current_x, current_y)

        if new_pos == finish_pos:
            finish = True
            break

# restore path
path_length = 0
current_pos = finish_pos
parent = (None, None)
while parent != (-1, -1):
    parent = was_in_queue[current_pos]
    print(current_pos)
    current_pos = parent
    path_length += 1

print('path length: {}'.format(path_length))
