.. contents::

Introduction
============

Allow to define local roles settings by dexterity type.

A new configuration page is added as a new tab on a dexterity type configuration.

You can now define for each state which principal will receive some local roles automatically.

By example:

* on the "pending" state, the "stephen" user will receive the following role: Reviewer.
* on the "published" state, the 'editors' group will receive the following roles: Editor, Reviewer.

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
