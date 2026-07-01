from types import SimpleNamespace

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory

from dashboard_24782091.views import DashboardDataView, DashboardView
from main_app.models import Report
from main_app.permissions import CanAccessDraftReport
from usermanagement_24782091.serializers import RegisterSerializer
from usermanagement_24782091.views import CustomLoginView


User = get_user_model()


class SimplePageCoverageTests(TestCase):
    def test_about_and_contacts_pages_render(self):
        about_response = self.client.get(reverse('about'))
        contacts_response = self.client.get(reverse('contacts'))

        self.assertEqual(about_response.status_code, 200)
        self.assertEqual(contacts_response.status_code, 200)


class DashboardCoverageTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='dashboard_user',
            password='StrongPass123!',
            is_admin=False,
        )
        Report.objects.create(
            title='Lampu Jalan Mati',
            category='Infrastruktur',
            description='Lampu jalan mati sejak malam.',
            location='Jl. Merdeka',
            status='REPORTED',
            reporter=self.user,
        )
        Report.objects.create(
            title='Sampah Terangkut',
            category='Lingkungan',
            description='Sampah sudah selesai ditangani.',
            location='Pasar Tengah',
            status='RESOLVED',
            reporter=self.user,
        )

    def test_dashboard_template_view_uses_expected_template(self):
        view = DashboardView()

        self.assertEqual(view.template_name, 'dashboard/dashboard.html')

    def test_dashboard_data_returns_report_summary(self):
        response = self.client.get(reverse('dashboard_data'))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload['total_reports'], 2)
        self.assertEqual(len(payload['latest_reported']), 1)
        self.assertEqual(len(payload['latest_resolved']), 1)
        self.assertTrue(any(item['status'] == 'REPORTED' for item in payload['status_data']))
        self.assertTrue(any(item['category'] == 'Lingkungan' for item in payload['category_data']))

    def test_dashboard_data_view_get_direct_call(self):
        request = APIRequestFactory().get('/dashboard/data/')
        response = DashboardDataView.as_view()(request)

        self.assertEqual(response.status_code, 200)


