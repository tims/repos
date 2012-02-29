Repos
=====

repos.py is a python script for managing my local git repositories.

Config is stored in ~/.repos.json
Which looks something like this::

  {
    "projects": [
      {
        "local": "workspace/repos", 
        "provider": "git", 
        "remote": "git@github.com:tims/repos.git"
      }
    ]
  }

Update all repositories
-----------------------

This just does a git pull on every git repo::

  repos.py update

List managed repositories
-------------------------

List all the repositories being managed::

  repos.py ls

Add a repository
----------------

Just clone it to some dir then change to that directory and::

  repos.py add .
  
Drop a repository
-----------------

To remove a repository from the repos config, change to it's directory and::

  repos.py drop .

The repository is not deleted from disk.

Create missing repositories
---------------------------

Create repositories that are in your .repos.json but not yet cloned locally::

  repos.py create
  
Get status
----------

Run git status on each repo::

  repos.py status
  
