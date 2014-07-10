# encoding: utf-8

from Products.CMFPlone.utils import base_hasattr
from collective.z3cform.datagridfield import DataGridField
from collective.z3cform.datagridfield import DictRow
from copy import deepcopy
from five import grok
from plone import api
from plone.app.dexterity.interfaces import ITypeSchemaContext
from z3c.form import field
from z3c.form import form
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.interfaces import IValidator
from z3c.form.validator import SimpleFieldValidator
from z3c.form.widget import FieldWidget
from zope import schema
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import Interface

from dexterity.localroles import _
from dexterity.localroles import PMF
from dexterity.localroles.browser.exceptions import DuplicateEntryError
from dexterity.localroles.browser.exceptions import UnknownPrincipalError
from dexterity.localroles.browser.interfaces import IPrincipal
from dexterity.localroles.browser.interfaces import IRole
from dexterity.localroles.browser.interfaces import IWorkflowState
from dexterity.localroles.browser.interfaces import ILocalRoleList
from dexterity.localroles.browser.overrides import CustomTypeFormLayout
from dexterity.localroles.browser.vocabulary import plone_role_generator


class WorkflowState(schema.Choice):
    grok.implements(IWorkflowState)

    def __init__(self, *args, **kwargs):
        kwargs['vocabulary'] = u''
        super(WorkflowState, self).__init__(*args, **kwargs)

    def bind(self, object):
        return super(schema.Choice, self).bind(object)


class Role(schema.List):
    grok.implements(IRole)


class Principal(schema.TextLine):
    grok.implements(IPrincipal)


class RoleFieldValidator(grok.MultiAdapter, SimpleFieldValidator):
    grok.provides(IValidator)
    grok.adapts(
        Interface,
        Interface,
        Interface,
        IPrincipal,
        Interface)

    def validate(self, value, force=False):
        if value is not None and force is True:
            if api.user.get(username=value) is None and \
               api.group.get(groupname=value) is None:
                raise UnknownPrincipalError


@grok.adapter(IRole, IFormLayer)
@grok.implementer(IFieldWidget)
def role_widget(field, request):
    return FieldWidget(field, CheckBoxWidget(request))


class LocalRoleList(schema.List):
    grok.implements(ILocalRoleList)


class LocalRoleListValidator(grok.MultiAdapter, SimpleFieldValidator):
    grok.provides(IValidator)
    grok.adapts(
        Interface,
        Interface,
        Interface,
        ILocalRoleList,
        Interface)

    def validate(self, value, force=False):
        for subform in [widget.subform for widget in self.widget.widgets]:
            for widget in subform.widgets.values():
                if hasattr(widget, 'error') and widget.error:
                    raise ValueError(widget.label)
        if value is not None:
            vset = set([(s, v) for s, r, v in [l.values() for l in value]])
            if len(vset) < len(value):
                raise DuplicateEntryError


@grok.adapter(ILocalRoleList, IFormLayer)
@grok.implementer(IFieldWidget)
def localrolelist_widget(field, request):
    return FieldWidget(field, DataGridField(request))


class ILocalRole(Interface):
    state = WorkflowState(title=_(u'state'), required=True)

    value = Principal(title=_(u'value'))

    roles = Role(title=_(u'roles'),
                 value_type=schema.Choice(source=plone_role_generator),
                 required=True)


class LocalRoleConfigurationAdapter(object):
    adapts(ITypeSchemaContext)

    def __init__(self, context):
        self.__dict__['context'] = context
        self.__dict__['fti'] = self.context.fti

    def __getattr__(self, name):
        if not base_hasattr(self.context.fti, name) \
           or not isinstance(getattr(self.context.fti, name), dict):
            raise AttributeError
        value = getattr(self.context.fti, name)
        return self.convert_to_list(value)

    def __setattr__(self, name, value):
        old_value = getattr(self.context.fti, name, {})
        new_dict = self.convert_to_dict(value)
        if old_value == new_dict:
            return
        setattr(self.context.fti, name, new_dict)

    @staticmethod
    def convert_to_dict(value):
        value_dict = {}
        for row in value:
            state, roles, principal = row.values()
            if state not in value_dict:
                value_dict[state] = {'users': {}, 'groups': {}}
            if api.user.get(username=principal) is not None:
                value_dict[state]['users'][principal] = roles
            elif api.group.get(groupname=principal) is not None:
                value_dict[state]['groups'][principal] = roles
        return value_dict

    @staticmethod
    def convert_to_list(value):
        value_list = []
        for state_key, state in sorted(value.items()):
            for username, roles in sorted(state.get('users').items()):
                value_list.append({'state': state_key, 'roles': roles,
                                   'value': username})
            for groupname, roles in sorted(state.get('groups').items()):
                value_list.append({'state': state_key, 'roles': roles,
                                   'value': groupname})
        return value_list


class LocalRoleConfigurationForm(form.EditForm):
    template = ViewPageTemplateFile('templates/role-config.pt')
    label = _(u'Local Role configuration')
    successMessage = _(u'Local role configurations successfully updated.')
    noChangesMessage = _(u'No changes were made.')
    buttons = deepcopy(form.EditForm.buttons)
    buttons['apply'].title = PMF(u'Save')

    def update(self):
        super(LocalRoleConfigurationForm, self).update()

    def updateWidgets(self):
        super(LocalRoleConfigurationForm, self).updateWidgets()

    def getContent(self):
        return LocalRoleConfigurationAdapter(self.context)

    @property
    def fields(self):
        fields = [
            LocalRoleList(
                __name__='localroleconfig',
                title=_(u'Local role configuration'),
                description=u'',
                value_type=DictRow(title=u"fieldconfig", schema=ILocalRole))
        ]
        fields = sorted(fields, key=lambda x: x.title)
        fields = field.Fields(*fields)

        return fields


class LocalRoleConfigurationPage(CustomTypeFormLayout):
    form = LocalRoleConfigurationForm
    label = _(u'Local roles')
