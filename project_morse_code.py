def str_to_morse(string):
    chart = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..',
        '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
        '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----'
    }
    converted_letters = []
    forbidden_letters = []

    for line in string.upper().splitlines():
        words = line.split()
        for word in words:
            for letter in word:
                if letter in chart.keys():
                    converted_letters.append(f"{chart[letter]} ")
                else:
                    forbidden_letters.append(letter)
            converted_letters.append("  ")
        converted_letters.append("<br>")

    morse_code = "".join(converted_letters)
    deleted_letters = " ".join(forbidden_letters)
    if deleted_letters != "":
        return morse_code + "\n" + f"⚠️ {deleted_letters} is(are) deleted."
    return morse_code