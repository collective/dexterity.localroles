.. contents::

Introduction
============

Allow to define local roles settings by dexterity type.

A new configuration page is added as a new tab on a dexterity type configuration.

A configuration line has the following fields:

* the state
* the principal
* the roles
* an optional configuration as string, but evaluated as a dict: {'utility name': [roles]}. The utility implements
  ILocalRolesRelatedSearchUtility and get related objects.

You can then define for each state which principal will receive some local roles automatically on the content,
and other local roles on related content.

By example:

* on the "pending" state, the "stephen" user will receive the following role: Reviewer.
* on the "published" state, the "editors" group will receive the following roles: Editor, Reviewer.

The utility "dexterity.localroles.related_parent" get the object parent and can be used to give local roles on the content parent.

* on the "pending" state, the "stephen" user will receive on the content parent the role: Reviewer.

Those automaticaly given roles cannot be manually removed by the "sharing" tab (read only, as inherited roles).

This package is a base for dexterity.localrolesfield that adds a field to define the principal.

Installation
============

* Add dexterity.localroles to your eggs.
* Re-run buildout.
* Done.

Credits
=======

Have an idea? Found a bug? Let us know by `opening a ticket`_.

.. _`opening a ticket`: https://github.com/collective/dexterity.localroles/issues


Tests
=====

This package is tested using Travis CI. The current status of the add-on is :

.. image:: https://api.travis-ci.org/collective/dexterity.localroles.png
    :target: https://travis-ci.org/collective/dexterity.localroles
.. image:: https://coveralls.io/repos/collective/dexterity.localroles/badge.svg?branch=master&service=github
  :target: https://coveralls.io/github/collective/dexterity.localroles?branch=master
