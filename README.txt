This plugin provides four integrations with gitolite:

 1. Trac's repository permissions (BROWSER_VIEW, CHANGESET_VIEW) are inherited from the gitolite.conf file per repository and per user

 1. Add and remove users' read and write permissions from each repository through the Trac admin UI

 1. Management of users' SSH public keys through the Trac web UI, as an admin panel and as a per-user preferences panel

 1. A "Create New Repository" feature allows you to initialize an empty git repository through the Trac web UI if the user has sufficient permissions (REPOSITORY_CREATE)
