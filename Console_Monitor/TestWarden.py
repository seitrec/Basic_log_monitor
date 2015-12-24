import unittest
from Warden import AlertWarden


class TestAlertWarden(unittest.TestCase):
    def test_update(self):
        alert_warden = AlertWarden(2)
        now = 1450983778
        readable_now = "2015-12-24 20:02:58"
        self.assertTupleEqual(alert_warden.update(0, now), (2, ()))
        self.assertTupleEqual(alert_warden.update(60, now), (2, ()))
        self.assertTupleEqual(alert_warden.update(239, now), (2, ()))
        self.assertTupleEqual(alert_warden.update(240, now), (1, (readable_now, 240, 240)))
        now += 20
        readable_now = "2015-12-24 20:03:18"
        self.assertTupleEqual(alert_warden.update(200, now), (0, ("0: 0:20", 240, 240)))
        self.assertTupleEqual(alert_warden.update(400, now), (1, (readable_now, 400, 240)))
        self.assertTupleEqual(alert_warden.update(450, now), (2, ()))
        now += 130
        self.assertTupleEqual(alert_warden.update(200, now), (0, ("0: 2:10", 450, 240)))

    def test_status(self):
        alert_warden = AlertWarden(2)
        now = 1450983778
        alert_warden.update(60, now)
        self.assertEqual(alert_warden.status(), 0)
        alert_warden.update(230, now)
        self.assertEqual(alert_warden.status(), 1)
        alert_warden.update(300, now)
        self.assertEqual(alert_warden.status(), 2)
        alert_warden.update(100, now)
        self.assertEqual(alert_warden.status(), 0)
        alert_warden.update(215, now)
        self.assertEqual(alert_warden.status(), 0)
        alert_warden.update(216, now)
        self.assertEqual(alert_warden.status(), 1)

if __name__ == '__main__':
    unittest.main()
