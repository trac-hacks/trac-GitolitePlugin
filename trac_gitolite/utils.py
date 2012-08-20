import os
import subprocess
from StringIO import StringIO
from tempfile import mkdtemp

def get_repo_node(env, repo_name, node):
    try:
        from tracopt.versioncontrol.git.PyGIT import GitError
    except ImportError: ## Pre-1.0 Trac
        from tracext.git.PyGIT import GitError
    from trac.core import TracError
    try:
        repo = env.get_repository(reponame=repo_name)
        return repo.get_node(node)
    except GitError:
        raise TracError("Error reading Git files at %s; check your repository path (for repo %s) and file permissions" % (node, repo_name))


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

def save_file(repo_path, file_path, contents, msg):
    tempdir = mkdtemp()
    subprocess.check_call(['git', 'clone', repo_path, tempdir])
    fp = open(os.path.join(tempdir, file_path), 'w')
    fp.write(contents)
    fp.close()
    subprocess.check_call(['git', 'add', file_path], cwd=tempdir)
    subprocess.check_call(['git', 'commit', '-m', msg], cwd=tempdir)
    subprocess.check_call(['git', 'push'], cwd=tempdir)

def remove_files(repo_path, file_paths, msg):
    tempdir = mkdtemp()
    subprocess.check_call(['git', 'clone', repo_path, tempdir])
    for file_path in file_paths:
        subprocess.check_call(['git', 'rm', file_path], cwd=tempdir)
    subprocess.check_call(['git', 'commit', '-m', msg], cwd=tempdir)
    subprocess.check_call(['git', 'push'], cwd=tempdir)
    
