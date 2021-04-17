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
            self.rev = version[5:]
            self.near = self.splitDots(self.fromSnapshot(self.year, self.week))
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
        range(1147, 1201): '1.1',
        range(1203, 1208): '1.2',
        range(1215, 1230): '1.3',
        range(1232, 1242): '1.4',
        range(1249, 1250): '1.4.6',
        range(1301, 1310): '1.5',
        range(1311, 1312): '1.5.1',
        range(1316, 1326): '1.6',
        range(1336, 1343): '1.7',
        range(1347, 1349): '1.7.4',
        range(1402, 1434): '1.8',
        range(1531, 1607): '1.9',
        range(1614, 1615): '1.9.3',
        range(1620, 1621): '1.10',
        range(1632, 1644): '1.11',
        range(1650, 1650): '1.11.1',
        range(1706, 1718): '1.12',
        range(1731, 1731): '1.12.1',
        range(1743, 1822): '1.13',
        range(1830, 1833): '1.13.1',
        range(1843, 1914): '1.14',
        range(1934, 9999): '1.15'
    })

    def fromSnapshot(self, year, week):
        value = (year * 100) + week
        if ver := SNAPSHOT_RANGES.get(value, None):
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

    def __repr__(self):
        return self.full