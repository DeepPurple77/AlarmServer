#deeppurple for Python3
def safe_write(stream, data, encoding='ascii'):
    if isinstance(data, str):
        data = data.encode(encoding)
    return stream.write(data)

def safe_str(data):
    return data.decode('ascii', errors='ignore') if isinstance(data, bytes) else data
