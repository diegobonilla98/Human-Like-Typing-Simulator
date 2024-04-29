import keyboard
import random
import time


is_bold_pressed = False
is_italic_pressed = False


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
        i = 0
        while i < len(text):
            char = text[i]
            if char == "*" or char == "**":
                # Determine if it's bold or italic based on the next character
                if i + 1 < len(text) and text[i + 1] == char:
                    # It's bold or italic with two asterisks
                    ctrl_key = "ctrl+i" if char == '*' else "ctrl+b"
                    end_marker = char * 2
                    i += 2
                else:
                    # It's bold or italic with one asterisk
                    ctrl_key = "ctrl+b" if char == '*' else "ctrl+i"
                    end_marker = char
                    i += 1

                time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))
                keyboard.send(ctrl_key)  # Start formatting

                # Type until we find the closing marker
                while i < len(text) and text[i:i + len(end_marker)] != end_marker:
                    keyboard.write(maybe_make_typo(text[i]))
                    time.sleep(random.uniform(max(speed - variance, 0.01), speed + variance))
                    i += 1

                keyboard.send(ctrl_key)  # End formatting
                i += len(end_marker)  # Skip the end marker
            else:
                keyboard.write(maybe_make_typo(char))
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
