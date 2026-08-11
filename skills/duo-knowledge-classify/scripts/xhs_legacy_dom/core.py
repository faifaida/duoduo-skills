import subprocess, time, os

JS_DIR = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(JS_DIR, "_run.js")

def osa(script, timeout=60):
    p = subprocess.run(['osascript', '-e', script], capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError('osa_err: ' + p.stderr.strip()[:300])
    return p.stdout.strip()

def run_js(win, js_filename, timeout=40):
    js = open(os.path.join(JS_DIR, js_filename)).read()
    open(TMP, 'w').write(js)
    script = '''
    tell application "Google Chrome"
      tell window id %d
        tell tab 1
          set r to execute javascript (read (POSIX file "%s"))
        end tell
      end tell
      return r
    end tell''' % (win, TMP)
    return osa(script, timeout)

def launch(url, tries=4):
    last=None
    for i in range(tries):
        try:
            script = '''
            tell application "Google Chrome"
              activate
              set w to make new window
              set t to active tab of w
              set URL of t to "%s"
              return id of w
            end tell''' % url
            return int(osa(script, 60).strip())
        except Exception as e:
            last=e
            time.sleep(3)
    raise RuntimeError('launch failed after retries: %s' % last)

def close_win(win):
    try:
        osa('tell application "Google Chrome" to close window id %d' % win, 20)
    except: pass

def relaunch_chrome():
    try: osa('tell application "Google Chrome" to quit', 10)
    except: pass
    time.sleep(3)
    osa('do shell script "open -a \\"Google Chrome\\""', 15)
    time.sleep(5)
