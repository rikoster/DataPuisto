LONGTIME = 28800

def status_ok(result):
    return result['status'] in ['Ok', 'OK', '0', 0]

def status_manual(result):
    return result['status'] == 'Manual'
