"""Checks a Ruffle Together key map (.keys) the way Ruffle Together reads it, without starting Ruffle.

  python -I tools/keys_check.py mygame.keys

Prints the players and buttons, or the first problem with its line number (exit code 1).
"""
import sys

BUTTONS = ["UP", "DOWN", "LEFT", "RIGHT", "FIRE", "ALT", "KEY1", "KEY2", "KEY3", "KEY4", "VIEW", "QUIT", "YES", "NO",
           "MENU"]
# Flash key codes Ruffle Together can press: letters, digits, numpad, space, arrows, Backspace, Tab, Enter, Shift,
# Ctrl, Alt, Esc, Page Up/Down, End, Home, Insert, Delete and the punctuation keys
KEY_CODES = (set(range(65, 91)) | set(range(48, 58)) | set(range(96, 106)) | {106, 107, 109, 110, 111}
             | {32, 37, 38, 39, 40, 8, 9, 13, 16, 17, 18, 27, 33, 34, 35, 36, 45, 46}
             | {186, 187, 188, 189, 190, 191, 192, 219, 220, 221, 222})
MAX_PLAYERS = 4


def parse(text):
    """Returns (slots, local, shared): slots is a list of {button: code}, local is {button: [codes]}."""
    slots, local, shared = [], {}, False
    for number, line in enumerate(text.splitlines(), 1):
        line = line.split("#")[0].strip()

        def fail(why):
            raise ValueError("line %d: %s" % (number, why))

        def pairs(items):
            out = []
            for pair in items.split():
                if "=" not in pair:
                    fail("expected BUTTON=code: " + pair)
                button, codes = pair.split("=", 1)
                if button not in BUTTONS:
                    fail("unknown button " + button)
                values = []
                for c in codes.split(","):
                    if not c.isdigit() or int(c) not in KEY_CODES:
                        fail("no key with code " + c)
                    values.append(int(c))
                out.append((button, values))
            return out

        if not line:
            continue
        if line == "shared":
            shared = True
        elif line.startswith("local:"):
            for button, codes in pairs(line[len("local:"):]):
                local.setdefault(button, []).extend(codes)
        elif line.startswith("slot "):
            head, _, items = line[len("slot "):].partition(":")
            if not _ or head.strip() != str(len(slots)) or len(slots) >= MAX_PLAYERS:
                fail("slots go 0, 1, 2, 3 in order (got %s)" % head.strip())
            slot = {}
            for button, codes in pairs(items):
                if len(codes) != 1:
                    fail("a slot button presses one key")
                slot[button] = codes[0]
            slots.append(slot)
        else:
            fail("unknown line: " + line)
    if not slots:
        raise ValueError("no slots")
    return slots, local, shared


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    try:
        slots, local, shared = parse(open(sys.argv[1], encoding="utf-8").read())
    except ValueError as e:
        sys.exit("%s: %s" % (sys.argv[1], e))
    print("%d players%s" % (len(slots), ", shared keys (hot-seat)" if shared else ""))
    for i, slot in enumerate(slots):
        print("  slot %d: %s" % (i, " ".join("%s=%d" % kv for kv in slot.items())))
    unused = sorted(b for b in local if not any(b in s for s in slots))
    if unused:
        print("  note: local keys for buttons no slot presses: " + ", ".join(unused))


if __name__ == "__main__":
    main()
