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
   user; the more correct way is to add the Trac and Gitolite users to
   a shared group, set ``UMASK=>0027`` in ``.gitolite.rc`` as well as
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

  sudo groupadd infra
  sudo usermod -a -G infra wsgi
  sudo usermod -a -G infra git
  sudo chown -R git:infra /home/git/repositories/
  sudo chmod -R g+rXs /home/git/repositories/

(The +s ensures that new files created in the git repositories, like
new commit objects in the repos, will retain the "infra" group-ownership
rather than reverting to the git user's primary group.)

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

Configuration
=============

Sensible defaults are provided that should work for most typical
installations of Trac and Gitolite. The following trac.ini options
(all in a `[trac-gitolite]` section) can be modified if necessary:

* admin_reponame: defaults to gitolite-admin; this is the name *in
  trac* of the gitolite-admin repository
* admin_real_reponame: defaults to gitolite-admin; this is the name
  *in gitolite* of the gitolite-admin repository
* admin_ssh_path: defaults to git@localhost:gitolite-admin.git
* admin_system_user: defaults to "trac"; this is the name *in
  gitolite* of the system user running the trac web process

* default_private: defaults to True; when set to True (the default)
  repositories known to Trac which are missing from gitolite.conf 
  will not be visible through the Trac source browser to any users.
  Set this to False to defer those repositories' permissions to the
  rest of the Trac permission system.
* all_includes_anonymous: defaults to False; when set to True,
  repositories with `@all = R` in `gitolite.conf` will be viewable
  through the web by anonymous users. The default is to make these
  repositories viewable by all logged-in users only.

Known Deficiencies
==================

Patches are welcome for any of these known deficiencies:

* Only the most basic Gitolite configuration is supported; any of the
  following advanced gitolite features will cause the plugin to fail:

  * refexes are unsupported: they cannot be configured through
    the Trac admin UI, and they are not respected by the Trac
    Browser permission policy.
  * deny rules are unsupported
  * user groups (aside from `@all`) are unsupported
  * project groups are unsupported
  * conf includes are unsupported
  * permissions other than R, W, + are unsupported: C, D, M
* Probably there are other unsupported advanced Gitolite features that
  I don't even know about -- feel free to tell me about them
* The process of creating a new repo is a bit confusing (first create
  it in Gitolite Repositories, then add it in Repositories)
* The permission-management UI is overwhelming
* All users are assumed to have the same usernames in Trac as their
  gitolite names.
* All repositories are assumed to have the same names in Trac as they
  do in gitolite.
* The behavior of Trac repository aliases have not been tested at all
* I think TRAC_ADMIN is not respected (TRAC_ADMIN users should have
  access to all repositories regardless of the gitolite.conf
  permissions, unless a configuration option says otherwise)
* Comments in the gitolite conf file will be overwritten when saving
  changes through Trac; in general, the gitolite conf file's
  particular contents, ordering and formatting will not be preserved
  reliably through Trac writes.
* The whole approach -- of having Trac clone, edit, commit and push
  the gitolite-admin repository during the user's web request with
  subprocesses -- is a pretty terrible hack, but I don't know if
  there's any possible alternative.  (I don't think Gitolite has an
  API.)  Using dulwich instead of `subprocess.call(['git', 'clone'])`
  etc would reduce the hackishness I guess.
