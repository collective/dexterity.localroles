# encoding: utf-8

from collective.z3cform.datagridfield.row import DictRow
from copy import deepcopy
from dexterity.localroles import _
from dexterity.localroles import PMF
from dexterity.localroles.browser.exceptions import DuplicateEntryError
from dexterity.localroles.browser.exceptions import RelatedFormatError
from dexterity.localroles.browser.exceptions import RoleNameError
from dexterity.localroles.browser.exceptions import UnknownPrincipalError
from dexterity.localroles.browser.exceptions import UtilityNameError
from dexterity.localroles.browser.interfaces import ILocalRoleList
from dexterity.localroles.browser.interfaces import ILocalRoleListUpdatedEvent
from dexterity.localroles.browser.interfaces import IPrincipal
from dexterity.localroles.browser.interfaces import IRole
from dexterity.localroles.browser.interfaces import IWorkflowState
from dexterity.localroles.browser.overrides import CustomTypeFormLayout
from dexterity.localroles.interfaces import ILocalRolesRelatedSearchUtility
from persistent.mapping import PersistentMapping
from plone import api
from plone.app.dexterity.interfaces import ITypeSchemaContext
from plone.app.workflow.interfaces import ISharingPageRole
from Products.CMFPlone.utils import base_hasattr
from z3c.form import field
from z3c.form import form
from z3c.form import validator
from z3c.form.browser.checkbox import CheckBoxWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.validator import SimpleFieldValidator
from z3c.form.widget import FieldWidget
from zope import event
from zope import schema
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import adapts
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface


try:
    from collective.z3cform.datagridfield.datagridfield import DataGridField as DataGridFieldWidget
except ImportError:
    from collective.z3cform.datagridfield.datagridfield import DataGridFieldWidget


@implementer(IWorkflowState)
class WorkflowState(schema.Choice):

    def __init__(self, *args, **kwargs):
        kwargs['vocabulary'] = u''
        super(WorkflowState, self).__init__(*args, **kwargs)

    def bind(self, object):
        return super(schema.Choice, self).bind(object)


@implementer(IRole)
class Role(schema.List):
    """Role"""


@implementer(IPrincipal)
class Principal(schema.TextLine):
    """Principal"""


class RoleFieldValidator(SimpleFieldValidator):

    def validate(self, value, force=False):
        if value is not None and force is True:
            if api.user.get(username=value) is None and \
               api.group.get(groupname=value) is None:
                raise UnknownPrincipalError


@implementer(IFieldWidget)
def role_widget(field, request):
    return FieldWidget(field, CheckBoxWidget(request))


@implementer(ILocalRoleList)
class LocalRoleList(schema.List):
    """LocalRole list"""


@implementer(ILocalRoleListUpdatedEvent)
class LocalRoleListUpdatedEvent(object):

    def __init__(self, fti, field, old_value, new_value):
        self.fti = fti
        self.field = field
        self.old_value = old_value
        self.new_value = new_value


class LocalRoleListValidator(SimpleFieldValidator):

    def validate(self, value, force=False):
        for dgfo_widget in self.widget.widgets:
            if dgfo_widget.id.endswith("AA") or dgfo_widget.id.endswith("TT"):
                continue
            if base_hasattr(dgfo_widget, 'subform'):
                dgfo_widget = dgfo_widget.subform
            for widget in dgfo_widget.widgets.values():
                if hasattr(widget, 'error') and widget.error:
                    raise ValueError(widget.label)
        if value is not None:
            vset = set([(item['state'], item['value']) for item in value])
            if len(vset) < len(value):
                raise DuplicateEntryError


@implementer(IFieldWidget)
def localrolelist_widget(field, request):
    return FieldWidget(field, DataGridFieldWidget(request))


class RelatedFormatValidator(validator.SimpleFieldValidator):
    def validate(self, value, force=False):
        # we call the already defined validators
        # super(RelatedFormatValidator, self).validate(value)
        if not value or not value.strip():
            return
        try:
            var = eval(value)
        except Exception:
            raise RelatedFormatError
        if not isinstance(var, dict):
            raise RelatedFormatError
        valid_roles = [i[0] for i in getUtilitiesFor(ISharingPageRole)]
        for utility in var:
            try:
                getUtility(ILocalRolesRelatedSearchUtility, utility)
            except Exception:
                raise UtilityNameError
            if not isinstance(var[utility], (list, tuple)):
                raise RelatedFormatError
            for role in var[utility]:
                if role not in valid_roles:
                    raise RoleNameError


class ILocalRole(Interface):
    state = WorkflowState(title=_(u'state'), required=True)

    value = Principal(title=_(u'value'))

    roles = Role(title=_(u'roles'),
                 value_type=schema.Choice(vocabulary='dexterity.localroles.vocabulary.SharingRolesVocabulary'),
                 required=True)

    related = schema.Text(title=_(u'related role configuration'),
                          required=False)


validator.WidgetValidatorDiscriminators(RelatedFormatValidator, field=ILocalRole['related'])


class LocalRoleConfigurationAdapter(object):
    adapts(ITypeSchemaContext)

    def __init__(self, context):
        self.__dict__['context'] = context
        self.__dict__['fti'] = self.context.fti

    def __getattr__(self, name):
        if not base_hasattr(self.context.fti, 'localroles') \
                or name not in self.context.fti.localroles \
                or not isinstance(self.context.fti.localroles[name], dict):
            raise AttributeError
        value = self.context.fti.localroles[name]
        return self.convert_to_list(value)

    def __setattr__(self, name, value):
        if not base_hasattr(self.context.fti, 'localroles'):
            setattr(self.context.fti, 'localroles', PersistentMapping())
        old_value = self.context.fti.localroles.get(name, {})
        # for plone 6 with state as tuple
        for dic in value:
            if isinstance(dic['state'], tuple):
                dic['state'] = dic['state'][0]
        new_dict = self.convert_to_dict(value)
        if old_value == new_dict:
            return
        self.context.fti.localroles[name] = new_dict
        event.notify(LocalRoleListUpdatedEvent(self.fti, name, old_value, new_dict))

    @staticmethod
    def convert_to_dict(value):
        value_dict = {}
        for row in value:
            state, roles, principal = row['state'], row['roles'], row['value']
            related = row['related'] is not None and row['related'].strip() and str(eval(row['related'])) or ''
            if state not in value_dict:
                value_dict[state] = {}
            value_dict[state][principal] = {'roles': roles, 'rel': related}
        return value_dict

    @staticmethod
    def convert_to_list(value):
        value_list = []
        for state_key, state_dic in sorted(value.items()):
            for principal, roles_dic in sorted(state_dic.items()):
                value_list.append({'state': state_key, 'roles': roles_dic['roles'],
                                   'value': principal, 'related': roles_dic.get('rel', '')})
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
                __name__='static_config',
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
