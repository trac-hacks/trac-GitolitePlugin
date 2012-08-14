import pkg_resources

from trac.admin import IAdminPanelProvider
from trac.core import *
from trac.config import Option, BoolOption
from trac.perm import IPermissionRequestor
from trac.util.translation import _
from trac.versioncontrol import DbRepositoryProvider
from trac.web.chrome import ITemplateProvider
from trac.web.chrome import add_notice, add_warning

from trac_gitolite import utils

class GitoliteRepositoryManager(Component):
    implements(IPermissionRequestor, IAdminPanelProvider, ITemplateProvider)

    gitolite_admin_reponame = Option('trac-gitolite', 'admin_reponame',
                                     default="gitolite-admin")

    def read_config(self):
        repo = self.env.get_repository(reponame=self.gitolite_admin_reponame)
        node = repo.get_node("conf/gitolite.conf")
        fp = node.get_content()
        return utils.read_config(fp)
    
    ## IPermissionRequestor methods

    def get_permission_actions(self):
        return [('VERSIONCONTROL_ADMIN', ['REPOSITORY_CREATE']),
                'REPOSITORY_CREATE']

    ## IAdminPanelProvider methods

    def get_admin_panels(self, req):
        if 'REPOSITORY_CREATE' in req.perm:
            yield ('versioncontrol', _('Version Control'), 'gitolite', 
                   _('Gitolite Repositories'))

    def render_admin_panel(self, req, category, page, path_info):
        req.perm.require('REPOSITORY_CREATE')

        if req.method == 'POST':

            req.redirect(req.href.admin(category, page))

        data = {'repos': sorted(self.read_config())}
        return 'admin_repository_gitolite.html', data

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('trac_gitolite', 'templates')]
