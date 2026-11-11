"""Checks a Ruffle Together key map (.keys) the way Ruffle Together reads it, without starting Ruffle.

  python -I tools/keys_check.py mygame.keys

Prints the players and buttons, or the first problem with its line number (exit code 1).

Follows the parser in Ruffle Together 1.0.8 (desktop/src/coop/keymap.rs): up to 8 slots, and the mouse lines
`mouse: host|zones|buttons|all`, `mouse N: ...` (N is 1 to 7), `zone N: X,Y WxH` or `zone N: _root.clip`,
`private: _root.clip [opened-by _root.pattern]`, `hover: own|shared` and `cursors: auto|on|off`. It checks their
form, not whether the clips exist. Ruffle Together's own loader (`--coop-keys`) is the final check: a newer release
may know lines this tool does not.
"""
import sys

BUTTONS = ["0", "UP", "DOWN", "LEFT", "RIGHT", "FIRE", "ALT", "KEY1", "KEY2", "KEY3", "KEY4", "VIEW", "QUIT", "YES", "NO",
           "MENU"]
# Flash key codes Ruffle Together can press: letters, digits, numpad, space, arrows, Backspace, Tab, Enter, Shift,
# Ctrl, Alt, Esc, Page Up/Down, End, Home, Insert, Delete and the punctuation keys
KEY_CODES = (set(range(65, 91)) | set(range(48, 58)) | set(range(96, 106)) | {106, 107, 109, 110, 111}
             | {32, 37, 38, 39, 40, 8, 9, 13, 16, 17, 18, 27, 33, 34, 35, 36, 45, 46}
             | {186, 187, 188, 189, 190, 191, 192, 219, 220, 221, 222})
MAX_PLAYERS = 8  # Ruffle Together 1.0.5 and later
MOUSE_MODES = ["host", "zones", "buttons", "all"]
HOVERS = ["own", "shared", "host"]  # host: the old name of shared
CURSORS = ["auto", "on", "off"]


def is_number(text):
    try:
        float(text)
        return True
    except ValueError:
        return False


def zone_ok(text):
    """`X,Y WxH` (stage pixels) or one clip path, as Ruffle Together's Zone::parse reads it."""
    text = text.strip()
    if text[:1].isdigit() or text[:1] == "-":
        at, space, size = text.partition(" ")
        x, comma, y = at.partition(",")
        width, times, height = size.strip().partition("x")
        return bool(space and comma and times) and all(map(is_number, (x, y, width, height)))
    return bool(text) and len(text.split()) == 1


def one_name(text):
    return bool(text) and len(text.split()) == 1


def parse(text, extras=None):
    """Returns (slots, local, shared): slots is a list of {button: code}, local is {button: [codes]}.
    Pass a dict as `extras` to get the mouse lines too: mouse, mouse_modes, zones, privates, hover, cursors."""
    extras = {} if extras is None else extras
    extras.update(mouse=None, mouse_modes=[], zones=[], privates=[], hover=None, cursors=None)
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
        elif line.startswith("mouse:"):
            mode = line[len("mouse:"):].strip()
            if mode not in MOUSE_MODES:
                fail("mouse is host, zones, buttons or all: " + mode)
            extras["mouse"] = mode
        elif line.startswith("mouse "):
            slot, colon, mode = line[len("mouse "):].partition(":")
            slot, mode = slot.strip(), mode.strip()
            if not colon or not slot.isdigit() or not 0 < int(slot) < MAX_PLAYERS or mode not in MOUSE_MODES:
                fail("expected mouse N: host, zones, buttons or all (N is 1 to %d)" % (MAX_PLAYERS - 1))
            extras["mouse_modes"].append((int(slot), mode))
        elif line.startswith("cursors:"):
            value = line[len("cursors:"):].strip()
            if value not in CURSORS:
                fail("cursors is auto, on or off: " + value)
            extras["cursors"] = value
        elif line.startswith("zone "):
            slot, colon, area = line[len("zone "):].partition(":")
            slot = slot.strip()
            if not colon or not slot.isdigit() or int(slot) >= MAX_PLAYERS or not zone_ok(area):
                fail("expected zone N: X,Y WxH or zone N: _root.clip")
            extras["zones"].append((int(slot), area.strip()))
        elif line.startswith("private:"):
            path, opened, openers = line[len("private:"):].partition(" opened-by ")
            if not one_name(path.strip()) or (opened and not one_name(openers.strip())):
                fail("expected private: _root.clip (opened-by _root.pattern)")
            extras["privates"].append((path.strip(), openers.strip() if opened else None))
        elif line.startswith("hover:"):
            value = line[len("hover:"):].strip()
            if value not in HOVERS:
                fail("hover is own or shared: " + value)
            extras["hover"] = value
        elif line.startswith("local:"):
            for button, codes in pairs(line[len("local:"):]):
                local.setdefault(button, []).extend(codes)
        elif line.startswith("slot "):
            head, _, items = line[len("slot "):].partition(":")
            if not _ or head.strip() != str(len(slots)) or len(slots) >= MAX_PLAYERS:
                fail("slots go 0, 1, 2 ... %d in order (got %s)" % (MAX_PLAYERS - 1, head.strip()))
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
        extras = {}
        slots, local, shared = parse(open(sys.argv[1], encoding="utf-8").read(), extras)
    except ValueError as e:
        sys.exit("%s: %s" % (sys.argv[1], e))
    print("%d players%s" % (len(slots), ", shared keys (hot-seat)" if shared else ""))
    for i, slot in enumerate(slots):
        print("  slot %d: %s" % (i, " ".join("%s=%d" % kv for kv in slot.items())))
    for name in ("mouse", "hover", "cursors"):
        if extras[name]:
            print("  %s: %s" % (name, extras[name]))
    for slot, mode in extras["mouse_modes"]:
        print("  mouse %d: %s" % (slot, mode))
    for slot, area in extras["zones"]:
        print("  zone %d: %s" % (slot, area))
    for path, openers in extras["privates"]:
        print("  private: %s%s" % (path, " opened-by " + openers if openers else ""))
    if any(slot >= len(slots) for slot, _ in extras["zones"] + extras["mouse_modes"]):
        print("  note: a zone or mouse line names a slot this map has no keys for")
    unused = sorted(b for b in local if not any(b in s for s in slots))
    if unused:
        print("  note: local keys for buttons no slot presses: " + ", ".join(unused))
    print("form OK; Ruffle Together's own loader (--coop-keys) is the final check")


if __name__ == "__main__":
    main()
