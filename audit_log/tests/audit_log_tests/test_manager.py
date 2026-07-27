from django.contrib.auth import get_user_model
from django.test import TestCase
from django.db import models
from .models import (Product, WarehouseEntry, ProductCategory, ExtremeWidget,
                        SaleInvoice, Employee, ProductRating, Property, PropertyOwner)


class DisablingTrackingTest(TestCase):


    def test_disable_enable_instance(self):
        ProductCategory.objects.create(name = 'test category', description = 'test')
        ProductCategory.objects.create(name = 'test category2', description = 'test')
        c1 = ProductCategory.objects.get(name = 'test category')
        c2 = ProductCategory.objects.get(name = 'test category2')
        self.assertTrue(c1.audit_log.is_tracking_enabled())
        c1.audit_log.disable_tracking()
        self.assertFalse(c1.audit_log.is_tracking_enabled())
        self.assertTrue(c2.audit_log.is_tracking_enabled())


    def test_disable_enable_class(self):
        self.assertRaises(ValueError, ProductCategory.audit_log.disable_tracking)
        self.assertRaises(ValueError, ProductCategory.audit_log.enable_tracking)
        self.assertRaises(ValueError, ProductCategory.audit_log.is_tracking_enabled)

    def test_disabled_not_tracking(self):
        ProductCategory(name = 'test category', description = 'test').save()
        ProductCategory(name = 'test category2', description = 'test').save()
        c1 = ProductCategory.objects.get(name = 'test category')
        c2 = ProductCategory.objects.get(name = 'test category2')
        c1.description = 'best'
        c1.audit_log.disable_tracking()
        c1.save()
        self.assertEqual(c1.audit_log.all().count(), 1)
        c1.audit_log.enable_tracking()
        c1.description = 'new desc'
        c1.save()
        self.assertEqual(c1.audit_log.all().count(), 2)
        c1.audit_log.disable_tracking()
        c1.delete()
        self.assertEqual(ProductCategory.audit_log.all().count(), 3)


class OnDeleteBehaviorTest(TestCase):

    def test_deleting_user_nulls_action_user(self):
        """Deleting a user sets action_user=NULL on log entries (SET_NULL) rather than deleting them."""
        User = get_user_model()
        credentials = {User.USERNAME_FIELD: 'editor@example.com', 'password': 'pass'}
        user = User.objects.create_user(**credentials)
        category = ProductCategory.objects.create(name='cat', description='test')
        entry_count = ProductCategory.audit_log.all().count()
        self.assertGreater(entry_count, 0)

        # Directly stamp action_user on existing entries so we have something to verify.
        ProductCategory.audit_log.model.objects.update(action_user=user)
        self.assertEqual(ProductCategory.audit_log.first().action_user, user)

        user.delete()

        # Log entries must survive and action_user must be NULL.
        self.assertEqual(ProductCategory.audit_log.all().count(), entry_count)
        self.assertIsNone(ProductCategory.audit_log.first().action_user)

    def test_deleting_fk_related_object_preserves_audit_log(self):
        """Deleting a FK-related object does not cascade-delete audit log entries.

        ProductAuditLogEntry.category has db_constraint=False so that stale FK
        values don't trigger IntegrityErrors and log entries are fully preserved.
        """
        category = ProductCategory.objects.create(name='cat', description='desc')
        product = Product.objects.create(
            name='widget', description='desc', price=1.00, category=category
        )
        entry_count = Product.audit_log.all().count()
        self.assertGreater(entry_count, 0)

        # Deleting the category cascades to Product (Product.category on_delete=CASCADE).
        # ProductAuditLogEntry.category uses db_constraint=False + DO_NOTHING, so its
        # entries survive with their historical category_id intact (no IntegrityError).
        category.delete()

        self.assertEqual(Product.objects.count(), 0)
        # The original entries plus a new 'D' entry from the cascade delete.
        self.assertEqual(Product.audit_log.all().count(), entry_count + 1)
        self.assertEqual(Product.audit_log.filter(action_type='D').count(), 1)
