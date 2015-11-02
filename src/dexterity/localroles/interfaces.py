# encoding: utf-8

from zope.interface import Interface


class IDexterityLocalRoles(Interface):
    """ Specific layer for the package """


class ILocalRolesRelatedSearchUtility(Interface):
    """ Interface for related local roles business """

    def get_objects(context):
        """ Get related objects.

        :param context: original type instance for which a related configuration is defined
        :type context: type instance object

        :returns: a list of objects
        :rtype: list
        """
