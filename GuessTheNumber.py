import random
number = random.randint(1, 100)
print("Welcome to the Guess the Number game!")
print('If you want to exit the game, type "exit".')
guesstime=0
while True:
    
    guess = input("Guess a number between 1 and 100: ")
    if guess.lower() == 'exit':
        break
    if not guess.isdigit():
        print("Please enter a valid number.")
        guesstime += 1
        continue
    guess = int(guess)
    if guess < number:
        guesstime += 1
        print("Too low!")
    elif guess > number:
        guesstime += 1
        print("Too high!")
    else:
        print("Congratulations! You guessed the number.")
        print(f"You took {guesstime} attempts to guess the number.")
        break