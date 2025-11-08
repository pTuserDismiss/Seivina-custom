# Odoo Enforce Two-Factor Authentication | 2FA

## Overview

The `wk_enforce_2fa` module introduces two-level security, commonly used in multi-factor authentication processes like accessing accounts with a phone-generated code.
By implementing Odoo Enforce Two-Factor Authentication, security vulnerabilities are minimized, making unauthorized access ineffective without proper authorization.

### Features:

- **Prevent unauthorized access**
- **Enable 2FA for portal users**
- **Displays a QR code pop-up during login**

## Configuration

### Enable 2FA for internal users

1. Go to **Settings** in the Odoo backend.
2. Navigate to **Users & Companies** and select **Users**.
3. Under the **Account Security** tab, enable 2FA by clicking on the **Enforce 2FA** button for the desired user.

### Enable 2FA for public users

1. Navigate to **Settings** in the Odoo backend.
2. Under the **Website** section, go to **Privacy**.
3. Enable 2FA for public users by clicking the **Enforce 2FA For Public User** button.

## How it Works

When 2FA is enabled:

1. Upon logging in, a QR Code pop-up will appear.
2. Scan the QR Code with your mobile device.
3. A passcode will be generated on your phone.
4. Enter the passcode to successfully log into your account.

## Additional Notes

- **Setting Up an Authenticator App**:

1. Download and install an authenticator app on your mobile device. Popular options include:
    **Authy**
    **Google Authenticator**
    **Microsoft Authenticator**
2. Open the app and select the Add an account option.
3. Scan the QR Code displayed during the 2FA setup process.

---

### Credits

- **Author**: Webkul Software Pvt. Ltd.
