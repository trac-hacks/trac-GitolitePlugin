from StringIO import StringIO

def read_config(fp):
    repos = dict()
    this_repo = None
    info = {}
    for line in fp:
        line = line.strip()
        if line.startswith("repo"):
            if this_repo is not None and len(info) > 0:
                repos[this_repo] = info
            this_repo = line[len("repo"):].strip()
            info = {}
        elif '=' in line:
            perms, users = line.split("=")
            perms = perms.strip().upper()
            users = [i.strip() for i in users.split()]
            for perm in perms:
                if perm in info:
                    info[perm].extend(users)
                else:
                    info[perm] = list(users) ## Copy it!

    if this_repo is not None and len(info) > 0:
        repos[this_repo] = info

    fp.close()
    return repos


def to_string(config):

    def _sort(perms):
        tail = []
        ## Ensure the + goes last
        if '+' in perms:
            perms = perms.replace("+", '')
            tail.append("+")
        perms = sorted(perms)
        perms.extend(tail)
        return ''.join(perms)

    fp = StringIO()
    for repo in sorted(config):
        fp.write("repo\t%s\n" % repo)

        ## Combine permissions
        perms = config[repo]
        transposed = {}
        for perm in perms:
            for user in perms[perm]:
                if user in transposed:
                    transposed[user] += perm
                    transposed[user] = _sort(transposed[user])
                else:
                    transposed[user] = perm


        detransposed = {}
        for user in transposed:
            if transposed[user] in detransposed:
                detransposed[transposed[user]].append(user)
                detransposed[transposed[user]] = sorted(detransposed[transposed[user]])
            else:
                detransposed[transposed[user]] = [user]

        for permset in sorted(detransposed):
            fp.write("\t%s\t=\t%s\n" % (permset, ' '.join(detransposed[permset])))

        fp.write("\n")
    fp.seek(0)
    return fp.read()

