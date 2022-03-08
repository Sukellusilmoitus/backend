import unittest
import datetime
from models.target import Target


class TestTarget(unittest.TestCase):
    def setUp(self):
        targets = Target.objects.raw({
            'source': {'$eq': 'ilmoitus'}
        }).all()
        for target in targets:
            target.delete()

    def test_target_can_be_created_with_right_parameters(self):
        Target.create(target_id='9999999999991',
                      name='Testihylky',
                      town='SaimaaTesti',
                      type='Hylky',
                      x_coordinate=25.0,
                      y_coordinate=61.0,
                      location_method='gpstesti',
                      location_accuracy='huonotesti',
                      url='https://testiurl.com',
                      created_at=datetime.datetime.now(),
                      is_ancient=False,
                      source='ilmoitus',
                      is_pending=True)
        self.assertGreater(Target.objects.raw({
            'source': {'$eq': 'ilmoitus'}
        }).all().count(), 0)

    def test_target_is_not_pending_after_accepting(self):
        target = Target(target_id='9999999999992',
                        name='Testihylky2',
                        town='SaimaaTesti',
                        type='Hylky',
                        x_coordinate=25.0,
                        y_coordinate=61.0,
                        location_method='gpstesti',
                        location_accuracy='huonotesti',
                        url='https://testiurl.com',
                        created_at=datetime.datetime.now(),
                        is_ancient=False,
                        source='ilmoitus',
                        is_pending=True)
        target.save()
        accepted_target = Target.accept('9999999999992')
        self.assertFalse(accepted_target.is_pending)

    def test_target_can_be_updated(self):
        target = Target(target_id='9999999999993',
                        name='Testihylky3',
                        town='SaimaaTesti',
                        type='Hylky',
                        x_coordinate=25.0,
                        y_coordinate=61.0,
                        location_method='gpstesti',
                        location_accuracy='huonotesti',
                        url='https://testiurl.com',
                        created_at=datetime.datetime.now(),
                        is_ancient=False,
                        source='ilmoitus',
                        is_pending=True)
        target.save()
        updated_target = Target.update(target_id='9999999999993',
                                       name='Testihylky3',
                                       town='SaimaaTesti',
                                       type='Hylky',
                                       x_coordinate=26.666666,
                                       y_coordinate=61.0,
                                       location_method='gpstesti',
                                       location_accuracy='huonotesti',
                                       url='https://oikeatestiurl.com',
                                       created_at=datetime.datetime.now(),
                                       is_ancient=False,
                                       source='ilmoitus',
                                       is_pending=True)
        self.assertEqual(updated_target.x_coordinate, 26.666666)
        self.assertEqual(updated_target.url, 'https://oikeatestiurl.com')
