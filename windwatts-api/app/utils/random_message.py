import random

def random_message():
    messages = [
        "Hello, World!",
        "Goodbye, World!",
        "I am a message!",
        "This is a message!",
        "Random message!"
    ]
    return random.choice(messages)
