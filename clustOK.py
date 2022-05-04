import subprocess
import fire
import yaml
import time

from yaml.loader import SafeLoader

global tests
global interval

def checkSlurm():
  try:
    subprocess.call('sinfo') != 0
  except:
    print('Could not execute slurm-command. Please make sure slurm is installed and the user executing this script has enough permissions')
    exit(1)

def readConfig(config="clustOK.yml"):
  with open(config) as f:
    data = yaml.load(f, Loader=SafeLoader)

    global tests
    global interval

    tests = data['tests']
    interval = data['interval']

def executeTests(tests):
  print('Executing Tests...')
  print(tests)

  for test in tests: 
      if 'script' in test:
        print('Executing script-test: %s' % test['name'])

        result = executeSingleBash(test['script'])

        if (result.returncode == 0):
          print('Success!')
        else:
          print('Failed with errorCode: ', result.returncode)


def executeSingleBash(test):
  result = subprocess.run([test['path']], stdout=subprocess.PIPE)
  #  print(result.stdout.decode('utf-8'))
  return result

def main(config="clustOK.yml"):
  checkSlurm()
  readConfig(config)

  while True:
    executeTests(tests)
    time.sleep(interval)

if __name__ == '__main__':
    fire.Fire(main)