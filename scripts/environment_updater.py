#!/usr/bin/env spack-python
"""
This script will cycle over a list of environments
and update them.  These environments should control
the views that modules use.
"""
import spack.environment as ev
import spack.util.executable
from datetime import date
import os
import sys

sys.path.append(os.path.join(os.environ['SPACK_MANAGER'],'scripts'))
import set_permissions

git = spack.util.executable.which('git')

def GetValidEnvironment(env):
    try:
       # check for registerd env
       return ev.read(env)
    except:
       try:
          # check for anonymous env
          ev.Environment(env)
       except:
          raise ev.SpackEnvironmentErrror('%s is not a valid environment' % env)
       finally:
          return ev.Environment(env)
    return None


def GetListOfEnvironments(iFile):
    envs = []
    fp = open(iFile)
    for line in fp:
        print(line)
        try:
            name, frequency = line.split()
        except:
            print('Failing line: ', line)
        envs.append({'name' : name,'freq' : frequency})
    return envs

def TimeToUpdate(f):
    """
    Check if the environment should be built
    based off the specified frequency and current
    date
    """
    today = date.today()

    if f == 'monthly' and today.day == 1:
        return True
    if f == 'daily':
        return True
    if f == 'quarterly' and today.day == 1 and today.month in [1,4,7,10]:
        return True

    return False

def UpdateDevelopmentSpecs(e):
    env = GetValidEnvironment(e)
    with env:
        for name, entry in env.dev_specs.items():
            os.chdir(os.path.join(env.path, entry['path']))
            print('Updating develop spec for: %s' % name)
            try:
                git('fetch', '--unshallow', error=os.devnull)
            except:
                pass
            git('pull')
            git('submodule', 'update')

def UpdateEnvironment(e):
    env = GetValidEnvironment(e)
    with env:
        env.install_all()

def UpdatePermissionsForEnvironment(env, group):
    print("Updaing Permissions")
    #set_permissions.set_dir_permissions(
    #    os.path.join(os.environ['SPACK_MANAGER'],'modules'),0o755, group)
    #set_permissions.set_dir_permissions(
    #    os.path.join(os.environ['SPACK_MANAGER'],'views'),0o755, group)
    #set_permissions.set_dir_permissions(
    #    os.path.join(os.environ['SPACK_MANAGER'],'spack','opt'),0o755, group)

def UpdateListOfEnvironments(inputFile, group):
    envs = GetListOfEnvironments(inputFile)
    for e in envs:
        if TimeToUpdate(e['freq']):
            print("Updating environment: {f}".format(f=e['name']))
            try:
                UpdateDevelopmentSpecs(e['name'])
                UpdateEnvironment(e['name'])
            except:
                pass
            finally:
                print('Finished with environment: {f}'.format(f=e['name']))
    UpdatePermissionsForEnvironment(None, group)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description = 'Cycle environments and update them')
    parser.add_argument('-i', '--input_file', required = False, help = 'File with list of environments to update')
    parser.add_argument('-e', '--environment', required = False, help = 'Single environment to update without checking frequency')
    parser.add_argument('-u', '--update_spack_manager', action='store_true', help = 'Update spack-manager before updating environments')
    parser.add_argument('-g', '--group', required = False, help = 'Group to use when setting permissions')
    parser.add_argument('-j', '--jobs', required = False, help = 'Number of cores to forward to spack')
    parser.set_defaults(update_spack_manager=False, group='wg-sierra-users')
    args = parser.parse_args()

    if args.update_spack_manager:
        os.chdir(os.environ['SPACK_MANAGER'])
        git('pull')
        git('submodule', 'update')

    if args.input_file is not None:
        UpdateListOfEnvironments(args.input_file, args.group)

    if args.environment is not None:
        env = args.environment
        UpdateDevelopmentSpecs(env)
        UpdateEnvironment(env)
        UpdatePermissionsForEnvironment(env, args.group)

