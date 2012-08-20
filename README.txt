This plugin provides two-way integration with gitolite: https://github.com/sitaramc/gitolite

1. Users who don't have read access to a repository in Gitolite will be blocked from viewing that repository in Trac's web browser
2. Trac admins may manage users' gitolite-based repository permissions through the Trac web interface
3. Trac admins may add and remove users' SSH public keys through the Trac web interface to control access to the gitolite system
4. Trac admins may use a "Create New Repository" feature to initialize an empty gitolite repository through the Trac web interface

Installation 
============

Overview
--------

1. Install Trac and Gitolite on the same server.
2. Ensure that the system user running the Trac process has filesystem
   read access to all gitolite repositories in the present and
   future.  The simplest way to do this is to run Trac as the gitolite
   user; the more correct way is to add Trac to the gitolite user's
   primary group and set ``UMASK=>0027`` in ``.gitolite.rc`` as well as
   running chmod to fix up permissions on the already-created files.
3. Ensure that the system user running the Trac process can clone and
   push the gitolite-admin repository, by setting up an SSH keypair
   for the Trac user, adding that public key to ``gitolite-admin/keydir``
   and adding RW+ (or just RW) permissions to the corresponding user
   in ``gitolite-admin/conf/gitolite.conf`` for "repo gitolite-admin".
4. Tell Trac about the existence of the gitolite-admin repository by
   running a command like ``trac-admin <env> repository add
   gitolite-admin $GITOLITE_HOME/repositories/gitolite-admin.git git``
5. Install the trac_gitolite plugin, enable its components in trac.ini
   and prepend "GitolitePermissionPolicy" to your site's trac.ini
   permission_policies settings.


Detailed Instructions
---------------------

First, install both Trac and Gitolite in the standard ways.  They must
be installed on the same server.

You will need to ensure that Trac has the necessary read access to the 
filesystem directory that contains your gitolite repositories.  If Trac 
is running as user "wsgi" and gitolite has been installed to run as user
"git" with a homedir /home/git/ you will probably want to run a command 
on your server like this::

  sudo usermod -a -G git wsgi
  sudo chmod -R g+rX /home/git/repositories/

You will also need to ensure that Trac can continue to read all needed
files over time.  One way to do this is to set the UMASK setting in
``.gitolite.rc`` to 0027.  Another way would be to set the repository
configuration ``core.sharedRepository = group`` in all existing and new
repositories (including gitolite-admin) using a repository template.

Now Trac will be able to read from your gitolite repositories using its
standard repository features.  

You then need to add the gitolite-admin repository itself to Trac.
This will allow Trac to read configuration files directly from the
gitolite-admin repository using its own version-control APIs.  Do this
with a command line::

  trac-admin /path/to/env/ repository add gitolite-admin /home/git/repositories/gitolite-admin.git git

From now on, to add an existing gitolite repository named
"my-first-repo" to your
Trac system, you would add a Trac git repository named "my-first-repo"
with directory ``/home/git/repositories/my-first-repo.git``
through Trac's standard administrative web interface, shell scripts,
or configuration files.

Next, you will need to grant the Trac system user read and write
permissions on the gitolite-admin repository through gitolite itself.
This is how Trac will write changes to your Gitolite system (web-based
user, permission and repository management) -- it will clone the
gitolite-admin repo, write changes, commit and push them back to the
server. 

To do this -- again supposing that Trac is running as user "wsgi" --
you will run commands on your server like this::

  sudo su wsgi
  ssh-keygen
  exit
  cd /tmp/
  git clone git@localhost:gitolite-admin.git
  cd /tmp/gitolite-admin/
  echo "repo    gitolite-admin
      RW+ = wsgi" >> ./conf/gitolite.conf
  sudo cp ~wsgi/.ssh/id_rsa.pub ./keydir/wsgi.pub
  git add keydir/wsgi.pub conf/gitolite.conf
  git commit -m "configuring trac_gitolite permissions"
  git push

Finally, enable the trac_gitolite components in trac.ini for your site::

  [components]
  trac_gitolite.* = enabled

This will add three new panels to the "Version Control" section in the Trac Admin.  To additionally enable the permission policy, add to your trac.ini::

  [trac]
  permission_policies = GitolitePermissionPolicy, AuthzPolicy, 
                        DefaultPermissionPolicy, LegacyAttachmentPolicy

