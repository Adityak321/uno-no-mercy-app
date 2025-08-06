import streamlit as st
import random

# GAME SETUP
colours = ['Red', 'Green', 'Blue', 'Yellow']
numbers = [str(i) for i in range(10)]
actions = ['Skip', 'Reverse', '+2']
special_wilds = [
    'Wild Reverse Draw 4',
    'Wild Draw 6',
    'Wild Draw 10',
    'Wild Color Roulette'
]

# DECK
deck = []
for color in colours:
    deck.append(color + ' 0')
    for i in range(1, 10):
        deck.append(color + ' ' + str(i))
        deck.append(color + ' ' + str(i))
    for action in actions:
        deck.append(color + ' ' + action)
        deck.append(color + ' ' + action)

for i in range(4):
    deck.append('Wild')
    deck.append('+4')

for i in range(2):
    for wild in special_wilds:
        deck.append(wild)

random.shuffle(deck)

# FUNCTIONS
def draw_card(deck, count=1):
    return [deck.pop() for _ in range(count) if len(deck) > 0]

def allowed_play(card, top):
    if "Wild" in card or "+4" in card:
        return True
    c_parts = card.split(" ")
    t_parts = top.split(" ")
    return c_parts[0] == t_parts[0] or c_parts[1] == t_parts[1]

def choose_color():
    return st.selectbox("Choose a color:", colours)

def handle_special(card, me, opponent, deck):
    message = ""
    skip = False

    if card == 'Wild Reverse Draw 4':
        if len(me) == 1:
            me.extend(draw_card(deck, 4))
            message = "Only 2 players: YOU draw 4!"
        else:
            opponent.extend(draw_card(deck, 4))
            message = "Opponent draws 4!"
            skip = True

    elif card == 'Wild Draw 6':
        opponent.extend(draw_card(deck, 6))
        message = "Opponent draws 6 cards!"
        skip = True

    elif card == 'Wild Draw 10':
        opponent.extend(draw_card(deck, 10))
        message = "Opponent draws 10 cards!"
        skip = True

    elif card == 'Wild Color Roulette':
        chosen = choose_color()
        message = "Color chosen: " + chosen + ". Opponent keeps drawing until they get that color."
        revealed = []
        while len(deck) > 0:
            c = deck.pop()
            revealed.append(c)
            if c.startswith(chosen) and "Wild" not in c:
                break
        opponent.extend(revealed)
        skip = True

    return message, skip

# INITIAL STATE
if 'player' not in st.session_state:
    st.session_state.deck = deck
    st.session_state.player = draw_card(st.session_state.deck, 7)
    st.session_state.computer = draw_card(st.session_state.deck, 7)
    top = st.session_state.deck.pop()
    while "Wild" in top or "+4" in top:
        st.session_state.deck.insert(0, top)
        random.shuffle(st.session_state.deck)
        top = st.session_state.deck.pop()
    st.session_state.discard = [top]
    st.session_state.turn = 'player'
    st.session_state.skip = False
    st.session_state.color_override = None
    st.session_state.message = ""

# UI
st.title("UNO: No Mercy Edition 🎮")
st.markdown("**Top Card:** " + st.session_state.discard[-1])
st.write(st.session_state.message)

# PLAYER TURN
if st.session_state.turn == 'player':
    st.subheader("Your Turn")

    for i, card in enumerate(st.session_state.player):
        if allowed_play(card, st.session_state.discard[-1]):
            if st.button("Play " + card, key="p" + str(i)):
                chosen = st.session_state.player.pop(i)
                if 'Wild' in chosen or '+4' in chosen:
                    color = choose_color()
                    new_card = color + " " + chosen
                    st.session_state.discard.append(new_card)
                    msg, skip = handle_special(chosen, st.session_state.player, st.session_state.computer, st.session_state.deck)
                    st.session_state.message = msg
                    st.session_state.skip = skip
                else:
                    st.session_state.discard.append(chosen)
                    if '7' in chosen:
                        st.session_state.player, st.session_state.computer = st.session_state.computer, st.session_state.player
                        st.session_state.message = "7 Played: Hands Swapped!"
                    elif '0' in chosen:
                        st.session_state.player, st.session_state.computer = st.session_state.computer, st.session_state.player
                        st.session_state.message = "0 Played: Hands Passed!"
                st.session_state.turn = 'computer'
                st.rerun()

    if st.button("Draw"):
        drawn = draw_card(st.session_state.deck)
        if drawn:
            st.session_state.player.extend(drawn)
            st.session_state.message = "You drew: " + drawn[0]
        st.session_state.turn = 'computer'
        st.rerun()

# COMPUTER TURN
elif st.session_state.turn == 'computer':
    st.subheader("Computer's Turn")

    played = False
    for i, card in enumerate(st.session_state.computer):
        if allowed_play(card, st.session_state.discard[-1]):
            chosen = st.session_state.computer.pop(i)
            if 'Wild' in chosen or '+4' in chosen:
                color = random.choice(colours)
                new_card = color + " " + chosen
                st.session_state.discard.append(new_card)
                msg, skip = handle_special(chosen, st.session_state.computer, st.session_state.player, st.session_state.deck)
                st.session_state.message = "Computer played: " + chosen + ". " + msg
                st.session_state.skip = skip
            else:
                st.session_state.discard.append(chosen)
                if '7' in chosen:
                    st.session_state.computer, st.session_state.player = st.session_state.player, st.session_state.computer
                    st.session_state.message = "Computer played 7: Swapped hands!"
                elif '0' in chosen:
                    st.session_state.computer, st.session_state.player = st.session_state.player, st.session_state.computer
                    st.session_state.message = "Computer played 0: Passed hands!"
                else:
                    st.session_state.message = "Computer played: " + chosen
            played = True
            break

    if not played:
        drawn = draw_card(st.session_state.deck)
        st.session_state.computer.extend(drawn)
        st.session_state.message = "Computer drew a card."

    # Switch turns
    if st.session_state.skip:
        st.session_state.skip = False
        st.session_state.turn = 'computer'
    else:
        st.session_state.turn = 'player'


# SHOW PLAYER CARDS
st.subheader("Your Cards")
st.write(st.session_state.player)

# WINNING CONDITION
if len(st.session_state.player) == 0:
    st.balloons()
    st.success("You Won!")
elif len(st.session_state.computer) == 0:
    st.error("Computer Won!")
