import getpass
import pkg_resources

from trac.admin import IAdminPanelProvider
from trac.core import *
from trac.config import Option, BoolOption
from trac.perm import IPermissionRequestor
from trac.util.translation import _
from trac.web.chrome import ITemplateProvider
from trac.web.chrome import add_notice, add_warning

from trac_gitolite import utils

class GitoliteRepositoryManager(Component):
    implements(IPermissionRequestor, IAdminPanelProvider, ITemplateProvider)

    gitolite_admin_reponame = Option('trac-gitolite', 'admin_reponame',
                                     default="gitolite-admin")
    gitolite_admin_ssh_path = Option('trac-gitolite', 'admin_ssh_path',
                                     default="git@localhost:gitolite-admin.git")

    def read_config(self):
        node = utils.get_repo_node(self.env, self.gitolite_admin_reponame,
                                   "conf/gitolite.conf")
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
            repo_name = req.args['name']
            perms = self.read_config()
            if repo_name in perms:
                add_warning(req, _('A repository named %s already exists; maybe you just need to tell Trac about it using the Repositories panel?'))
                req.redirect(req.href.admin(category, page))
            perms[repo_name] = repo_perms = {}
            trac_user = getpass.getuser()
            for perm in ['R', 'W', '+']:
                repo_perms[perm] = [trac_user]
            utils.save_file(self.gitolite_admin_ssh_path, 'conf/gitolite.conf',
                            utils.to_string(perms),
                            _('Adding new repository %s' % repo_name))
            add_notice(req, _('Repository "%s" has been created.  Now you should give some users permissions on it using the Version Control Permissions panel.' % repo_name))
            req.redirect(req.href.admin(category, page))

        data = {'repos': sorted(self.read_config())}
        return 'admin_repository_gitolite.html', data

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('trac_gitolite', 'templates')]
