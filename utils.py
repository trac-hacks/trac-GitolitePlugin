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
                    info[perm] = users

    if this_repo is not None and len(info) > 0:
        repos[this_repo] = info

    fp.close()
    return repos
