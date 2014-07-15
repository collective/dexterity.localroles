import unittest2 as unittest

import robotsuite
from dexterity.localroles.testing import DLR_ROBOT_TESTING
from plone.testing import layered


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(robotsuite.RobotTestSuite('settings.robot'),
                layer=DLR_ROBOT_TESTING),
    ])
    return suite
