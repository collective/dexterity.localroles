from dexterity.localroles.testing import DLR_ROBOT_TESTING
from plone.testing import layered

import robotsuite
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(
        [
            layered(robotsuite.RobotTestSuite("settings.robot"), layer=DLR_ROBOT_TESTING),
        ]
    )
    return suite
