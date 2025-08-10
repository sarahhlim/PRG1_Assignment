import random

SAVE_FILENAME = 'savegame.txt'
MAP_FILENAME = 'level1.txt'

def read_map(filename):
    #open and read from the file
    try:
        with open(filename, 'r') as f:
            lines = [line.rstrip('\n') for line in f.readlines() if line.strip('') is not None]
    except Exception:
        # backup!!! if my txt isnt working :(
        lines = [
            "T CCCCC SS GGG",
            " CCCCC SSSS",
            "GGG",
            " CCCC SSSS GGG",
            " SSSSS CCC",
            " CC S CCCC",
            "CCCCCCCCC CCCCC",
            "CCCCCCCC G CCCC",
            " CCCCC GG SS",
            " CCCCC GGG",
            "SSSSSS",
            " CCC GGG",
            "SSSGGG",
        ]
    # maxw → Finds the length of the longest row.
    #Loops over every row and if it’s shorter than maxw, adds spaces at the end so all rows have equal length.
    #This ensures the map have a perfect rectangle grid 
    grid = [list(line) for line in lines]
    maxw = max(len(r) for r in grid)
    for r in grid:
        if len(r) < maxw:
            r.extend([' '] * (maxw - len(r)))
    return grid


def find_tile(grid, tile): 
    #basically finds a certain character and gives me coords
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            if ch == tile:
                return (x, y)
    return None


def in_bounds(grid, x, y):
    #Checks if the coordinates (x, y) are within the valid boundaries of the grid.
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def tile_at(grid, x, y):
    #Returns the tile (character) at position (x, y) in the grid if it’s within bounds.
    if in_bounds(grid, x, y):
        return grid[y][x]
    #if invaild, doesnt return anything
    return None

# ----------------------------
# Game state and defaults
# ----------------------------

def new_player(name, town_pos):
    #This function sets up the initial state of the player when starting a new game(basically default setting)
    return {
        'name': name,
        'pos': town_pos[:],  # [x,y]
        'portal': town_pos[:],
        'pickaxe': 1,  # 1=copper,2=silver,3=gold
        'capacity': 10,
        'copper': 0,
        'silver': 0,
        'gold': 0,
        'gp': 0,
        'steps': 0,
        'day': 1,
        'turns_left': 20,
    }

# ----------------------------
# Save / Load
# ----------------------------

def save_game(player, fog, filename=SAVE_FILENAME):
    #saves the current game into a file
    try:
        lines = []
        # basic player info stored
        lines.append(player['name'])
        lines.append(','.join(map(str, player['pos'])))
        lines.append(','.join(map(str, player['portal'])))
        lines.append(str(player['pickaxe']))
        lines.append(str(player['capacity']))
        lines.append(str(player['copper']))
        lines.append(str(player['silver']))
        lines.append(str(player['gold']))
        lines.append(str(player['gp']))
        lines.append(str(player['steps']))
        lines.append(str(player['day']))
        lines.append(str(player['turns_left']))

        # save fog based on whether it is visible or not
        for row in fog:
            #1=visible, 0=not visible 
            lines.append(''.join('1' if v else '0' for v in row))
        #open the file and writes 
        with open(filename, 'w') as f:
            f.write('\n'.join(lines))
        print('Game saved.')
    except Exception as e:
        print('Failed to save game:', e)


def load_game(grid, filename=SAVE_FILENAME):
    try:
        #open the saved file
        with open(filename, 'r') as f:
            lines = [ln.rstrip('\n') for ln in f.readlines()]
    except Exception as e:
        print('No save file found.')
        return None, None
    try:
        #read player data
        count = 0
        name = lines[count]; count += 1
        pos = list(map(int, lines[count].split(','))); count += 1
        portal = list(map(int, lines[count].split(','))); count += 1
        pickaxe = int(lines[count]); count += 1
        capacity = int(lines[count]); count += 1
        copper = int(lines[count]); count += 1
        silver = int(lines[count]); count += 1
        gold = int(lines[count]); count += 1
        gp = int(lines[count]); count += 1
        steps = int(lines[count]); count += 1
        day = int(lines[count]); count += 1
        turns_left = int(lines[count]); count += 1

        # remaining lines are fog
        fog_lines = lines[count:]
        fog = []
        for r in fog_lines:
            fog.append([c == '1' for c in r])

        
        # checks if the loaded fog grid size matches the size of the current game map (grid).
        if len(fog) != len(grid) or any(len(fog[r]) != len(grid[0]) for r in range(len(grid))):
            fog = [[False] * len(grid[0]) for _ in range(len(grid))]
            # reveal town and portal and player position

            #It bundles all loaded player info into a dictionary to use in the game.
        player = {
            'name': name,
            'pos': pos,
            'portal': portal,
            'pickaxe': pickaxe,
            'capacity': capacity,
            'copper': copper,
            'silver': silver,
            'gold': gold,
            'gp': gp,
            'steps': steps,
            'day': day,
            'turns_left': turns_left,
        }
        print('Game loaded.')
        return player, fog
    except Exception as e:
        print('Failed to load save:', e)
        return None, None

