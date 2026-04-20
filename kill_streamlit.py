import os, signal
for p in os.listdir('/proc'):
    if p.isdigit():
        try:
            with open(f'/proc/{p}/cmdline', 'r') as f:
                cmd = f.read().replace('\0', ' ')
            if 'streamlit' in cmd:
                os.kill(int(p), signal.SIGKILL)
        except Exception:
            pass
