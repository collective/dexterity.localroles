# encoding: utf-8

from Products.CMFPlone.utils import base_hasattr
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from copy import deepcopy
from five import grok
from plone import api
from plone.app.dexterity.browser.layout import TypeFormLayout
from plone.app.dexterity.interfaces import ITypeSchemaContext
from z3c.form import field
from z3c.form import form
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import IFormLayer
from z3c.form.widget import FieldWidget
from zope import schema
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.interface import Interface

from dexterity.localroles import _
from dexterity.localroles import PMF
from dexterity.localroles.browser.interfaces import IStateField
from dexterity.localroles.browser.interfaces import IRoleField
from dexterity.localroles.browser.vocabulary import plone_role_generator


class StateField(schema.Choice):
    grok.implements(IStateField)

    def __init__(self, *args, **kwargs):
        kwargs['vocabulary'] = u''
        super(StateField, self).__init__(*args, **kwargs)

    def bind(self, object):
        return super(schema.Choice, self).bind(object)


class RoleField(schema.List):
    grok.implements(IRoleField)


@grok.adapter(IRoleField, IFormLayer)
@grok.implementer(IFieldWidget)
def role_widget(field, request):
    return FieldWidget(field, CheckBoxWidget(request))


class IFieldRole(Interface):
    state = StateField(title=_(u'state'), required=True)

    value = schema.TextLine(title=_(u'value'))

    roles = RoleField(title=_(u'roles'),
                      value_type=schema.Choice(source=plone_role_generator),
                      required=True)


class RoleFieldConfigurationAdapter(object):
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


class RoleFieldConfigurationForm(form.EditForm):
    template = ViewPageTemplateFile('templates/role-config.pt')
    label = _(u'Role field configuration')
    successMessage = _(u'Role fields configurations successfully updated.')
    noChangesMessage = _(u'No changes were made.')
    buttons = deepcopy(form.EditForm.buttons)
    buttons['apply'].title = PMF(u'Save')

    def update(self):
        super(RoleFieldConfigurationForm, self).update()

    def updateWidgets(self):
        super(RoleFieldConfigurationForm, self).updateWidgets()

    def getContent(self):
        return RoleFieldConfigurationAdapter(self.context)

    @property
    def fields(self):
        fields = [
            schema.List(
                __name__='localroleconfig',
                title=_(u'Local role configuration'),
                description=u'',
                value_type=DictRow(title=u"fieldconfig", schema=IFieldRole))
        ]
        fields = sorted(fields, key=lambda x: x.title)
        fields = field.Fields(*fields)

        for f in fields.values():
            f.widgetFactory = DataGridFieldFactory
        return fields


class RoleConfigurationPage(TypeFormLayout):
    form = RoleFieldConfigurationForm
    label = _(u'Role field configuration')
