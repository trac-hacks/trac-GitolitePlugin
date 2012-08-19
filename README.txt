This plugin provides two-way integration with gitolite: https://github.com/sitaramc/gitolite

 1. Users who don't have read access to a repository in Gitolite will be blocked from viewing that repository in Trac's web browser
 2. Trac admins may manage users' gitolite-based repository permissions through the Trac web interface
 3. Trac admins may add and remove users' SSH public keys through the Trac web interface to control access to the gitolite system
 4. Trac admins may use a "Create New Repository" feature to initialize an empty gitolite repository through the Trac web interface

## Installation 

First, install both Trac and Gitolite in the standard ways.  They must
be installed on the same server.

You will need to ensure that Trac has read access to the filesystem
directory that contains your gitolite repositories.  If Trac is
running as user "trac" and gitolite has been installed to run as user
"git" with a homedir /var/lib/gitolite/ created during gitolite
installation, you will probably want to run a command on your server
like this::

  sudo usermod -a -G gitolite trac
  sudo chmod -R g+r /var/lib/gitolite/repositories/

Now Trac will be able to read from your gitolite repositories using its
standard repository features.  

To add an existing gitolite repository named "my-first-repo" to your
Trac system, you would add a Trac git repository named "my-first-repo"
with directory `/var/lib/gitolite/repositories/my-first-repo.git`
through Trac's standard administrative web interface or configuration
files.

Next, you will need to grant the Trac system user read and write
permissions on the gitolite-admin repository through gitolite itself.
To do this -- again supposing that Trac is running as user "trac" --
you will run commands on your server like this::

  sudo su trac
  ssh-keygen
  exit
  cd /tmp/
  git clone git@localhost:gitolite-admin.git
  cd /tmp/gitolite-admin/
  echo "repo    gitolite-admin
      RW = trac" >> ./conf/gitolite.conf
  sudo cp ~trac/.ssh/id_rsa.pub ./keydir/trac.pub
  git add keydir/trac.pub conf/gitolite.conf
  git commit -m "configuring trac_gitolite permissions"
  git push

Finally, enable the trac_gitolite components in trac.ini for your site::

  [components]
  trac_gitolite.* = enabled

This will add three new panels to the "Version Control" section in the Trac Admin.  To additionally enable the permission policy, add to your trac.ini::

  [trac]
  permission_policies = GitolitePermissionPolicy, AuthzPolicy, 
                        DefaultPermissionPolicy, LegacyAttachmentPolicy

