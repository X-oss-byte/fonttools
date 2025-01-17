# Copyright 2013 Google, Inc. All Rights Reserved.
#
# Google Author(s): Behdad Esfahbod, Roozbeh Pournader


class Options(object):
    class UnknownOptionError(Exception):
        pass

    def __init__(self, **kwargs):

        self.verbose = False
        self.timing = False
        self.drop_tables = []

        self.set(**kwargs)

    def set(self, **kwargs):
        for k, v in kwargs.items():
            if not hasattr(self, k):
                raise self.UnknownOptionError(f"Unknown option '{k}'")
            setattr(self, k, v)

    def parse_opts(self, argv, ignore_unknown=[]):
        ret = []
        opts = {}
        for a in argv:
            orig_a = a
            if not a.startswith("--"):
                ret.append(a)
                continue
            a = a[2:]
            i = a.find("=")
            op = "="
            if i == -1:
                if a.startswith("no-"):
                    k = a[3:]
                    v = False
                else:
                    k = a
                    v = True
            else:
                k = a[:i]
                if k[-1] in "-+":
                    op = f"{k[-1]}="
                    k = k[:-1]
                v = a[i + 1 :]
            ok = k
            k = k.replace("-", "_")
            if not hasattr(self, k):
                if ignore_unknown is not True and ok not in ignore_unknown:
                    raise self.UnknownOptionError(f"Unknown option '{a}'")

                ret.append(orig_a)
                continue
            ov = getattr(self, k)
            if isinstance(ov, bool):
                v = bool(v)
            elif isinstance(ov, int):
                v = int(v)
            elif isinstance(ov, list):
                vv = v.split(",")
                if vv == [""]:
                    vv = []
                vv = [int(x, 0) if len(x) and x[0] in "0123456789" else x for x in vv]
                if op == "+=":
                    v = ov
                    v.extend(vv)
                elif op == "-=":
                    v = ov
                    for x in vv:
                        if x in v:
                            v.remove(x)
                elif op == "=":
                    v = vv
                else:
                    assert 0

            opts[k] = v
        self.set(**opts)

        return ret
