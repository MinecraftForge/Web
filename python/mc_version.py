class MCVer:
    type = 0
    week = 0
    year = 0
    pre = 0
    rev = None
    near = []
    full = None

    def __init__(self, version):
        self.full = version
        lower = version.lower().replace('-', '_')
        if 'default' == lower:  # Not a MC Version, sort bottom
            pass
        elif '15w14a' == lower:  # 2015 April Fools
            self.week = 14
            self.year = 15
            self.type = 3
            self.rev = 'a'
            self.near = [1, 10]
        elif '1.rv_pre1' == lower:  # 2016 April Fools
            self.week = 14
            self.year = 16
            self.type = 3
            self.rev = chr(ord('a') - 1)
            self.near = [1, 9, 3]
        elif '3d shareware v1.34' == lower:  # 2019 April Fools
            self.week = 14
            self.year = 19
            self.type = 3
            self.rev = chr(ord('a') - 1)
            self.near = [1, 14]
        elif '20w14infinite' == lower:  # 2020 April Fools
            self.week = 14
            self.year = 20
            self.type = 3
            self.rev = chr(ord('a') - 1)
            self.near = [1, 16]
        elif '22w13oneblockatatime' == lower:  # 2022 April Fools
            self.week = 13
            self.year = 22
            self.type = 3
            self.rev = 'b'
            self.near = [1, 19]
        elif '23w13a_or_b' == lower:  # 2023 April Fools
            self.week = 13
            self.year = 23
            self.type = 3
            self.rev = 'b'
            self.near = [1, 20]
        elif 'inf_20100618' == lower:
            self.week = 25
            self.year = 10
            self.type = 1
            self.rev = 'a'
            self.near = [1, 0, 4]
        elif 'c0.0.13a_03' == lower:
            self.week = -1
            self.year = -1
            self.type = 1
            self.rev = chr(ord('a') - 1)
            self.near = [0, 0, 13]
        elif lower.startswith('rd_'):
            self.week = 20
            self.year = 9
            self.type = 1
            
            if 'rd_132211' == lower: self.rev = 'a'
            if 'rd_132328' == lower: self.rev = 'b'
            if 'rd_20090515' == lower: self.rev = 'c'
            if 'rd_160052' == lower: self.rev = 'd'
            if 'rd_161348' == lower: self.rev = 'e'

            self.near = [0, 0, 1]
        elif version[0] == 'a' or version[0] == 'b' or version[0] == 'c':
            clean = version[1:].replace('_', '.')
            self.type = 2 if version[0] == 'b' else 1
            if clean[-1] < '0' or clean[-1] > '9':
                self.rev = clean[-1]
                self.near = self.splitDots(clean[0:-1])
            else:
                self.near = self.splitDots(clean)
        elif len(version) == 6 and version[2] == 'w':
            self.year = int(version[0:2])
            self.week = int(version[3:5])
            self.type = 3
            self.rev = version[5:]
            self.near = self.splitDots(self.fromSnapshot(self.year, self.week))
        else:
            self.type = 4
            for suffix in ['_pre_release_', ' pre_release ', ' Pre-Release ', '_pre', '-pre', '-rc']:
                if suffix in self.full:
                    pts = self.full.split(suffix)
                    self.pre = int(pts[1])
                    if suffix == '-rc':
                        self.pre *= -1
                    self.near = self.splitDots(pts[0])
                    break

            if self.near == []:
                self.near = self.splitDots(self.full)

    def splitDots(self, ver):
        return [int(i) for i in ver.split('.')]

    class RangedDict(dict):
        def __getitem__(self, item):
            if not isinstance(item, range):
                for key in self:
                    if item in key:
                        return self[key]
                raise KeyError(item)
            else:
                return super().__getitem__(item)

    SNAPSHOT_RANGES = RangedDict({
        range(1147, 1202): '1.1',
        range(1203, 1209): '1.2',
        range(1215, 1231): '1.3',
        range(1232, 1243): '1.4',
        range(1249, 1251): '1.4.6',
        range(1301, 1311): '1.5',
        range(1311, 1313): '1.5.1',
        range(1316, 1327): '1.6',
        range(1336, 1344): '1.7',
        range(1347, 1350): '1.7.4',
        range(1402, 1435): '1.8',
        range(1531, 1608): '1.9',
        range(1614, 1616): '1.9.3',
        range(1620, 1622): '1.10',
        range(1632, 1645): '1.11',
        range(1650, 1651): '1.11.1',
        range(1706, 1719): '1.12',
        range(1731, 1732): '1.12.1',
        range(1743, 1823): '1.13',
        range(1830, 1834): '1.13.1',
        range(1843, 1915): '1.14',
        range(1934, 1947): '1.15',
        range(2006, 2023): '1.16',
        range(2027, 2031): '1.16.2',
        range(2045, 2121): '1.17',
        range(2137, 2145): '1.18',
        range(2203, 2208): '1.18.2',
        range(2211, 2220): '1.19',
        range(2224, 2225): '1.19.1',
        range(2242, 2247): '1.19.3',
        range(2303, 2308): '1.19.4',
        range(2312, 9999): '1.20'
    })

    def fromSnapshot(self, year, week):
        value = (year * 100) + week
        if ver := self.SNAPSHOT_RANGES[value]:
            return ver
        raise Exception(f'Invalid snapshot date: {value}')

    def compareStr(self, s1, s2):
        return (s1 > s2) - (s1 < s2)

    def compareFull(self, o):
        for i in range(len(self.near)):
            if i >= len(o.near): return 1
            if self.near[i] != o.near[i]: return self.near[i] - o.near[i]
        return 0 if len(o.near) == len(self.near) else -1

    def compare(self, o):
        if self.type != o.type:
            if self.type <= 2 or o.type <= 2: return self.type - o.type
            if self.type == 3: return -1 if self.compareFull(o) == 0 else self.compareFull(o)
            return 1 if self.compareFull(o) == 0 else self.compareFull(o)

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

        ret = self.compareFull(o)
        if ret != 0: return ret
        self_pre_type = min(1, max(-1, self.pre))
        o_pre_type = min(1, max(-1, o.pre))
        if self_pre_type == o_pre_type: return abs(self.pre) - abs(o.pre)
        if self_pre_type == 0: return 1
        if o_pre_type == 0: return -1
        if self_pre_type == 1: return -1
        return 1
    
    def getFullRelease(self):
        return '.'.join(map(str, self.near)) if len(self.near) > 0 else self.full

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

    def __repr__(self):
        return self.full