from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Report


User = get_user_model()


class ReportApiRoleTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='password',
            is_admin=True,
        )
        self.owner = User.objects.create_user(
            username='owner',
            password='password',
        )
        self.other = User.objects.create_user(
            username='other',
            password='password',
        )
        self.owner_draft = self.create_report(self.owner, 'Owner Draft', 'DRAFT')
        self.other_draft = self.create_report(self.other, 'Other Draft', 'DRAFT')
        self.owner_reported = self.create_report(
            self.owner,
            'Owner Reported',
            'REPORTED',
        )
        self.other_reported = self.create_report(
            self.other,
            'Other Reported',
            'REPORTED',
        )

    @staticmethod
    def create_report(reporter, title, status):
        return Report.objects.create(
            reporter=reporter,
            title=title,
            category='Jalan',
            description='Deskripsi laporan',
            location='Bandar Lampung',
            status=status,
        )

    @staticmethod
    def report_payload(status='REPORTED'):
        return {
            'title': 'Laporan Baru',
            'category': 'Jalan',
            'description': 'Deskripsi laporan baru',
            'location': 'Bandar Lampung',
            'status': status,
        }

    def authenticate(self, user):
        self.client.force_authenticate(user=user)

    def list_ids(self, tab=None):
        url = reverse('report-list')
        if tab:
            url = f'{url}?tab={tab}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return {item['id'] for item in response.data['results']}

    def test_admin_can_only_see_non_draft_reports(self):
        self.authenticate(self.admin)

        ids = self.list_ids()

        self.assertNotIn(self.owner_draft.id, ids)
        self.assertNotIn(self.other_draft.id, ids)
        self.assertIn(self.owner_reported.id, ids)
        self.assertIn(self.other_reported.id, ids)

    def test_admin_cannot_retrieve_or_update_draft_by_id(self):
        self.authenticate(self.admin)
        url = reverse('report-detail', args=[self.owner_draft.id])

        self.assertEqual(self.client.get(url).status_code, 404)
        self.assertEqual(
            self.client.patch(url, {'status': 'VERIFIED'}, format='json').status_code,
            404,
        )

    def test_admin_cannot_create_delete_or_edit_report_content(self):
        self.authenticate(self.admin)
        list_url = reverse('report-list')
        detail_url = reverse('report-detail', args=[self.owner_reported.id])

        self.assertEqual(
            self.client.post(list_url, self.report_payload(), format='json').status_code,
            403,
        )
        self.assertEqual(
            self.client.patch(
                detail_url,
                {'title': 'Diubah Admin'},
                format='json',
            ).status_code,
            403,
        )
        self.assertEqual(self.client.delete(detail_url).status_code, 403)

    def test_admin_can_only_assign_non_draft_status(self):
        self.authenticate(self.admin)
        url = reverse('report-detail', args=[self.owner_reported.id])

        invalid_response = self.client.patch(
            url,
            {'status': 'DRAFT'},
            format='json',
        )
        valid_response = self.client.patch(
            url,
            {'status': 'VERIFIED'},
            format='json',
        )

        self.assertEqual(invalid_response.status_code, 400)
        self.assertEqual(valid_response.status_code, 200)
        self.owner_reported.refresh_from_db()
        self.assertEqual(self.owner_reported.status, 'VERIFIED')

    def test_citizen_visibility_includes_own_draft_but_not_other_draft(self):
        self.authenticate(self.owner)

        ids = self.list_ids()

        self.assertIn(self.owner_draft.id, ids)
        self.assertNotIn(self.other_draft.id, ids)
        self.assertIn(self.owner_reported.id, ids)
        self.assertIn(self.other_reported.id, ids)

    def test_citizen_feed_includes_own_and_other_non_draft_reports(self):
        self.authenticate(self.owner)

        ids = self.list_ids(tab='feed')

        self.assertNotIn(self.owner_draft.id, ids)
        self.assertNotIn(self.other_draft.id, ids)
        self.assertIn(self.owner_reported.id, ids)
        self.assertIn(self.other_reported.id, ids)

    def test_citizen_can_create_only_draft_or_reported(self):
        self.authenticate(self.owner)
        url = reverse('report-list')

        draft_response = self.client.post(
            url,
            self.report_payload('DRAFT'),
            format='json',
        )
        reported_response = self.client.post(
            url,
            self.report_payload('REPORTED'),
            format='json',
        )
        invalid_response = self.client.post(
            url,
            self.report_payload('VERIFIED'),
            format='json',
        )

        self.assertEqual(draft_response.status_code, 201)
        self.assertEqual(reported_response.status_code, 201)
        self.assertEqual(invalid_response.status_code, 400)

    def test_citizen_can_edit_content_and_delete_own_report(self):
        self.authenticate(self.owner)
        update_url = reverse('report-detail', args=[self.owner_reported.id])
        delete_url = reverse('report-detail', args=[self.owner_draft.id])

        update_response = self.client.patch(
            update_url,
            {'title': 'Judul Milik Sendiri'},
            format='json',
        )
        delete_response = self.client.delete(delete_url)

        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(delete_response.status_code, 204)
        self.owner_reported.refresh_from_db()
        self.assertEqual(self.owner_reported.title, 'Judul Milik Sendiri')
        self.assertFalse(Report.objects.filter(pk=self.owner_draft.id).exists())

    def test_citizen_can_submit_own_draft_as_reported(self):
        self.authenticate(self.owner)
        url = reverse('report-detail', args=[self.owner_draft.id])

        response = self.client.patch(
            url,
            {'status': 'REPORTED'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.owner_draft.refresh_from_db()
        self.assertEqual(self.owner_draft.status, 'REPORTED')

    def test_citizen_cannot_change_status_or_manage_another_report(self):
        self.authenticate(self.owner)
        own_url = reverse('report-detail', args=[self.owner_reported.id])
        other_url = reverse('report-detail', args=[self.other_reported.id])

        status_response = self.client.patch(
            own_url,
            {'status': 'RESOLVED'},
            format='json',
        )
        edit_response = self.client.patch(
            other_url,
            {'title': 'Bukan Miliknya'},
            format='json',
        )
        delete_response = self.client.delete(other_url)

        self.assertEqual(status_response.status_code, 400)
        self.assertEqual(edit_response.status_code, 403)
        self.assertEqual(delete_response.status_code, 403)


class ReportDjangoViewRoleTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin-view',
            password='password',
            is_admin=True,
        )
        self.owner = User.objects.create_user(
            username='owner-view',
            password='password',
        )
        self.other = User.objects.create_user(
            username='other-view',
            password='password',
        )
        self.draft = ReportApiRoleTests.create_report(
            self.owner,
            'Draft View',
            'DRAFT',
        )
        self.reported = ReportApiRoleTests.create_report(
            self.owner,
            'Reported View',
            'REPORTED',
        )

    def test_admin_status_endpoint_rejects_draft_and_invalid_status(self):
        self.client.force_login(self.admin)
        draft_url = reverse('update_status', args=[self.draft.id])
        reported_url = reverse('update_status', args=[self.reported.id])

        self.assertEqual(
            self.client.post(draft_url, {'status': 'VERIFIED'}).status_code,
            404,
        )
        self.client.post(reported_url, {'status': 'DRAFT'})

        self.reported.refresh_from_db()
        self.assertEqual(self.reported.status, 'REPORTED')

    def test_admin_report_list_renders_status_control(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse('report_list'))

        self.assertContains(response, 'Ubah Status')
        self.assertContains(
            response,
            reverse('update_status', args=[self.reported.id]),
        )
        self.assertContains(response, 'name="status"')

    def test_citizen_cannot_use_admin_status_endpoint(self):
        self.client.force_login(self.owner)
        url = reverse('update_status', args=[self.reported.id])

        self.client.post(url, {'status': 'RESOLVED'})

        self.reported.refresh_from_db()
        self.assertEqual(self.reported.status, 'REPORTED')

    def test_admin_cannot_create_report_and_other_citizen_cannot_edit_or_delete(self):
        self.client.force_login(self.admin)
        create_response = self.client.post(
            reverse('add_report'),
            {
                'title': 'Admin Report',
                'category': 'Jalan',
                'description': 'Tidak boleh dibuat',
                'location': 'Bandar Lampung',
            },
        )
        self.assertEqual(create_response.status_code, 302)
        self.assertFalse(Report.objects.filter(title='Admin Report').exists())

        self.client.force_login(self.other)
        edit_response = self.client.post(
            reverse('update_report', args=[self.reported.id]),
            {
                'title': 'Diubah Orang Lain',
                'category': self.reported.category,
                'description': self.reported.description,
                'location': self.reported.location,
            },
        )
        delete_response = self.client.post(
            reverse('delete_report', args=[self.reported.id]),
        )

        self.assertEqual(edit_response.status_code, 302)
        self.assertEqual(delete_response.status_code, 302)
        self.reported.refresh_from_db()
        self.assertEqual(self.reported.title, 'Reported View')
        self.assertTrue(Report.objects.filter(pk=self.reported.id).exists())
