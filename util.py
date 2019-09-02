
def reconnect(signal, newhandler=None, oldhandler=None):
    while True:
        try:
            if oldhandler is not None:
                signal.disconnect(oldhandler)
            else:
                signal.disconnect()
        except TypeError:
            break
    if newhandler is not None:
        signal.connect(newhandler)

def compute_completeness(jd):
    finished = sum(jd['finished'])
    total = len(jd['finished'])
    return finished,total
