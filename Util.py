import hashlib
import os
    
def writeFile(path, data):
    ensureDir(os.path.dirname(path))
    
    print('  Writing %s' % (path))
    
    with open(path, 'wb') as f:
        f.write(data)
        
    return True
    
def writeFileHashed(path, data):
    ensureDir(os.path.dirname(path))
    md5 = hashlib.md5(data).hexdigest()
    sha1 = hashlib.sha1(data).hexdigest()
    
    if md5 == getFirstFileLine(path + '.md5') and sha1 == getFirstFileLine(path + '.sha1'):
        return False
    
    print('  Writing %s' % (path))
    
    with open(path, 'wb') as f:
        f.write(data)
    with open(path + '.md5', 'wb') as f:
        f.write(md5.encode('utf-8'))
    with open(path + '.sha1', 'wb') as f:
        f.write(sha1.encode('utf-8'))
        
    return True
    
def writeFileMD5ed(path, data):
    ensureDir(os.path.dirname(path))
    md5 = hashlib.md5(data).hexdigest()
    
    if md5 == getFirstFileLine(path + '.md5'):
        return False
    
    print('  Writing %s' % (path))
    
    with open(path, 'wb') as f:
        f.write(data)
    with open(path + '.md5', 'wb') as f:
        f.write(md5.encode('utf-8'))
        
    return True
        
def getFirstFileLine(filename):
    try:
        if not os.path.exists(filename):
            return ''
        with open(filename, 'r') as f:
            line = f.readline()
        return line
    except: return ''
    
def readFile(filename):
    try:
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as f:
            return f.read()
    except: return None
    
def ensureDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
  