import keyboard
import random
import time


italic = False
bold = False


def type_like_human(text, speed=0.2, variable_speed=True, error_rate=0.03, take_breaks=True, stop_event=None):
    common_typos = {
        'b': 'v', 'v': 'b', 'o': 'p', 'p': 'o', 'r': 't', 't': 'r',
        'a': 's', 's': 'a', 'n': 'm', 'm': 'n', 'd': 'f', 'f': 'd',
        'g': 'h', 'h': 'g', 'i': 'o', 'k': 'l', 'l': 'k', 'c': 'x',
        'x': 'c', 'e': 'r', 'u': 'y', 'y': 'u'
    }
    variance = 0.15 if variable_speed else 0.
    speed = 1. - speed

    def maybe_make_typo(character):
        if random.random() < error_rate:
            typo = common_typos.get(character, character)
            keyboard.write(typo)
            time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))
            keyboard.write('\b')  # backspace
            time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))
        return character

    def handle_special_formatting(text):
        global bold, italic
        i = 0
        while i < len(text):
            if text[i] == "*" and (i + 1 < len(text) and text[i + 1] == "*"):
                # Toggle italic if it's a double asterisk "**"
                if italic:
                    time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))
                    keyboard.send("ctrl+i")  # End italic
                    italic = False
                    i += 2  # Skip the closing "**"
                else:
                    italic = True
                    time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))
                    keyboard.send("ctrl+i")  # Start italic
                    i += 2  # Skip the opening "**"
            elif text[i] == "*":
                # Toggle bold if it's a single asterisk "*"
                if bold:
                    time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))
                    keyboard.send("ctrl+b")  # End bold
                    bold = False
                    i += 1  # Skip the closing "*"
                else:
                    bold = True
                    time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))
                    keyboard.send("ctrl+b")  # Start bold
                    i += 1  # Skip the opening "*"
            else:
                keyboard.write(maybe_make_typo(text[i]))
                time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))
                i += 1

    words = text.split(" ")
    for i, word in enumerate(words):
        if stop_event.is_set():
            break
        handle_special_formatting(word)
        keyboard.write(' ')
        time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))

        if '.' in word or '!' in word or '?' in word:
            if random.random() < 0.3:
                time.sleep(random.uniform(2, 5))
            if take_breaks and random.random() < 0.05:  # More realistic 5% chance of a pause
                time.sleep(random.uniform(30, 60))  # up to 60 seconds rest

        if take_breaks and random.random() < 0.01:  # More realistic 1% chance of a long break
            time.sleep(random.uniform(180, 420))  # 3 to 7 minutes break


# if __name__ == '__main__':
#     # Example usage
#     print("Start!")
#     time.sleep(5)
#     type_like_human("Hello, world! This is an *example* of **simulated** typing.", speed=0.1, variance=0.03)
