## 🗂️ (54) List of automation test (parametrization not considered)

---

1. **tests/test_about_website_page.py**
 - test_verify_there_are_login_and_signup_links_for_logged_in_user
 - test_verify_that_there_s_no_login_and_signup_links_for_logged_in_user
 - test_links_to_signup_and_login

---

2. **tests/test_change_password_page.py**
 - test_admin_can_open_change_password_for_user
 - test_regular_user_cannot_change_other_users_password
 - test_admin_can_change_password_for_any_user
 - test_regular_user_change_own_password

---

3. **tests/test_demo.py**
 - test_demo_homepage_title
 - test_demo_login_flow

---

4. **tests/test_excel_import_page.py**
 - test_excel_import_page_access_denied_for_regular_user
 - test_excel_import_page_access_granted_for_admin
 - test_excel_import_upload_valid_file_admin
 - test_excel_import_upload_invalid_file_admin
 - tests/test_localization_backend_vs_ui.py
 - test_localization_backend_vs_ui_matches_admin
 - test_localization_backend_vs_ui_matches_regular_user

---

5. **tests/test_login_page.py**
 - test_login_page_renders
 - test_login_valid_credentials_admin
 - test_login_valid_credentials_regular_user
 - test_login_invalid_credentials_shows_error
 - test_login_redirects_when_already_logged_in

---

6. **tests/test_logout.py**
 - test_logout_admin
 - test_logout_regular_user

---

7. **tests/test_profile_edit_page.py**
 - test_profile_edit_page_access_admin
 - test_profile_edit_page_access_regular_user
 - test_profile_edit_update_name
 - test_profile_edit_update_email
 - test_profile_edit_cancel_does_not_save

---

8. **tests/test_profile_view_page.py**
 - test_profile_view_page_access_admin
 - test_profile_view_page_access_regular_user
 - test_profile_view_shows_user_details

---

9. **tests/test_reset_password_page.py**
 - test_reset_password_page_renders
 - test_reset_password_invalid_email_shows_error
 - test_reset_password_valid_email_shows_success

---

10. **tests/test_settings_page.py**
 - test_settings_page_access_admin
 - test_settings_page_access_denied_for_regular_user
 - test_settings_change_theme
 - test_settings_change_locale
 - test_settings_persists_preferences

---

11. **tests/test_signup_page.py**
 - test_signup_page_renders
 - test_signup_valid_data_creates_user
 - test_signup_invalid_data_shows_errors
 - test_signup_duplicate_email_shows_error

---

12. **tests/test_stats_page.py**
 - test_stats_page_access_admin
 - test_stats_page_access_denied_for_regular_user
 - test_stats_page_renders_charts_for_admin
 - test_stats_page_filters_work_for_admin

---

13. **tests/test_user_delete_confirm_page.py**
 - test_user_delete_confirm_page_access_admin
 - test_user_delete_confirm_page_access_denied_for_regular_user
 - test_user_delete_confirm_admin_can_delete_user
 - test_user_delete_confirm_cancel_does_not_delete

---

14. **tests/test_users_table_page.py**
 - test_users_table_admin_theme_and_locale
 - test_users_table_regular_user_has_restricted_controls
 - test_users_table_multi_column_sort_admin
 - test_users_table_clear_sort_resets_order
 - test_users_table_search_filters_results
