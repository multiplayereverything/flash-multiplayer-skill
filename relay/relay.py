"""Old entry point, kept so existing launchers and the mods' labs (which run relay.py) keep working: runs init.py.
The relay lives in init.py (start-up, one port), relay-flash.py (star rooms), relay-unity.py (tunnel rooms) and
relay-common.py (shared parts)."""
import importlib.util
import os
import sys

spec = importlib.util.spec_from_file_location("relay_init", os.path.join(os.path.dirname(os.path.abspath(__file__)), "init.py"))
init = importlib.util.module_from_spec(spec)
sys.modules["relay_init"] = init
spec.loader.exec_module(init)

if __name__ == "__main__":
    init.main()