# ----------------------------
# Shop
# ----------------------------

def shop_menu(player):
    while True:
        print('\n----------------------- Shop Menu -------------------------')
        if player['pickaxe'] < 2:
            print('(P)ickaxe upgrade to Level 2 to mine silver ore for 50 GP')
        elif player['pickaxe'] < 3:
            print('(P)ickaxe upgrade to Level 3 to mine gold ore for 150 GP')
            #calculates the price of the new backpack
        cap_upgrade_price = player['capacity'] * 2
        #prints the backpack update option
        print('(B)ackpack upgrade to carry {} items for {} GP'.format(player['capacity'] + 2, cap_upgrade_price))
        print('(L)eave shop')
        print('-----------------------------------------------------------')
        print('GP: {}'.format(player['gp']))
        choice = input('Your choice? ').strip().upper()
        if choice == 'P':
            if player['pickaxe'] == 1:
                price = 50
                #check whether it has enough money
                if player['gp'] >= price:
                    #minus the money
                    player['gp'] -= price
                    player['pickaxe'] = 2
                    print('Pickaxe upgraded to Level 2! You can now mine silver.')
                else:
                    print('Not enough GP.')
            elif player['pickaxe'] == 2:
                price = 150
                if player['gp'] >= price:
                    player['gp'] -= price
                    player['pickaxe'] = 3
                    print('Pickaxe upgraded to Level 3! You can now mine gold.')
                else:
                    print('Not enough GP.')
            else:
                #no more pickaxe to buy
                print('You already have the best pickaxe.')
        elif choice == 'B':
            price = cap_upgrade_price
            if player['gp'] >= price:
                player['gp'] -= price
                player['capacity'] += 2
                print('Congratulations! You can now carry {} items!'.format(player['capacity']))
            else:
                print('Not enough GP for backpack upgrade.')
        elif choice == 'L':
            return
        else:
            print('Invalid choice.')

# ----------------------------
# Prices and mining
# ----------------------------

def sell_all(player):
    # prices of ores
    copper_price = random.randint(1, 3)
    silver_price = random.randint(5, 8)
    gold_price = random.randint(10, 18)

    total = 0
    if player['copper'] > 0:
        earned = player['copper'] * copper_price
        print('You sell {} copper ore for {} GP.'.format(player['copper'], earned))
        total += earned
        #reset the ore to 0
        player['copper'] = 0
    if player['silver'] > 0:
        earned = player['silver'] * silver_price
        print('You sell {} silver ore for {} GP.'.format(player['silver'], earned))
        total += earned
        #reset the ore to 0
        player['silver'] = 0
    if player['gold'] > 0:
        earned = player['gold'] * gold_price
        print('You sell {} gold ore for {} GP.'.format(player['gold'], earned))
        total += earned
        #reset the ore to 0
        player['gold'] = 0
    if total > 0:
        #adds everything tgt and show the new amount of money
        player['gp'] += total
        print('You now have {} GP!'.format(player['gp']))
    return total


def can_mine(player, tile):
    if tile == 'C':
        return True
    if tile == 'S' and player['pickaxe'] >= 2:
        return True
    if tile == 'G' and player['pickaxe'] >= 3:
        return True
    return False


