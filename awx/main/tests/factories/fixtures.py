import json

from django.contrib.auth.models import User

from awx.main.models import (
    Organization,
    Project,
    Team,
    Instance,
    JobTemplate,
    Job,
    NotificationTemplate,
    Credential,
    Inventory,
    Label,
    WorkflowJobTemplate,
    WorkflowJob,
    WorkflowJobNode,
    WorkflowJobTemplateNode,
)

# mk methods should create only a single object of a single type.
# they should also have the option of being persisted or not.
# if the object must be persisted an error should be raised when
# persisted=False
#

def mk_instance(persisted=True):
    if not persisted:
        raise RuntimeError('creating an Instance requires persisted=True')
    from django.conf import settings
    return Instance.objects.get_or_create(uuid=settings.SYSTEM_UUID, hostname="instance.example.org")


def mk_organization(name, description=None, persisted=True):
    description = description or '{}-description'.format(name)
    org = Organization(name=name, description=description)
    if persisted:
        mk_instance(persisted)
        org.save()
    return org


def mk_label(name, organization=None, description=None, persisted=True):
    description = description or '{}-description'.format(name)
    label = Label(name=name, description=description)
    if organization is not None:
        label.organization = organization
    if persisted:
        label.save()
    return label


def mk_team(name, organization=None, persisted=True):
    team = Team(name=name)
    if organization is not None:
        team.organization = organization
    if persisted:
        mk_instance(persisted)
        team.save()
    return team


def mk_user(name, is_superuser=False, organization=None, team=None, persisted=True):
    user = User(username=name, is_superuser=is_superuser)
    if persisted:
        user.save()
        if organization is not None:
            organization.member_role.members.add(user)
        if team is not None:
            team.member_role.members.add(user)
    return user


def mk_project(name, organization=None, description=None, persisted=True):
    description = description or '{}-description'.format(name)
    project = Project(name=name, description=description)
    if organization is not None:
        project.organization = organization
    if persisted:
        project.save()
    return project


def mk_credential(name, cloud=False, kind='ssh', persisted=True):
    cred = Credential(name=name, cloud=cloud, kind=kind)
    if persisted:
        cred.save()
    return cred


def mk_notification_template(name, notification_type='webhook', configuration=None, organization=None, persisted=True):
    nt = NotificationTemplate(name=name)
    nt.notification_type = notification_type
    nt.notification_configuration = configuration or dict(url="http://localhost", headers={"Test": "Header"})

    if organization is not None:
        nt.organization = organization
    if persisted:
        nt.save()
    return nt


def mk_inventory(name, organization=None, persisted=True):
    inv = Inventory(name=name)
    if organization is not None:
        inv.organization = organization
    if persisted:
        inv.save()
    return inv


def mk_job(job_type='run', status='new', job_template=None, inventory=None,
           credential=None, project=None, extra_vars={},
           persisted=True):
    job = Job(job_type=job_type, status=status, extra_vars=json.dumps(extra_vars))

    job.job_template = job_template
    job.inventory = inventory
    job.credential = credential
    job.project = project

    if persisted:
        job.save()
    return job


def mk_job_template(name, job_type='run',
                    organization=None, inventory=None,
                    credential=None, network_credential=None,
                    cloud_credential=None, persisted=True, extra_vars='',
                    project=None, spec=None):
    if extra_vars:
        extra_vars = json.dumps(extra_vars)

    jt = JobTemplate(name=name, job_type=job_type, extra_vars=extra_vars,
                     playbook='mocked')

    jt.inventory = inventory
    if jt.inventory is None:
        jt.ask_inventory_on_launch = True

    jt.credential = credential
    if jt.credential is None:
        jt.ask_credential_on_launch = True

    jt.network_credential = network_credential
    jt.cloud_credential = cloud_credential

    jt.project = project

    jt.survey_spec = spec
    if jt.survey_spec is not None:
        jt.survey_enabled = True

    if persisted:
        jt.save()
    return jt

def mk_workflow_job(status='new', workflow_job_template=None, extra_vars={},
                    persisted=True):
    job = WorkflowJob(status=status, extra_vars=json.dumps(extra_vars))

    job.workflow_job_template = workflow_job_template

    if persisted:
        job.save()
    return job

def mk_workflow_job_template(name, extra_vars='', spec=None, persisted=True):
    if extra_vars:
        extra_vars = json.dumps(extra_vars)

    wfjt = WorkflowJobTemplate(name=name, extra_vars=extra_vars)

    wfjt.survey_spec = spec
    if wfjt.survey_spec is not None:
        wfjt.survey_enabled = True

    if persisted:
        wfjt.save()
    return wfjt

def mk_workflow_job_template_node(workflow_job_template=None,
                                  unified_job_template=None, 
                                  success_nodes=None,
                                  failure_nodes=None,
                                  always_nodes=None,
                                  persisted=True):
    workflow_node = WorkflowJobTemplateNode(workflow_job_template=workflow_job_template,
                                            unified_job_template=unified_job_template,
                                            success_nodes=success_nodes,
                                            failure_nodes=failure_nodes,
                                            always_nodes=always_nodes)
    if persisted:
        workflow_node.save()
    return workflow_node

def mk_workflow_job_node(unified_job_template=None, 
                         success_nodes=None,
                         failure_nodes=None,
                         always_nodes=None,
                         workflow_job=None, 
                         job=None,
                         persisted=True):
    workflow_node = WorkflowJobNode(unified_job_template=unified_job_template,
                                    success_nodes=success_nodes,
                                    failure_nodes=failure_nodes,
                                    always_nodes=always_nodes,
                                    workflow_job=workflow_job,
                                    job=job)
    if persisted:
        workflow_node.save()
    return workflow_node
