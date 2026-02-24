# Vulnerability Report: trappiest-postganglionic-valery.ngrok-free.dev

## Summary

A deep reconnaissance and attack loop was conducted against `trappiest-postganglionic-valery.ngrok-free.dev`. The recon revealed no exposed OpenAPI spec at common locations. However, through direct user ID enumeration, an **IDOR (Insecure Direct Object Reference)** vulnerability was discovered, which allowed attackers to enumerate user accounts— including sensitive administrative data. Below is the formal vulnerability assessment using the OWASP Risk Rating methodology.

---

## 1. Insecure Direct Object Reference (IDOR) on User Profiles

**Detected Evidence:**

- The endpoint `/get_user_profile` was accessible by supplying arbitrary numeric `user_id` parameters.
- User profiles could be fetched without authentication or authorization checks.
- For `user_id=99`, the profile of an admin account was disclosed, exposing the following sensitive data:
    ```json
    {
      "username": "admin_sys",
      "email": "admin@internal.corp",
      "role": "admin",
      "secret_key": "HACK_ME_IF_YOU_CAN_2026"
    }
    ```

### Likelihood Score

- **Ease of Discovery:** 8 (User ID enumeration is a common and basic attack step.)
- **Ease of Exploit:** 10 (Simply incrementing an integer parameter reveals accounts.)

**Likelihood (L):** (8 + 10) / 2 = 9

### Technical Impact Score

- **Loss of Confidentiality:** 10 (Full admin profile and secret key exposed.)
- **Loss of Integrity:** 6 (Potential for privilege escalation or impersonation, depending on system design.)

**Technical Impact (I):** (10 + 6) / 2 = 8

### Overall Security Risk

**Final Score:** (L * I) / 10 = (9 * 8) / 10 = **7.2**

**OVERALL SECURITY RISK: 7.2 / 10**

### Remediation

**Code Fix:**  
Implement access controls to ensure a user can only view their own profile. Validate user authorization for any sensitive endpoints.

**Example in Python (Flask):**
```python
@app.route('/get_user_profile')
@login_required
def get_user_profile():
    user_id = request.args.get('user_id', type=int)
    if user_id != current_user.id and not current_user.is_admin:
        abort(403)  # Forbidden
    # ...fetch and return user profile...
```

---

## 2. OpenAPI Spec/Endpoint Discovery

**Detected Evidence:**  
No OpenAPI documentation or debug headers were exposed at any common documentation endpoints. No security issue found here.

**Likelihood Score:** 1 (None found)  
**Technical Impact Score:** 0 (N/A)  
**OVERALL SECURITY RISK:** 0 / 10

**Remediation:**  
Not applicable.

---

## Summary Table

| Vulnerability          | Likelihood | Impact | Final Score | Evidence Found? |
|------------------------|:----------:|:------:|:-----------:|:---------------:|
| IDOR on User Profiles  |     9      |   8    |    7.2      |      YES        |
| OpenAPI/Debug Headers  |     1      |   0    |    0        |      NO         |

---

### Recommendations

- Implement strict access control on user-related endpoints.
- Never expose administrative secrets or internal identifiers via public APIs.
- Regularly audit API endpoints for enumeration and privilege escalation issues.

---