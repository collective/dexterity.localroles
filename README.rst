.. contents::

Introduction
============

Allow to define local roles settings by dexterity type.

A new configuration page is added as a new tab on a dexterity type configuration.

You can now define for each state which principal will receive some local roles automatically.

By example:

* on the "pending" state, the "stephen" user will receive the following role: Reviewer.
* on the "published" state, the 'editors' group will receive the following roles: Editor, Reviewer.

Those automaticaly given roles cannot be removed by the "sharing" tab (read only, as inherited roles).

Installation
============

* Add dexterity.localroles to your eggs.
* Re-run buildout.
* Done.

Credits
=======

Have an idea? Found a bug? Let us know by `opening a ticket`_.

.. _`opening a ticket`: https://github.com/IMIO/dexterity.localroles/issues


Tests
=====

This package is tested using Travis CI. The current status of the add-on is :

.. image:: https://api.travis-ci.org/IMIO/dexterity.localroles.png
    :target: https://travis-ci.org/IMIO/dexterity.localroles
