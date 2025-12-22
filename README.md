## ℹ️ Info

This is a test website + automation framework

- ✅ **Users App - Stable version #1.1:** [stable_v1.1_dec_19_2025/users_app](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.1_dec_19_2025/users_app)
- ℹ️ More info related to the Users App: [tree/stable_v1.1_dec_19_2025/users_app/README.md](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.1_dec_19_2025/users_app/README.md)
- ✅ **UI tests - Stable version #1.1:** [stable_v1.1_dec_19_2025/ui_tests_pw](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.1_dec_19_2025/ui_tests_pw)
- ℹ️ More info related to the UI tests: [stable_v1.1_dec_19_2025/ui_tests_pw/README.md](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.1_dec_19_2025/ui_tests_pw/README.md)
- ℹ️ `users_app` module created on Oct-10-2025
- ℹ️ `ui_tests_pw` module created on Nov-05-2025

---

## 📦 Releases

- 🟨 **v1.2** is in progress, it is not released yet
- 🟩 **[v1.1](https://github.com/inartov555/user_hub_web_app/tree/stable_v1.1_dec_19_2025)** released on Dec-19-2025
- 🟩 **[v1](https://github.com/inartov555/user_hub_web_app/tree/stable_v1_nov_05_2025)**   released on Nov-05-2025

---

## 📌 Changelog v1.2 vs. v1.1

- 🛠️ **Fixed in `users_app`:** Infinite requesting /api/v1/auth/users/me/ after 1st login with clear localStorage
- 🛠️ **Fixed in `users_app`:** Users table header was shown over the Column visibility popup
- 🛠️ **Fixed in `users_app`:** Users table -> Column visibility popup was not dismissed when clicked outside the overlay
- 🛠️ **Fixed in `users_app`:** Users table -> Column visibility popup settings were not preserved after page reload
- 🛠️ **Fixed in `users_app`:** Empty space was displayed after deselecting all columns while being logged in as a regular user
- ✨ **Improved in `users_app`:** Unifying button style accross the website
- ✨ **Improved in `users_app`:** Prettifying table headers (mouse over/up/down styles)
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
