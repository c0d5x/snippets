

def is_running(process):
    import subprocess
    import re
    try:  # Linux/Unix
        sout = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
    except:  # Windows
        sout = subprocess.Popen(["tasklist", "/v"], stdout=subprocess.PIPE)
    for x in sout.stdout:
        if re.search(process, x):
            return True
    return False
