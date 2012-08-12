from trac.core import *
from trac.config import Option, BoolOption
from trac.perm import IPermissionPolicy

from trac_gitolite import utils

class GitolitePermissionPolicy(Component):
    implements(IPermissionPolicy)

    gitolite_admin_reponame = Option('trac-gitolite', 'admin_reponame',
                                     default="gitolite-admin")
    default_to_private = BoolOption('trac-gitolite', 'default_private',
                                    default=False,
        doc=("If this flag is set to True, then repositories will be private by default, "
             "causing all permissions to be denied to all users if the repository "
             "is not mentioned in the gitolite conf file."))
    all_includes_anonymous = BoolOption('trac-gitolite', 'all_includes_anonymous'
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
        return utils.read_config(self.env, self.gitolite_admin_reponame)

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