def mine_tile(player, tile):
    # returns number mined, and message
    if tile == 'C':
        amt = random.randint(1, 5)
        #checks how much free space the player has in their inventory
        space = player['capacity'] - (player['copper'] + player['silver'] + player['gold'])
        taken = min(amt, space)
        #takes the minimum of the random amount and available space, so the player never exceeds capacity.
        player['copper'] += taken
        return taken, amt
    if tile == 'S':
        amt = random.randint(1, 3)
        space = player['capacity'] - (player['copper'] + player['silver'] + player['gold'])
        taken = min(amt, space)
        player['silver'] += taken
        return taken, amt
    if tile == 'G':
        amt = random.randint(1, 2)
        space = player['capacity'] - (player['copper'] + player['silver'] + player['gold'])
        taken = min(amt, space)
        player['gold'] += taken
        #taken: the actual number of pieces mined and added to inventory (could be less than amt if space is limited)
        #amt: the random amount attempted to mine
        return taken, amt
    return 0, 0

# ----------------------------
# Display functions
# ----------------------------

def show_player_info(player):
    print('\n----- Player Information -----')
    print('Name:', player['name'])
    print('Current position: ({}, {})'.format(player['pos'][0], player['pos'][1]))
    pickaxelevel = {1: '1 (copper)', 2: '2 (silver)', 3: '3 (gold)'}
    print('Pickaxe level:', pickaxelevel.get(player['pickaxe'], str(player['pickaxe'])))
    print('Gold:', player['gold'])
    print('Silver:', player['silver'])
    print('Copper:', player['copper'])
    load = player['copper'] + player['silver'] + player['gold']
    print('------------------------------')
    print('Load: {} / {}'.format(load, player['capacity']))
    print('------------------------------')
    print('GP:', player['gp'])
    print('Steps taken:', player['steps'])
    print('------------------------------')


def show_town_menu():
    print('\nDAY {}'.format(player['day']))
    print('----- Sundrop Town -----')
    print('(B)uy stuff')
    print('See Player (I)nformation')
    print('See Mine (M)ap')
    print('(E)nter mine')
    print('Sa(V)e game')
    print('(Q)uit to main menu')
    print('------------------------')


def render_viewport(grid, player, fog):
    #Gets the player's current coordinates.
    x, y = player['pos']
    out = []
    #to cover the 3 rows and 3 columns around the player (including their current tile).
    for dy in (-1, 0, 1):
        row = ''
        for dx in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            #If it's outside the map boundaries (in_bounds returns False), it adds a '#' to the row, representing a wall or edge.
            if not in_bounds(grid, nx, ny):
                row += '#'
            else:
                if dx == 0 and dy == 0:
                    #player's current position
                    row += 'M'
                else:
                    ch = grid[ny][nx]
                    #check if its empty and output shows a blank space
                    if ch == ' ':
                        row += ' '
                    else:
                        # show the ores symbol
                        row += ch
          
            #check if the coords are inside the grid boundaries
            if in_bounds(grid, nx, ny):
                #if yes then the tile is revealed 
                fog[ny][nx] = True
        out.append(row)

    print('\n+---+')
    for r in out:
        print('|' + r + '|')
    print('+---+')


def show_map(grid, player, fog):
    #make the map "+---+"
    print('+{}+'.format('-' * (len(grid[0]) + 2)))
    for y, row in enumerate(grid):
        #left border '|'
        s = '|'
        for x, ch in enumerate(row):
            #If the player’s current position matches (x, y), it adds 'M' to represent the player.
            if player['pos'][0] == x and player['pos'][1] == y:
                s += 'M'
            #Else if the portal’s position matches (x, y), it adds 'P' to represent the portal.
            elif player['portal'][0] == x and player['portal'][1] == y:
                s += 'P'
                #t = town
            elif ch == 'T':
                s += 'T'
            elif fog[y][x]:
                # show revealed tile
                if ch in ['C', 'S', 'G']:
                    s += ch
                else:
                    s += ' '
            else:
                #unknown place in the map
                s += '?'
        #closes the border with another '|'
        s += '|' 
        # trim to width
        print(s)
        #It visually frames the map horizontally.
    print('+{}+'.format('-' * (len(grid[0]) + 2)))

# ----------------------------
# Game loops
# ----------------------------

