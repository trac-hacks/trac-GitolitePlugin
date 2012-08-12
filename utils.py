def read_config(env, reponame):
    repo = self.env.get_repository(reponame=self.gitolite_admin_reponame)
    node = repo.get_node("conf/gitolite.conf")

    fp = node.get_content()
    repos = dict()
    this_repo = None
    info = []
    for line in fp:
        line = line.strip()
        if line.startswith("repo"):
            if this_repo is not None and len(info) > 0:
                repos[this_repo] = info
            this_repo = line[len("repo"):].strip()
            info = []
        elif '=' in line:
            perms, users = line.split("=")
            perms = perms.strip()
            users = [i.strip() for i in users.split()]
            if 'R' not in perms.upper():
                continue
            info.extend(users)
        pass
    if this_repo is not None and len(info) > 0:
        repos[this_repo] = info

    fp.close()
    return repos
