import pkg_resources

from trac.admin import IAdminPanelProvider
from trac.core import *
from trac.config import Option, BoolOption
from trac.util.translation import _
from trac.web.chrome import ITemplateProvider
from trac.web.chrome import add_notice, add_warning

from trac_gitolite import utils

class GitoliteUserManager(Component):
    implements(IAdminPanelProvider, ITemplateProvider)

    gitolite_admin_reponame = Option('trac-gitolite', 'admin_reponame',
                                     default="gitolite-admin")
    gitolite_admin_ssh_path = Option('trac-gitolite', 'admin_ssh_path',
                                     default="git@localhost:gitolite-admin.git")

    def get_users(self):
        node = utils.get_repo_node(self.env, self.gitolite_admin_reponame, 
                                   "keydir")
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

        if req.method == 'POST':

            if 'add_user' in req.args:
                username = req.args['name']
                pubkey = req.args['sshkey'].file
                
                utils.save_file(self.gitolite_admin_ssh_path, 'keydir/%s.pub' % username,
                                pubkey.read(), _('Adding new user %s' % username))

                add_notice(req, _('User "%s" has been added.  Visit the repository permissions panel to set up the new user\'s read/write permissions.' % (
                            username)))
                req.redirect(req.href.admin(category, page))

            users = ['keydir/%s.pub' % username for username in req.args.get('remove_user', [])]
            if users:
                utils.remove_files(self.gitolite_admin_ssh_path, users, _('Removing users'))
                add_notice(req, _('The selected users have been removed and no longer have SSH access to your repositories.  Note that if they have Trac accounts, they may still be able to browse the source code through the web.'))
            else:
                add_warning(req, _('No users were selected.'))
            req.redirect(req.href.admin(category, page))

        data = {'users': self.get_users()}
        return 'admin_repository_users.html', data

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('trac_gitolite', 'templates')]
