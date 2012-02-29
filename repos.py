#!/usr/bin/env python
# coding=utf8

"""
Script for managing all my local git repositories.
"""

import sys, os, json, tempfile, subprocess
import ConfigParser
import optfunc

DEFAULT_CONFIG_FILE = os.path.expanduser("~/.repos.json")
DEFAULT_BASE_DIR = os.path.expanduser("~/")

def run(args, cwd=None):
  try:
    output = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=cwd).communicate()[0]
  except OSError, e:
    print args
    raise e 
  return output

class Project(object):
  def __init__(self, local, remote, basedir):
    self.local, self.remote, self.basedir = local, remote, basedir
    
  def getDict(self):
    # This is not pretty.
    return {"local":self.local,"remote":self.remote,"provider":self.provider}
    
# I don't have any svn projects anymore, so whatevs
class SvnProject(Project):
  def __init__(self, *args, **kwargs):
    super(SvnProject, self).__init__(*args, **kwargs)
    self.provider = "svn"

  def update(self):
    pass
    
  def create(self):
    pass
    
  def status(self):
    pass
        
class GitProject(Project):
  def __init__(self, *args, **kwargs):
    super(GitProject, self).__init__(*args, **kwargs)
    self.provider = "git"

  def update(self):
    path = os.path.join(self.basedir, self.local)
    run(["git", "pull"], cwd=path)
    
  def create(self):
    path = os.path.abspath(os.path.join(self.basedir, os.path.normpath(self.local)))
    remote = os.path.expanduser(self.remote)
    print "Cloning", remote, "into", path
    print run(["git", "clone", "--no-hardlinks", remote, path])
  
  def status(self):
    print self.local, "status:"
    path = os.path.abspath(os.path.join(self.basedir, os.path.normpath(self.local)))
    print run(["git", "status"], cwd=path)

class Workspace(object):
  def __init__(self, basedir=DEFAULT_BASE_DIR, config=DEFAULT_CONFIG_FILE):
    self.projects = []
    self.basedir = basedir
    self.config = config
    
    if os.path.exists(self.config):
      f = open(self.config)
      conf = json.load(f)
      f.close()
    else:
      conf = {}

    if "projects" in conf:
      for project in conf["projects"]:
        provider = project["provider"]
        local = project["local"]
        remote = project["remote"]
        if provider == "git":
          self.projects.append(GitProject(local, remote, self.basedir))
        elif provider == "svn":
          self.projects.append(SvnProject(local, remote, self.basedir))
    self.sort()

  def save(self):
    configDict = { "projects": list(project.getDict() for project in self.projects) }
    f = None
    try:
      f = open(self.config, 'w')
      f.write(json.dumps(configDict, sort_keys=True, indent=2))
    finally:
      if f:
        f.close()

  def update(self):
    for project in self.projects:
      print "Updating", project.local
      project.update()

  def add(self, local):
    config = ConfigParser.ConfigParser()
    
    # hack to remove left hand whitespace so we can use ConfigParser to read the git .config, eww.
    f = open('%s/.git/config' % local)
    tmp = tempfile.TemporaryFile()
    for line in f:
      tmp.write(line.lstrip())
    f.close()
    tmp.seek(0)
    config.readfp(tmp)
    tmp.close()
    
    for section in config.sections():
      if "remote" in section:
        remote = config.get(section, "url")
        break
    local = os.path.normpath(os.path.relpath(local, self.basedir))
    name = os.path.split(local)[1]
    
    print local, remote
    project = GitProject(local, remote, self.basedir)
    for p in self.projects:
      if p.local == project.local:
        print p.__dict__
        raise Exception("This project already being tracked")
    self.projects.append(project)
    self.sort()
    
  def sort(self):
    self.projects.sort(key=lambda project: project.local)
    
  def drop(self, path):
    path = os.path.abspath(os.path.normpath(path))
    for project in self.projects:
      if os.path.abspath(os.path.normpath(project.local)) == path:
        print "Dropping project", project.local
        self.projects.remove(project)
        return
    print "No project with that path is being tracked"
    
  def create(self):
    for project in self.projects:
      projectPath = os.path.abspath(os.path.join(self.basedir, os.path.normpath(project.local)))
      if not os.path.exists(projectPath):
        print "Creating project ", project.local
        project.create()
        print "Project created"
    
  def status(self):
    for project in self.projects:
      project.status()

def update():
  workspace = Workspace()
  workspace.update()
  
def add(path):
  workspace = Workspace()
  workspace.add(path)
  workspace.save()

def drop(path):
  workspace = Workspace()
  workspace.drop(path)
  workspace.save()

def ls():
  workspace = Workspace()
  print "Projects:"
  for project in workspace.projects:
    print "\t", project.local

def status():
  workspace = Workspace()
  workspace.status()
  
# create local repos which do not exist yet.
def create():
  workspace = Workspace()
  workspace.create()

if __name__ == '__main__':
  optfunc.run([update, add, create, drop, ls, status])
