from trac.core import *
from trac.config import Option, BoolOption
from trac.perm import IPermissionPolicy

class GitoliteMultiRepoPermissionPolicyProvider(Component):
    implements(IPermissionPolicy)

    gitolite_admin_reponame = Option('multirepo-permissions', 'gitolite_admin_reponame',
                                     default="gitolite-admin")
    default_to_private = BoolOption(
        'multirepo-permissions', 'default_private', 
        default=False,
        doc=("If this flag is set to True, then repositories will be private by default, "
             "causing all permissions to be denied to all users if the repository "
             "is not mentioned in the gitolite conf file."))
    all_includes_anonymous = BoolOption(
        'multirepo-permissions', 'all_includes_anonymous', 
        default=False,
        doc=("If this flag is set to True, then anonymous users will be granted permissions "
             "on repositories that specify ``@all = R``.  By default, the ``@all`` token "
             "is considered to mean all logged-in users only."))
    
    ## Helper methods

    def parent_repository(self, resource):
        while True:
            if resource is None:
                return None
            if resource.realm == 'repository':
                return resource
            resource = resource.parent

    def read_config(self):
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

    def check_repository_permission(self, action, username, repository, resource, perm):
        repos = self.read_config()
        if username != 'anonymous' and username in repos.get(repository.id, []):
            return True
        if '@all' in repos.get(repository.id, []):
            if username != 'anonymous':
                return True
            elif self.all_includes_anonymous:
                return True

        ## If the repo is known in the config but the user isn't explicitly granted access there,
        ## then the user does not have access.
        if repository.id in repos:
            return False

        ## If the repo is not known in the config, we defer to the supersystem's decisions,
        ## unless our configuration says otherwise.
        if self.default_to_private:
            return False
        return None

    ## IPermissionPolicy methods
            
    def check_permission(self, action, username, resource, perm):
        ## This policy only covers entities that live within a repository
        ## so we'll decline to state any permission if it's not a repository subresource
        repository = self.parent_repository(resource)
        if repository is None:
            return None

        return self.check_repository_permission(action, username, repository, resource, perm)

