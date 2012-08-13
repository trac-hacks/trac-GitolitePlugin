import pkg_resources

from trac.admin import IAdminPanelProvider
from trac.core import *
from trac.config import Option, BoolOption
from trac.util.translation import _
from trac.web.chrome import ITemplateProvider

from trac_gitolite import utils

class GitoliteConfWriter(Component):
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
        
        flattened_perms = set()
        for p in perms.values():
            for perm in p:
                flattened_perms.add(perm)
        flattened_perms = list(flattened_perms)
        def sort_perms(perms):
            tail = []
            ## Ensure the + goes last
            if '+' in perms:
                perms.remove("+")
                tail.append("+")
            perms = sorted(perms)
            perms.extend(tail)
            return perms
        flattened_perms = sort_perms(flattened_perms)

        data = {'repositories': perms, 'permissions': flattened_perms, 'users': list(self.get_users()),
                'sort_perms': sort_perms}
        return 'admin_repository_permissions.html', data

    # ITemplateProvider methods

    def get_htdocs_dirs(self):
        return []

    def get_templates_dirs(self):
        return [pkg_resources.resource_filename('trac_gitolite', 'templates')]
