import pkg_resources

from trac.admin import IAdminPanelProvider
from trac.core import *
from trac.config import Option, BoolOption
from trac.util.translation import _
from trac.web.chrome import ITemplateProvider

from trac_gitolite import utils

class GitoliteUserManager(Component):
    implements(IAdminPanelProvider, ITemplateProvider)

    gitolite_admin_reponame = Option('trac-gitolite', 'admin_reponame',
                                     default="gitolite-admin")

    def get_users(self):
        repo = self.env.get_repository(reponame=self.gitolite_admin_reponame)
        node = repo.get_node("keydir")
        assert node.isdir, "Node %s at /keydir/ is not a directory" % node
        for child in node.get_entries():
            name = child.get_name()
            assert name.endswith(".pub"), "Node %s" % name
            yield name[:-4]

    ## IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'VERSIONCONTROL_ADMIN' in req.perm:
            yield ('versioncontrol', _('Version Control'), 'users', 
                   _('Users'))

    def render_admin_panel(self, req, category, page, path_info):
        req.perm.require('VERSIONCONTROL_ADMIN')

        pass

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('trac_gitolite', 'templates')]
