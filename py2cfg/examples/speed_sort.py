class Sort:
    def merge(self, l, r):
        i = 0
        j = 0
        arr = []
        size = len(l) + len(r)
        for k in range(0, size):
            lSentinel = i == len(l)
            rSentinel = j == len(r)
            if i == len(l):
                arr.append(r[j])
                j += 1
            elif j == len(r):
                arr.append(l[i])
                i += 1
            elif l[i] <= r[j]:
                arr.append(l[i])
                i += 1
            else:
                arr.append(r[j])
                j += 1

        return arr

    def merge_sort(self, src):
        n = len(src) / 2
        l = src[0:n]
        r = src[n:]
        if len(l) > 1:
            l = self.merge_sort(l)
        if len(r) > 1:
            r = self.merge_sort(r)

        src = self.merge(l, r)
        return src

    def insertion_sort(self, src):
        j = 1
        for j in range(1, len(src)):
            i = j - 1
            key = src[j]
        while i >= 0 and src[i] >= key:
            src[i + 1] = src[i]
            i = i - 1
            src[i + 1] = key
        return src
