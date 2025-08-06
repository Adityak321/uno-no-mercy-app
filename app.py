import streamlit as st
import random

# Initialize game state
if 'game_started' not in st.session_state:
    st.session_state.game_started = True
    st.session_state.colours = ['Red', 'Green', 'Blue', 'Yellow']
    st.session_state.numbers = [str(i) for i in range(10)]
    st.session_state.actions = ['Skip', 'Reverse', '+2']
    st.session_state.deck = []
    for color in st.session_state.colours:
        st.session_state.deck.append(color + ' 0')
        for i in range(1, 10):
            st.session_state.deck.append(color + ' ' + str(i))
            st.session_state.deck.append(color + ' ' + str(i))
        for action in st.session_state.actions:
            st.session_state.deck.append(color + ' ' + action)
            st.session_state.deck.append(color + ' ' + action)
    for i in range(4):
        st.session_state.deck.append('Wild')
        st.session_state.deck.append('+4')
    wilds = [
        'Wild Reverse Draw 4',
        'Wild Draw 6',
        'Wild Draw 10',
        'Wild Color Roulette']
    for i in range(2):
        for wild in wilds:
            st.session_state.deck.append(wild)
    random.shuffle(st.session_state.deck)

    st.session_state.player = [st.session_state.deck.pop() for _ in range(7)]
    st.session_state.computer = [st.session_state.deck.pop() for _ in range(7)]
    st.session_state.discard_pile = []
    top_card = st.session_state.deck.pop()
    while ('+4' in top_card or 'Wild' in top_card):
        st.session_state.deck.append(top_card)
        random.shuffle(st.session_state.deck)
        top_card = st.session_state.deck.pop()
    st.session_state.discard_pile.append(top_card)
    st.session_state.turn = 'player'


def allowed_play(card, top_card):
    if "Wild" in card:
        return True
    card_parts = card.split(' ')
    top_parts = top_card.split(' ')
    if card_parts[0] == top_parts[0]:
        return True
    if len(card_parts) > 1 and len(top_parts) > 1 and card_parts[1] == top_parts[1]:
        return True
    return False

st.title("UNO No Mercy - Streamlit Edition")
st.subheader("Top card: " + st.session_state.discard_pile[-1])

if st.session_state.turn == 'player':
    st.subheader("Your Hand")
    selected_card = st.selectbox("Choose a card to play or Draw", options=st.session_state.player + ['Draw'])

    if st.button("Play Card"):
        if selected_card == 'Draw':
            if len(st.session_state.deck) > 0:
                drawn = st.session_state.deck.pop()
                st.session_state.player.append(drawn)
                st.write("You drew:", drawn)
            else:
                st.write("Deck is empty! Can't draw.")
        elif allowed_play(selected_card, st.session_state.discard_pile[-1]):
            st.session_state.player.remove(selected_card)
            if 'Wild' in selected_card:
                color_choice = st.selectbox("You played a Wild! Choose a color", st.session_state.colours, key='color_pick')
                wild_card = color_choice + " " + selected_card
                st.session_state.discard_pile.append(wild_card)
                st.write("You played:", wild_card)
            else:
                st.session_state.discard_pile.append(selected_card)
                st.write("You played:", selected_card)
            if len(st.session_state.player) == 0:
                st.success("You won!")
            else:
                st.session_state.turn = 'computer'
        else:
            st.write("You can't play that card.")

elif st.session_state.turn == 'computer':
    st.subheader("Computer's Turn")
    top_card = st.session_state.discard_pile[-1]
    found = False
    for i, card in enumerate(st.session_state.computer):
        if allowed_play(card, top_card):
            st.session_state.computer.pop(i)
            if 'Wild' in card:
                color = random.choice(st.session_state.colours)
                played = color + ' ' + card
                st.session_state.discard_pile.append(played)
                st.write("Computer played:", played)
            else:
                st.session_state.discard_pile.append(card)
                st.write("Computer played:", card)
            found = True
            break
    if not found:
        if len(st.session_state.deck) > 0:
            drawn = st.session_state.deck.pop()
            st.session_state.computer.append(drawn)
            st.write("Computer drew a card.")
        else:
            st.write("Deck is empty! Computer can't draw.")

    if len(st.session_state.computer) == 0:
        st.error("Computer won!")
    else:
        st.session_state.turn = 'player'

st.write("---")
st.write("Cards remaining in deck:", len(st.session_state.deck))