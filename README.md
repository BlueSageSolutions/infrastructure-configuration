# Infrastructure Configuration

This repo is used to configure our client applications and tooling. 

## Structure

We use ansible playbooks to update our application configurations on remote hosts. 

- `setup.yml` file in the root directory outlines the steps ansible will perform 
- `roles` directory defines tasks that are to be called within the `setup.yml`. 
- `inventory/*` directories define host servers that ansible will interact with and are generated by python scripts.
- `templates` directory contains template files that are used by ansible and custom python scripts to generate configuration files.
- `src` directory contains python modules that are used by our custom scripts

## Setup 

This project uses [poetry](https://python-poetry.org/docs/) as a python package manager.

### Poetry setup

These steps are largely taken from [poetry documentation](https://python-poetry.org/docs/managing-environments/):

Set python version for virtual environment:
```
poetry env use 3.11
```

Install dependencies
```
poetry install 
```

Enter virtual environment
```
eval $(poetry env activate)
```

Exit virtual environment
```
deactivate
```

## Running 

### Template inventory file

invoke task assumes you already have already authenticated with aws. It will assume the roles associated with the aws-profile names you pass in. See the doc strings defined in the [tasks.py](tasks.py) file for more information about the parameters to be passed in

Ensure you are in a virtual environment before running the following command:

```
inv inventory-template --envs <env> --client-code <client-code> --client-account-aws-profile <profile-name>
```

### Run ansible playbook
Ensure you are in a virtual environment before running the following command:

```
ansible-playbook -i inventory/<path to host file> setup.yml -u ubuntu
```

You can also run specifc parts of a playbook by passing in a tag. Below is an example if you wanted to just install newrelic java agents:
```
ansible-playbook --tags newrelic -i inventory/lower/01-move.yml setup.yml -u ubuntu
```

#### New Relic
New relic account, and client read only group must be created using the bootstrap playbook:
```
ansible-playbook playbooks/newrelic/bootstrap_new_relic_account.yml -e "client_code=<client code>"
```
This will also add the account to the `ClientAccountManagement` group which allows for the new relic service user to create resources via the new_relic terraform module

Bss groups are created and managed by the reconcile bss user groups playbook:
```
ansible-playbook playbooks/newrelic/reconcile_bss_user_groups.yml
```

This adds all bss full platform users to the `ClientAccountManagement` group, and all bss basic users to the `ClientAccountReadonly` group

## Refactor/Notes

- ansible playbook should read secrets and credentials from aws store at runtime so passwords are not stored in host yaml files on machines. For example, instead of reading db_pwd and writing to .yml file, the ansible playbook should read that password from aws ssm at runtime