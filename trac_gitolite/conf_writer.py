from trac.admin import IAdminPanelProvider
from trac.core import *
from trac.config import Option, BoolOption
from trac.util.translation import _

from trac_gitolite import utils

class GitoliteConfWriter(Component):
    implements(IAdminPanelProvider)

    gitolite_admin_reponame = Option('trac-gitolite', 'admin_reponame',
                                     default="gitolite-admin")

    def read_config(self):
        repo = self.env.get_repository(reponame=self.gitolite_admin_reponame)
        node = repo.get_node("conf/gitolite.conf")
        fp = node.get_content()
        return utils.read_config(fp)
    
    ## IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'VERSIONCONTROL_ADMIN' in req.perm:
            yield ('versioncontrol', _('Version Control'), 'permissions', 
                   _('Permissions'))

    def render_admin_panel(self, req, category, page, path_info):
        req.perm.require('VERSIONCONTROL_ADMIN')

        perms = self.read_config()

        if req.method == 'POST':
            req.redirect(req.href.admin(category, page))
        
        data = {'perms': perms}
        return 'admin_repository_permissions.html', data