def enter_mine(grid, player, fog):
    # Ensure player starts at portal position when entering mine
    player['pos'] = player['portal'][:]
    print('\n---------------------------------------------------')
    print(' DAY {}'.format(player['day']))
    print('---------------------------------------------------')
    while True:
        # display viewport and info
        render_viewport(grid, player, fog)
        load = player['copper'] + player['silver'] + player['gold']
        print('Turns left: {} Load: {} / {} Steps: {}'.format(player['turns_left'], load, player['capacity'], player['steps']))
        print('(WASD) to move')
        print('(M)ap, (I)nformation, (P)ortal, (Q)uit to main menu')
        action = input('Action? ').strip().upper()
        if action == 'M':
            show_map(grid, player, fog)
            continue
        if action == 'I':
            show_player_info(player)
            continue
        if action == 'P':
            # use portal
            use_portal(player, fog)
            return
        if action == 'Q':
            # quit to town (no portal used)
            print('Quitting to town (no portal used).')
            return
        if action in ['W','A','S','D']:
            dx = 0; dy = 0
            if action == 'W': dy = -1
            if action == 'S': dy = 1
            if action == 'A': dx = -1
            if action == 'D': dx = 1
            #calculates the new coords
            nx = player['pos'][0] + dx
            ny = player['pos'][1] + dy
            # bounds check
            if not in_bounds(grid, nx, ny):
                print("You can't go that way.")
            else:
                #shows what kind of character is at the position
                tile = grid[ny][nx]
                #sums up the ores that the player is currently carrying
                load = player['copper'] + player['silver'] + player['gold']
                #check if the tile is ore
                if tile in ['C','S','G']:
                    #check if the player has enough space
                    if load >= player['capacity']:
                        print("You can't carry any more, so you can't go that way.")
                    else:
                        #check if the pickaxe is good enough
                        if not can_mine(player, tile):
                            print("Your pickaxe is not good enough to mine that.")
                        else:
                            taken, amt = mine_tile(player, tile)
                            if taken > 0:
                                #shows how much the player mined and how many they can take
                                print('You mined {} piece(s) of {}.'.format(amt, 'copper' if tile=='C' else 'silver' if tile=='S' else 'gold'))
                                if taken < amt:
                                    space = player['capacity'] - load
                                    #It prints how many pieces were mined.
                                    print("...but you can only carry {} more piece(s)!".format(space))
                                # REMOVE ore from map here
                                grid[ny][nx] = ' '
                            else:
                                print('No space to carry ore.')
                            # move onto tile after mining
                            player['pos'][0] = nx
                            player['pos'][1] = ny
                else:
                    # empty tile or T
                    player['pos'][0] = nx
                    player['pos'][1] = ny
                    if tile == 'T':
                        # returned to town naturally
                        print('You step onto T and return to town.')
                        use_portal_forced(player, fog)
                        return
            #After moving, the code make the player’s step count and reduces their turns left by 1.
            player['steps'] += 1
            player['turns_left'] -= 1
            # check turns left
            if player['turns_left'] <= 0:
                print('You are exhausted.')
                # automatic portal placement
                use_portal_forced(player, fog)
                return
            continue
        else:
            print('Invalid action.')




def use_portal(player, fog):
    # place portal at current location and return to town
    player['portal'][0] = player['pos'][0]
    player['portal'][1] = player['pos'][1]
    print('You place your portal stone here and zap back to town.')

    sell_all(player)

    # increase the day and reset 20 turns
    player['day'] += 1
    player['turns_left'] = 20

    # teleport player to the portal position if valid, else to town
    #gets the portal coords
    px, py = player['portal']
    #check if its in the boundaries and if its empty
    if in_bounds(grid, px, py) and tile_at(grid, px, py) != ' ':
        #if both are true, it moves the player to that coords
        player['pos'] = [px, py]
    else:
        #If not, it finds the town location ('T') on the map and sends the player there instead
        town_pos = find_tile(grid, 'T')
        if town_pos:
            player['pos'] = [town_pos[0], town_pos[1]]

    # reveal portal position on fog
    fog[player['portal'][1]][player['portal'][0]] = True

    # check win
    if player['gp'] >= 500:
        print('\n-------------------------------------------------------------')
        print('Woo-hoo! Well done, {}, you have {} GP!'.format(player['name'], player['gp']))
        print('You now have enough to retire and play video games every day.')
        print('And it only took you {} days and {} steps! You win!'.format(player['day'], player['steps']))
        print('-------------------------------------------------------------')
        raise SystemExit



def use_portal_forced(player, fog):
    # like use_portal but used when stepping on T or turns end; still sells ores
    use_portal(player, fog)

# ----------------------------
# Main program
# ----------------------------

