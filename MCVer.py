class MCVer:
    type = 0
    week = 0
    year = 0
    pre  = 0
    rev  = None
    near = []
    full = None
    
    def __init__(self, version):
        self.full = version
        lower = version.lower().replace('-', '_')
        if 'default' == lower: #Not a MC Version, sort bottom
            pass
        elif '15w14a' == lower: #2015 April Fools
            self.week = 14
            self.year = 15
            self.type = 3
            self.rev  = 'a'
            self.near = [1, 10]
        elif '1.rv_pre1' == lower: #2016 April Fools
            self.week = 14
            self.year = 16
            self.type = 3
            self.rev  = char(ord('a') - 1)
            self.near = [1, 9, 3]
        elif '3d shareware v1.34' == lower: #2019 April Fools
            self.week = 14
            self.year = 19
            self.type = 3
            self.rev  = char(ord('a') - 1)
            self.near = [1, 14]
        elif version[0] == 'a' or version[0] == 'b':
            clean = version[1:].replace('_', '.')
            self.type = 1 if version[0] == 'a' else 2
            if clean[-1] < '0' or clean[-1] > '9':
                self.rev = clean[-1]
                self.near = self.splitDots(clean[0:-1])
            else:
                self.near = self.splitDots(clean)
        elif len(version) == 6 and version[2] == 'w':
            self.year = int(version[0:2])
            self.week = int(version[3:5])
            self.type = 3
            self.rev  = version[5:]
            self.near = self.splitDots(self.fromSnapshot(year, week))
        else:
            self.type = 4
            for suffix in ['_pre_release_', ' pre_release ', '_pre']:
                if suffix in self.full:
                    pts = self.full.split(suffix)
                    self.pre = int(pts[1])
                    self.near = self.splitDots(pts[0])
                    break
                    
            if self.near == []:
                self.near = self.splitDots(self.full)
            
    def splitDots(self, ver):
        return [int(i) for i in ver.split('.')]
    
    def fromSnapshot(self, year, week):
        value = (year * 100) + week
        if value >= 1147 and value <= 1201: return '1.1'
        if value >= 1203 and value <= 1208: return '1.2'
        if value >= 1215 and value <= 1230: return '1.3'
        if value >= 1232 and value <= 1242: return '1.4'
        if value >= 1249 and value <= 1250: return '1.4.6'
        if value >= 1301 and value <= 1310: return '1.5'
        if value >= 1311 and value <= 1312: return '1.5.1'
        if value >= 1316 and value <= 1326: return '1.6'
        if value >= 1336 and value <= 1343: return '1.7'
        if value >= 1347 and value <= 1349: return '1.7.4'
        if value >= 1402 and value <= 1434: return '1.8'
        if value >= 1531 and value <= 1607: return '1.9'
        if value >= 1614 and value <= 1615: return '1.9.3'
        if value >= 1620 and value <= 1621: return '1.10'
        if value >= 1632 and value <= 1644: return '1.11'
        if value >= 1650 and value <= 1650: return '1.11.1'
        if value >= 1706 and value <= 1718: return '1.12'
        if value >= 1731 and value <= 1731: return '1.12.1'
        if value >= 1743 and value <= 1822: return '1.13'
        if value >= 1830 and value <= 1833: return '1.13.1'
        if value >= 1843 and value <= 1914: return '1.14'
        if value >= 1934 and value <= 9999: return '1.15'
        raise Exception('Invalid snapshot date: %s' % (value))

    def compareStr(self, s1, s2):
        return (s1 > s2) - (s1 < s2)

    def compareFull(self, o):
        for i in range(len(self.near)):
            if i >= len(o.near): return 1
            if self.near[i] != o.near[i]: return self.near[i] - o.near[i]
        return 0 if len(o.near) == len(self.near) else -1
        
    def compare(self, o):
        if self.type != o.type:
            if self.type == 1: return -1
            if self.type == 2: return 1 if self.type == 1 else -1
            if self.type == 3: return -1 if self.compareFull(o) == 0 else 1
            return 1 if self.compareFull(o) == 0 else -1
            
        if self.type == 1 or self.type == 2:
            ret = self.compareFull(o)
            if ret != 0: return ret
            if self.rev == None and o.rev != None: return 1
            if self.rev != None and o.rev == None: return -1
            return self.compareStr(self.rev, o.rev)
            
        elif self.type == 3:
            if self.year != o.year: return self.year - o.year
            if self.week != o.week: return self.week - o.week
            return self.compareStr(self.rev, o.rev)
            
        return self.compareFull(o)
        
    def __lt__(self, other):
        return self.compare(other) < 0
    def __gt__(self, other):
        return self.compare(other) > 0
    def __eq__(self, other):
        return self.compare(other) == 0
    def __le__(self, other):
        return self.compare(other) <= 0
    def __ge__(self, other):
        return self.compare(other) >= 0
    def __ne__(self, other):
        return self.compare(other) != 0