class UserManagementSerializerCoverageTests(TestCase):
    def test_register_serializer_creates_citizen_user(self):
        serializer = RegisterSerializer(data={
            'username': 'new_citizen',
            'email': 'new_citizen@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.username, 'new_citizen')
        self.assertEqual(user.email, 'new_citizen@example.com')
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_member)
        self.assertTrue(user.check_password('StrongPass123!'))

    def test_register_serializer_rejects_duplicate_email(self):
        User.objects.create_user(
            username='existing_user',
            email='same@example.com',
            password='StrongPass123!',
        )
        serializer = RegisterSerializer(data={
            'username': 'another_user',
            'email': 'same@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_register_serializer_rejects_mismatched_password_confirmation(self):
        serializer = RegisterSerializer(data={
            'username': 'mismatch_user',
            'email': 'mismatch@example.com',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass123!',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('password2', serializer.errors)


class UserManagementApiCoverageTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='api_user',
            password='StrongPass123!',
            is_admin=False,
            is_member=True,
        )

    def test_register_api_creates_citizen(self):
        response = self.client.post(reverse('api_register'), {
            'username': 'api_new_user',
            'email': 'api_new_user@example.com',
            'password': 'StrongPass123!',
            'password2': 'StrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Registrasi citizen berhasil.')
        self.assertEqual(response.data['user']['username'], 'api_new_user')
        self.assertFalse(response.data['user']['is_admin'])
        self.assertTrue(response.data['user']['is_member'])

    def test_register_api_returns_validation_error(self):
        response = self.client.post(reverse('api_register'), {
            'username': 'api_invalid_user',
            'email': 'api_invalid_user@example.com',
            'password': 'StrongPass123!',
            'password2': 'DifferentPass123!',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password2', response.data)

    def test_current_user_api_requires_authentication(self):
        response = self.client.get(reverse('api_current_user'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_current_user_api_returns_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(reverse('api_current_user'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'api_user')
        self.assertFalse(response.data['is_admin'])
        self.assertTrue(response.data['is_member'])


class MainAppApiViewSetCoverageTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='api_admin',
            password='StrongPass123!',
            is_admin=True,
        )
        self.citizen = User.objects.create_user(
            username='api_citizen',
            password='StrongPass123!',
            is_admin=False,
        )
        self.other = User.objects.create_user(
            username='api_other',
            password='StrongPass123!',
            is_admin=False,
        )
        self.admin_report = Report.objects.create(
            title='Admin Reported',
            category='Infrastruktur',
            description='Laporan admin',
            location='Kantor Admin',
            status='REPORTED',
            reporter=self.admin,
        )
        self.citizen_draft = Report.objects.create(
            title='Citizen Draft',
            category='Lingkungan',
            description='Laporan draft warga',
            location='Rumah Warga',
            status='DRAFT',
            reporter=self.citizen,
        )
        self.other_reported = Report.objects.create(
            title='Other Reported',
            category='Transportasi',
            description='Laporan warga lain',
            location='Halte Kota',
            status='REPORTED',
            reporter=self.other,
        )

    def test_report_queryset_for_anonymous_is_empty_but_blocked_by_auth(self):
        response = self.client.get(reverse('report-list'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_my_reports_tab_excludes_draft_and_limits_to_admin_reports(self):
        Report.objects.create(
            title='Admin Draft',
            category='Infrastruktur',
            description='Draft admin',
            location='Kantor Admin',
            status='DRAFT',
            reporter=self.admin,
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('report-list'), {'tab': 'my_reports'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item['title'] for item in response.data['results']]
        self.assertIn('Admin Reported', titles)
        self.assertNotIn('Admin Draft', titles)
        self.assertNotIn('Other Reported', titles)

    def test_admin_feed_tab_excludes_all_drafts(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(reverse('report-list'), {'tab': 'feed'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item['title'] for item in response.data['results']]
        self.assertIn('Admin Reported', titles)
        self.assertIn('Other Reported', titles)
        self.assertNotIn('Citizen Draft', titles)

    def test_citizen_default_queryset_includes_public_and_own_draft(self):
        self.client.force_authenticate(user=self.citizen)

        response = self.client.get(reverse('report-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [item['title'] for item in response.data['results']]
        self.assertIn('Citizen Draft', titles)
        self.assertIn('Other Reported', titles)

    def test_citizen_create_sets_reporter_from_request_user(self):
        self.client.force_authenticate(user=self.citizen)

        response = self.client.post(reverse('report-list'), {
            'title': 'Created From API',
            'category': 'Infrastruktur',
            'description': 'Dibuat melalui API',
            'location': 'Taman Kota',
            'status': 'DRAFT',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        report = Report.objects.get(title='Created From API')
        self.assertEqual(report.reporter, self.citizen)

    def test_admin_update_requires_status_field(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse('report-detail', args=[self.other_reported.pk]),
            {'title': 'Tidak Boleh'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Admin wajib mengirim field status.')

    def test_admin_update_rejects_fields_other_than_status(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse('report-detail', args=[self.other_reported.pk]),
            {'status': 'VERIFIED', 'title': 'Tidak Boleh'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Admin hanya dapat memperbarui status laporan.')

    def test_admin_partial_update_can_change_only_status(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.patch(
            reverse('report-detail', args=[self.other_reported.pk]),
            {'status': 'VERIFIED'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.other_reported.refresh_from_db()
        self.assertEqual(self.other_reported.status, 'VERIFIED')

    def test_citizen_update_uses_standard_update_flow_for_own_draft(self):
        self.client.force_authenticate(user=self.citizen)

        response = self.client.put(
            reverse('report-detail', args=[self.citizen_draft.pk]),
            {
                'title': 'Citizen Draft Updated',
                'category': 'Lingkungan',
                'description': 'Draft warga diperbarui',
                'location': 'Rumah Warga',
                'status': 'REPORTED',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.citizen_draft.refresh_from_db()
        self.assertEqual(self.citizen_draft.title, 'Citizen Draft Updated')
        self.assertEqual(self.citizen_draft.status, 'REPORTED')


class UserManagementViewCoverageTests(TestCase):
    def test_register_view_get_renders_form(self):
        response = self.client.get(reverse('register'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')

    def test_register_view_post_creates_non_admin_user(self):
        response = self.client.post(reverse('register'), {
            'username': 'form_user',
            'email': 'form_user@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })

        self.assertRedirects(response, reverse('login'))
        user = User.objects.get(username='form_user')
        self.assertFalse(user.is_admin)

    def test_login_view_success_url_and_invalid_form(self):
        view = CustomLoginView()
        self.assertEqual(view.get_success_url(), '/')

        response = self.client.post(reverse('login'), {
            'username': 'missing_user',
            'password': 'wrong-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Username')

    def test_login_and_logout_views(self):
        User.objects.create_user(
            username='login_user',
            password='StrongPass123!',
        )

        login_response = self.client.post(reverse('login'), {
            'username': 'login_user',
            'password': 'StrongPass123!',
        })
        self.assertRedirects(login_response, '/')

        logout_response = self.client.post(reverse('logout'))
        self.assertRedirects(logout_response, reverse('home'))


class PermissionCoverageTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = CanAccessDraftReport()
        self.owner = User.objects.create_user(
            username='owner_perm',
            password='StrongPass123!',
            is_admin=False,
        )
        self.other = User.objects.create_user(
            username='other_perm',
            password='StrongPass123!',
            is_admin=False,
        )
        self.admin = User.objects.create_user(
            username='admin_perm',
            password='StrongPass123!',
            is_admin=True,
        )
        self.draft = Report.objects.create(
            title='Draft Laporan',
            category='Infrastruktur',
            description='Draft',
            location='Lokasi',
            status='DRAFT',
            reporter=self.owner,
        )
        self.reported = Report.objects.create(
            title='Reported Laporan',
            category='Infrastruktur',
            description='Reported',
            location='Lokasi',
            status='REPORTED',
            reporter=self.owner,
        )
        self.resolved = Report.objects.create(
            title='Resolved Laporan',
            category='Infrastruktur',
            description='Resolved',
            location='Lokasi',
            status='RESOLVED',
            reporter=self.owner,
        )

    def build_request(self, method, user):
        request = getattr(self.factory, method.lower())('/api/report/1/')
        request.user = user
        return request

    def test_permission_denies_anonymous_and_admin_create(self):
        anonymous_request = self.build_request('get', AnonymousUser())
        admin_create_request = self.build_request('post', self.admin)

        self.assertFalse(
            self.permission.has_permission(
                anonymous_request,
                SimpleNamespace(action='list'),
            )
        )
        self.assertFalse(
            self.permission.has_permission(
                admin_create_request,
                SimpleNamespace(action='create'),
            )
        )

    def test_permission_allows_citizen_create(self):
        request = self.build_request('post', self.owner)

        self.assertTrue(
            self.permission.has_permission(
                request,
                SimpleNamespace(action='create'),
            )
        )

    def test_object_permission_safe_methods_for_admin_and_citizen(self):
        admin_request = self.build_request('get', self.admin)
        owner_request = self.build_request('get', self.owner)
        other_request = self.build_request('get', self.other)

        self.assertFalse(
            self.permission.has_object_permission(
                admin_request,
                SimpleNamespace(action='retrieve'),
                self.draft,
            )
        )
        self.assertTrue(
            self.permission.has_object_permission(
                owner_request,
                SimpleNamespace(action='retrieve'),
                self.draft,
            )
        )
        self.assertFalse(
            self.permission.has_object_permission(
                other_request,
                SimpleNamespace(action='retrieve'),
                self.draft,
            )
        )
        self.assertTrue(
            self.permission.has_object_permission(
                other_request,
                SimpleNamespace(action='retrieve'),
                self.reported,
            )
        )

    def test_object_permission_write_rules(self):
        owner_patch_request = self.build_request('patch', self.owner)
        admin_patch_request = self.build_request('patch', self.admin)
        other_delete_request = self.build_request('delete', self.other)

        self.assertFalse(
            self.permission.has_object_permission(
                owner_patch_request,
                SimpleNamespace(action='partial_update'),
                self.resolved,
            )
        )
        self.assertTrue(
            self.permission.has_object_permission(
                admin_patch_request,
                SimpleNamespace(action='partial_update'),
                self.reported,
            )
        )
        self.assertTrue(
            self.permission.has_object_permission(
                owner_patch_request,
                SimpleNamespace(action='partial_update'),
                self.draft,
            )
        )
        self.assertFalse(
            self.permission.has_object_permission(
                other_delete_request,
                SimpleNamespace(action='destroy'),
                self.draft,
            )
        )