grid = read_map(MAP_FILENAME)

def make_fog():
    #make everything unknown
    return [[False] * len(grid[0]) for _ in range(len(grid))]

# initial

while True:
    print('\n---------------- Welcome to Sundrop Caves! ----------------')
    print('You spent all your money to get the deed to a mine, a small')
    print('backpack, a simple pickaxe and a magical portal stone.')
    print('How quickly can you get the 500 GP you need to retire')
    print('and live happily ever after?')
    print('-----------------------------------------------------------')
    print('--- Main Menu ----')
    print('(N)ew game')
    print('(L)oad saved game')
    print('(Q)uit')
    print('------------------')
    choice = input('Your choice? ').strip().upper()
    if choice == 'N':
        name = input('Greetings, miner! What is your name? ').strip()
        town_pos = find_tile(grid, 'T')
        if not town_pos:
            town_pos = [0, 0]
        player = new_player(name, [town_pos[0], town_pos[1]])
        fog = make_fog()
        # reveal initial nearby squares
        x,y = player['pos']
        for dy in (-1,0,1):
            for dx in (-1,0,1):
                nx, ny = x+dx, y+dy
                if in_bounds(grid, nx, ny):
                    fog[ny][nx] = True
        print('Pleased to meet you, {}. Welcome to Sundrop Town!'.format(player['name']))
        # town loop
        while True:
            # upon entering town, automatically sell all ore
            sell_all(player)
            print('\nDAY {}'.format(player['day']))
            print('----- Sundrop Town -----')
            print('(B)uy stuff')
            print('See Player (I)nformation')
            print('See Mine (M)ap')
            print('(E)nter mine')
            print('Sa(V)e game')
            print('(Q)uit to main menu')
            print('------------------------')
            ch = input('Your choice? ').strip().upper()
            if ch == 'B':
                shop_menu(player)
                continue
            elif ch == 'I':
                show_player_info(player)
                continue
            elif ch == 'M':
                show_map(grid, player, fog)
                continue
            elif ch == 'E':
                # enter mine
                try:
                    enter_mine(grid, player, fog)
                except SystemExit:
                    # win -> exit game entirely back to main menu
                    break
                continue
            elif ch == 'V':
                save_game(player, fog)
                continue
            elif ch == 'Q':
                print('Returning to main menu...')
                break
            else:
                print('Invalid choice.')
        # back to main menu after finishing town loop
        continue
    elif choice == 'L':
        fog = make_fog()
        #load player data and fog from a saved file.
        player_loaded, fog_loaded = load_game(grid)
        if player_loaded:
            #Replace the current player with the loaded player data.
            player = player_loaded
            # ensure types
            player['pos'] = list(player['pos'])
            player['portal'] = list(player['portal'])
            # fog handling
            if fog_loaded:
                fog = fog_loaded
            else:
                fog = make_fog()
            # reveal around player and portal
            x,y = player['pos']
            for dy in (-1,0,1):
                for dx in (-1,0,1):
                    nx, ny = x+dx, y+dy
                    if in_bounds(grid, nx, ny):
                        fog[ny][nx] = True
            # go to town after load
            while True:
                sell_all(player)
                print('\nDAY {}'.format(player['day']))
                print('----- Sundrop Town -----')
                print('(B)uy stuff')
                print('See Player (I)nformation')
                print('See Mine (M)ap')
                print('(E)nter mine')
                print('Sa(V)e game')
                print('(Q)uit to main menu')
                print('------------------------')
                ch = input('Your choice? ').strip().upper()
                if ch == 'B':
                    shop_menu(player)
                    continue
                elif ch == 'I':
                    show_player_info(player)
                    continue
                elif ch == 'M':
                    show_map(grid, player, fog)
                    continue
                elif ch == 'E':
                    try:
                        enter_mine(grid, player, fog)
                    except SystemExit: #If enter_mine() raises SystemExit (e.g., player won or quit), the program catches it to stop the current loop without crashing the entire program.
                        break
                    continue
                elif ch == 'V':
                    save_game(player, fog)
                    continue
                elif ch == 'Q':
                    print('Returning to main menu...')
                    break
                else:
                    print('Invalid choice.')
            continue
        else:
            continue
    elif choice == 'Q':
        print('Goodbye!')
        break
    else:
        print('Invalid choice. Please select N, L or Q.')
