## ℹ️ Info

This is a test website + automation framework

- ✅ [**Users App - Stable version #1.4**](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.4_jan_4_2026/users_app)
- ✅ [**UI tests - Stable version #1.4**](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.4_jan_4_2026/ui_tests_pw)
- ℹ️ `users_app` module created on Oct-10-2025
- ℹ️ `ui_tests_pw` module created on Nov-05-2025

---

## 📦 Releases

- 🟨 **[v1.5](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.5_jan_9_2025)** is in progress, it is not released yet
- 🟩 **[v1.4](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.4_jan_4_2026)** released on Jan-04-2026
- 🟩 **[v1.3](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.3_dec_28_2025)** released on Dec-28-2025
- 🟩 **[v1.2](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.2_dec_23_2025)** released on Dec-23-2025
- 🟩 **[v1.1](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.1_dec_19_2025)** released on Dec-19-2025
- 🟩 **[v1](https://github.com/inartov555/user_hub_web_app/tree/stable_v1_nov_05_2025)** released on Nov-05-2025

---

## 📌 Changelog v1.5 vs. v1.4

- 🛠️ **Fixed in `ui_tests_pw`:** Safari: white text on the white background in the select element was displayed when the dark theme was on
- 🛠️ **Fixed in `users_app`:** Excel: user could press the import button and process was started from scratch without waiting to finish the previous one
- 🛠️ **Fixed in `users_app`:** NavBar: Tabs were messed up when localization changed to, e.g., Spanish
- ✨ **Improved in `ui_tests_pw`:** Smart browser install (only selected one instead of all supported to preserve time)
- ✨ **Improved in `ui_tests_pw`:** Existing test structure, lite refactoring
- ✨ **Improved in `users_app`:** Page styles such as background, etc.
- ✨ **Improved in `users_app`:** Localization (removed unused, updated existing, localized not localized text)
- 🆕 **Added in `ui_tests_pw`:** New tests to test_change_password_page.py
- 🆕 **Added in `ui_tests_pw`:** New tests to test_settings_page.py
- 🆕 **Added in `ui_tests_pw`:** New tests to test_excel_import_page.py

---

## 📌 Changelog v1.4 vs. v1.3

- 🛠️ **Fixed in `users_app`:** 200 users were selected max, while more are available for selection to delete
- 🛠️ **Fixed in `users_app`:** Breaking words without spaces in lines in the UserDeleteConfirm page
- 🛠️ **Fixed in `users_app`:** The page error page showed the same list of users, including removed ones, when some users were not removed after submitting
- 🛠️ **Fixed in `users_app`:** Highlight hid the text when the mouse pointer was over an item on the column visibility pop-up of the UsersTable page
- 🛠️ **Fixed in `ui_tests_pw`:** Firefox: user redirected to the /login page after successful logging in and trying to open the /users page
- 🛠️ **Fixed in `ui_tests_pw`:** Firefox: sometimes, one random test failed to set the theme because the Login page is not fully loaded yet
- 🛠️ **Fixed in `ui_tests_pw`:** Firefox: sometimes, one random test failed to log in because the submit button cannot be clicked on the Login page
- 🛠️ **Fixed in `ui_tests_pw`:** Firefox: sometimes, one random test failed to type search text due to not finding the search input on the Users Table page
- 🛠️ **Fixed in `ui_tests_pw`:** Safari/Webkit: sometimes, one random test failed because the browser got closed
- ✨ **Improved in `users_app`:** Lite UI polishing
- ✨ **Improved in `users_app`:** Duplicating buttons, at the bottom and top of the content block for the UsersTable and UserDeleteConfirm pages
- ✨ **Improved in `users_app`:** Highlight kept for a row after checking it on the UsersTable page
- ✨ **Improved in `users_app`:** Unifying error message with a SimpleErrorMessage component
- 🆕 **Added in `users_app`:** Show/hide button for the password field
- 🆕 **Added in `users_app`:** Icons to page titles
- 🆕 **Added in `users_app`:** User ID column to the UserDeleteConfirm page
- 🆕 **Added in `ui_tests_pw`:** Logging in as a just created user for `test_signup_with_random_username`
- 🆕 **Added in `ui_tests_pw`:** New `test_base_demo` & `test_locale_demo` which walks all main pages and takes screenshots

---

## 📌 Changelog v1.3 vs. v1.2

- 🛠️ **Fixed in `ui_tests_pw`:** test_locale_dropdown_matches_backend_languages (ModuleNotFoundError: No module named 'core')
- 🛠️ **Fixed in `users_app`:** Unlocalized title for the Sign up page
- ✨ **Improved in `users_app`:** Polishing UI accross the website
- ✨ **Improved in `users_app`:** Behavior for the Cancel button in View/Edit Profile, Change Password pages (small area in the middle of the button was clickable)
- ✨ **Improved in `users_app`:** Validation in App Settings
- ✨ **Improved in `users_app`:** Button disabled state color now is more obvious
- ✨ **Improved in `ui_tests_pw`:** Now regular user, which is required by tests, is automatically created if not present
- 🆕 **Added in `ui_tests_pw`:** Localization checks to tests
- 🆕 **Added in `ui_tests_pw`:** Cleanup fixture for theme and locale (default is light theme and en-US locale)
- 🆕 **Added in `users_app`:** Localized tooltip text to elements without any text

---

## 📌 Changelog v1.2 vs. v1.1

- 🛠️ **Fixed in `users_app`:** Infinite requesting /api/v1/auth/users/me/ after 1st login with clear localStorage
- 🛠️ **Fixed in `users_app`:** Users table header was shown over the Column visibility popup
- 🛠️ **Fixed in `users_app`:** Users table -> Column visibility popup was not dismissed when clicked outside the overlay
- 🛠️ **Fixed in `users_app`:** Users table -> Column visibility popup settings were not preserved after page reload
- 🛠️ **Fixed in `users_app`:** A space was displayed after deselecting all columns while being logged in as a regular user
- 🛠️ **Fixed in `users_app`:** Profile Edit -> save an avatar > 1 MB -> 413 Request Entity Too Large (increased size to 10 MB)
- 🛠️ **Fixed in `users_app`:** Excel import -> incorrect counting of updated users (non-changed users were counted as updated ones when importing)
- 🛠️ **Fixed in `users_app`:** Excel import -> there was no validation for user uniqueness when importing
- ✨ **Improved in `users_app`:** Unifying button style accross the website
- ✨ **Improved in `users_app`:** Prettifying table headers (mouse over/up/down styles)
- ✨ **Improved in `users_app`:** Localization for some error cases
- ✨ **Improved in `users_app`:** Excel import -> email validation when importing
- 🆕 **Added in `users_app`:** Cookie consent overlay
- 🆕 **Added in `ui_tests_pw`:** Handling the cookie consent overlay in automation tests

---

## 📌 Changelog v1.1 vs. v1

- 🛠️ **Fixed in `users_app`:** /import-excel (Additional -> Import from Excel tab), Download Template button threw HTTP 404
- 🛠️ **Fixed in `users_app`:** /users/confirm-delete (when confirming user deletion), error thrown, and the website was not redirected to the /users page
- 🛠️ **Fixed in `users_app`:** /users page, sorting got cleared after page refresh
- ✨ **Improved in `users_app` & `ui_tests_pw`:** GitHub actions logic
- ✨ **Improved in `users_app`:** Docker configuration
- ✨ **Improved in `users_app`:** run_web_site.sh & setup.sh
- 🆕 **Added in `users_app`:** data-tag, id, etc. to key elements used in UI automation for convenience
- 🆕 **Added `ui_tests_pw`:** UI test framework
