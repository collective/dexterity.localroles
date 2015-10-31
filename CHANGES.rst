Changelog
=========

0.3 (unreleased)
----------------

- Use only local roles in vocabulary.
  [sgeulette]
- Store all configuration in one fti attribute 'localroles'.
  Useful for dexterity.localrolesfield to avoid a field name is an existing attribute
  [sgeulette]
- Add a related field to store a text configuration that will be used to set related objects local roles.
  [sgeulette]
- Simplify code
  [sgeulette]

0.2 (2015-06-02)
----------------

- Avoid exception on site deletion
  [sgeulette]


0.1 (2014-10-24)
----------------

- Various improvements
  [mpeeters, sgeulette]
- Added tests
  [sgeulette]
- Some improvements
  [sgeulette]
- Add validation on configuration view
  [mpeeters]
- Add localroles configuration view
  [mpeeters]
- Add an adapter for borg.localrole
  [mpeeters]
