"""Microsoft 365 and Entra ID administration for SlayScript.

This module provides enterprise administration capabilities using Microsoft Graph API.
Requires an Azure AD app registration with appropriate permissions.

Setup:
1. Register an app in Azure AD (Entra ID)
2. Grant appropriate Microsoft Graph API permissions
3. Use summon_azure_realm() with your tenant_id, client_id, and client_secret
"""

import json
from typing import Any, List, Optional, Dict
from .environment import BuiltinFunction
from .errors import SlayScriptError

# Lazy imports for optional dependencies
_msal = None
_requests = None


class AzureRealmError(SlayScriptError):
    """Error in Azure/M365 operations."""

    def format_message(self) -> str:
        base = super().format_message()
        return f"Azure Realm Error! {base}"


def _get_msal():
    """Lazy load MSAL library."""
    global _msal
    if _msal is None:
        try:
            import msal
            _msal = msal
        except ImportError:
            raise AzureRealmError("MSAL not installed. Run: pip install msal")
    return _msal


def _get_requests():
    """Lazy load requests library."""
    global _requests
    if _requests is None:
        try:
            import requests
            _requests = requests
        except ImportError:
            raise AzureRealmError("requests not installed. Run: pip install requests")
    return _requests


class AzureRealm:
    """Manages connection to Microsoft 365 / Entra ID."""

    GRAPH_URL = "https://graph.microsoft.com/v1.0"
    GRAPH_BETA_URL = "https://graph.microsoft.com/beta"

    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self._app = None

    def authenticate(self) -> bool:
        """Authenticate with Azure AD and get access token."""
        msal = _get_msal()

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self._app = msal.ConfidentialClientApplication(
            self.client_id,
            authority=authority,
            client_credential=self.client_secret
        )

        scopes = ["https://graph.microsoft.com/.default"]
        result = self._app.acquire_token_for_client(scopes=scopes)

        if "access_token" in result:
            self.access_token = result["access_token"]
            return True
        else:
            error = result.get("error_description", result.get("error", "Unknown error"))
            raise AzureRealmError(f"Authentication failed: {error}")

    def _headers(self) -> Dict[str, str]:
        """Get headers for Graph API requests."""
        if not self.access_token:
            raise AzureRealmError("Not authenticated. Call authenticate() first.")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def _get(self, endpoint: str, beta: bool = False) -> dict:
        """Make a GET request to Graph API."""
        requests = _get_requests()
        base_url = self.GRAPH_BETA_URL if beta else self.GRAPH_URL
        url = f"{base_url}{endpoint}"

        response = requests.get(url, headers=self._headers())

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise AzureRealmError(f"Resource not found: {endpoint}")
        else:
            self._handle_error(response)

    def _post(self, endpoint: str, data: dict, beta: bool = False) -> dict:
        """Make a POST request to Graph API."""
        requests = _get_requests()
        base_url = self.GRAPH_BETA_URL if beta else self.GRAPH_URL
        url = f"{base_url}{endpoint}"

        response = requests.post(url, headers=self._headers(), json=data)

        if response.status_code in (200, 201):
            return response.json() if response.text else {}
        else:
            self._handle_error(response)

    def _patch(self, endpoint: str, data: dict, beta: bool = False) -> dict:
        """Make a PATCH request to Graph API."""
        requests = _get_requests()
        base_url = self.GRAPH_BETA_URL if beta else self.GRAPH_URL
        url = f"{base_url}{endpoint}"

        response = requests.patch(url, headers=self._headers(), json=data)

        if response.status_code in (200, 204):
            return response.json() if response.text else {}
        else:
            self._handle_error(response)

    def _delete(self, endpoint: str, beta: bool = False) -> bool:
        """Make a DELETE request to Graph API."""
        requests = _get_requests()
        base_url = self.GRAPH_BETA_URL if beta else self.GRAPH_URL
        url = f"{base_url}{endpoint}"

        response = requests.delete(url, headers=self._headers())

        if response.status_code == 204:
            return True
        else:
            self._handle_error(response)

    def _handle_error(self, response):
        """Handle Graph API error response."""
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", str(error_data))
        except Exception:
            error_msg = response.text or f"HTTP {response.status_code}"
        raise AzureRealmError(f"Graph API error: {error_msg}")

    # ============ User Management ============

    def list_users(self, select: List[str] = None, top: int = 100) -> List[dict]:
        """List users in the tenant."""
        endpoint = "/users"
        params = [f"$top={top}"]
        if select:
            params.append(f"$select={','.join(select)}")
        if params:
            endpoint += "?" + "&".join(params)
        result = self._get(endpoint)
        return result.get("value", [])

    def get_user(self, user_id: str) -> dict:
        """Get a specific user by ID or UPN."""
        return self._get(f"/users/{user_id}")

    def create_user(self, display_name: str, mail_nickname: str, upn: str,
                    password: str, force_change: bool = True) -> dict:
        """Create a new user."""
        data = {
            "accountEnabled": True,
            "displayName": display_name,
            "mailNickname": mail_nickname,
            "userPrincipalName": upn,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": force_change,
                "password": password
            }
        }
        return self._post("/users", data)

    def update_user(self, user_id: str, properties: dict) -> dict:
        """Update user properties."""
        return self._patch(f"/users/{user_id}", properties)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return self._delete(f"/users/{user_id}")

    def disable_user(self, user_id: str) -> dict:
        """Disable a user account."""
        return self._patch(f"/users/{user_id}", {"accountEnabled": False})

    def enable_user(self, user_id: str) -> dict:
        """Enable a user account."""
        return self._patch(f"/users/{user_id}", {"accountEnabled": True})

    def reset_user_password(self, user_id: str, new_password: str,
                            force_change: bool = True) -> dict:
        """Reset a user's password."""
        return self._patch(f"/users/{user_id}", {
            "passwordProfile": {
                "forceChangePasswordNextSignIn": force_change,
                "password": new_password
            }
        })

    # ============ Group Management ============

    def list_groups(self, top: int = 100) -> List[dict]:
        """List groups in the tenant."""
        result = self._get(f"/groups?$top={top}")
        return result.get("value", [])

    def get_group(self, group_id: str) -> dict:
        """Get a specific group."""
        return self._get(f"/groups/{group_id}")

    def create_group(self, display_name: str, mail_nickname: str,
                     description: str = "", security_enabled: bool = True,
                     mail_enabled: bool = False, group_types: List[str] = None) -> dict:
        """Create a new group."""
        data = {
            "displayName": display_name,
            "mailNickname": mail_nickname,
            "description": description,
            "securityEnabled": security_enabled,
            "mailEnabled": mail_enabled,
            "groupTypes": group_types or []
        }
        return self._post("/groups", data)

    def delete_group(self, group_id: str) -> bool:
        """Delete a group."""
        return self._delete(f"/groups/{group_id}")

    def get_group_members(self, group_id: str) -> List[dict]:
        """Get members of a group."""
        result = self._get(f"/groups/{group_id}/members")
        return result.get("value", [])

    def add_group_member(self, group_id: str, user_id: str) -> dict:
        """Add a user to a group."""
        data = {
            "@odata.id": f"https://graph.microsoft.com/v1.0/directoryObjects/{user_id}"
        }
        requests = _get_requests()
        url = f"{self.GRAPH_URL}/groups/{group_id}/members/$ref"
        response = requests.post(url, headers=self._headers(), json=data)
        if response.status_code == 204:
            return {"success": True}
        else:
            self._handle_error(response)

    def remove_group_member(self, group_id: str, user_id: str) -> bool:
        """Remove a user from a group."""
        return self._delete(f"/groups/{group_id}/members/{user_id}/$ref")

    # ============ License Management ============

    def list_subscribed_skus(self) -> List[dict]:
        """List available licenses/SKUs in the tenant."""
        result = self._get("/subscribedSkus")
        return result.get("value", [])

    def get_user_licenses(self, user_id: str) -> List[dict]:
        """Get licenses assigned to a user."""
        result = self._get(f"/users/{user_id}/licenseDetails")
        return result.get("value", [])

    def assign_license(self, user_id: str, sku_id: str,
                       disabled_plans: List[str] = None) -> dict:
        """Assign a license to a user."""
        data = {
            "addLicenses": [{
                "skuId": sku_id,
                "disabledPlans": disabled_plans or []
            }],
            "removeLicenses": []
        }
        return self._post(f"/users/{user_id}/assignLicense", data)

    def remove_license(self, user_id: str, sku_id: str) -> dict:
        """Remove a license from a user."""
        data = {
            "addLicenses": [],
            "removeLicenses": [sku_id]
        }
        return self._post(f"/users/{user_id}/assignLicense", data)

    # ============ Directory Roles ============

    def list_directory_roles(self) -> List[dict]:
        """List activated directory roles."""
        result = self._get("/directoryRoles")
        return result.get("value", [])

    def get_role_members(self, role_id: str) -> List[dict]:
        """Get members of a directory role."""
        result = self._get(f"/directoryRoles/{role_id}/members")
        return result.get("value", [])

    # ============ Applications ============

    def list_applications(self, top: int = 100) -> List[dict]:
        """List application registrations."""
        result = self._get(f"/applications?$top={top}")
        return result.get("value", [])

    def get_application(self, app_id: str) -> dict:
        """Get an application by ID."""
        return self._get(f"/applications/{app_id}")

    # ============ Service Principals ============

    def list_service_principals(self, top: int = 100) -> List[dict]:
        """List service principals."""
        result = self._get(f"/servicePrincipals?$top={top}")
        return result.get("value", [])

    # ============ Domains ============

    def list_domains(self) -> List[dict]:
        """List domains in the tenant."""
        result = self._get("/domains")
        return result.get("value", [])

    # ============ Organization ============

    def get_organization(self) -> dict:
        """Get organization/tenant details."""
        result = self._get("/organization")
        return result.get("value", [{}])[0]

    # ============ Sign-in Logs (requires Azure AD Premium) ============

    def get_signin_logs(self, top: int = 50) -> List[dict]:
        """Get recent sign-in logs (requires Azure AD Premium)."""
        result = self._get(f"/auditLogs/signIns?$top={top}", beta=True)
        return result.get("value", [])

    # ============ Conditional Access ============

    def list_conditional_access_policies(self) -> List[dict]:
        """List conditional access policies."""
        result = self._get("/identity/conditionalAccess/policies", beta=True)
        return result.get("value", [])


# Global realm instance
_current_realm: Optional[AzureRealm] = None


def get_current_realm() -> AzureRealm:
    """Get the current Azure realm or raise an error."""
    if _current_realm is None:
        raise AzureRealmError("Not connected to Azure. Use summon_azure_realm() first.")
    return _current_realm


# ============ Built-in Functions ============

def builtin_summon_azure_realm(interpreter, args: List[Any]) -> dict:
    """summon_azure_realm(tenant_id, client_id, client_secret) - Connect to Azure/M365."""
    global _current_realm
    if len(args) != 3:
        raise AzureRealmError("summon_azure_realm requires 3 arguments (tenant_id, client_id, client_secret)")

    tenant_id = str(args[0])
    client_id = str(args[1])
    client_secret = str(args[2])

    realm = AzureRealm(tenant_id, client_id, client_secret)
    realm.authenticate()
    _current_realm = realm

    return {"connected": True, "tenant_id": tenant_id}


def builtin_banish_azure_realm(interpreter, args: List[Any]) -> bool:
    """banish_azure_realm() - Disconnect from Azure/M365."""
    global _current_realm
    _current_realm = None
    return True


# ---- User Management ----

def builtin_divine_users(interpreter, args: List[Any]) -> List[dict]:
    """divine_users([top]) - List users in the tenant."""
    realm = get_current_realm()
    top = int(args[0]) if args else 100
    return realm.list_users(top=top)


def builtin_divine_user(interpreter, args: List[Any]) -> dict:
    """divine_user(user_id) - Get a specific user."""
    if len(args) != 1:
        raise AzureRealmError("divine_user requires 1 argument (user_id or UPN)")
    realm = get_current_realm()
    return realm.get_user(str(args[0]))


def builtin_conjure_user(interpreter, args: List[Any]) -> dict:
    """conjure_user(display_name, mail_nickname, upn, password) - Create a user."""
    if len(args) < 4:
        raise AzureRealmError("conjure_user requires 4 arguments (display_name, mail_nickname, upn, password)")
    realm = get_current_realm()
    return realm.create_user(
        display_name=str(args[0]),
        mail_nickname=str(args[1]),
        upn=str(args[2]),
        password=str(args[3]),
        force_change=args[4] if len(args) > 4 else True
    )


def builtin_transmute_user(interpreter, args: List[Any]) -> dict:
    """transmute_user(user_id, properties) - Update user properties."""
    if len(args) != 2:
        raise AzureRealmError("transmute_user requires 2 arguments (user_id, properties dict)")
    realm = get_current_realm()
    if not isinstance(args[1], dict):
        raise AzureRealmError("Second argument must be a grimoire (dict) of properties")
    return realm.update_user(str(args[0]), args[1])


def builtin_vanquish_user(interpreter, args: List[Any]) -> bool:
    """vanquish_user(user_id) - Delete a user."""
    if len(args) != 1:
        raise AzureRealmError("vanquish_user requires 1 argument (user_id)")
    realm = get_current_realm()
    return realm.delete_user(str(args[0]))


def builtin_silence_user(interpreter, args: List[Any]) -> dict:
    """silence_user(user_id) - Disable a user account."""
    if len(args) != 1:
        raise AzureRealmError("silence_user requires 1 argument (user_id)")
    realm = get_current_realm()
    return realm.disable_user(str(args[0]))


def builtin_awaken_user(interpreter, args: List[Any]) -> dict:
    """awaken_user(user_id) - Enable a user account."""
    if len(args) != 1:
        raise AzureRealmError("awaken_user requires 1 argument (user_id)")
    realm = get_current_realm()
    return realm.enable_user(str(args[0]))


def builtin_reset_user_ward(interpreter, args: List[Any]) -> dict:
    """reset_user_ward(user_id, new_password) - Reset a user's password."""
    if len(args) < 2:
        raise AzureRealmError("reset_user_ward requires 2 arguments (user_id, new_password)")
    realm = get_current_realm()
    force_change = args[2] if len(args) > 2 else True
    return realm.reset_user_password(str(args[0]), str(args[1]), force_change)


# ---- Group Management ----

def builtin_divine_groups(interpreter, args: List[Any]) -> List[dict]:
    """divine_groups([top]) - List groups in the tenant."""
    realm = get_current_realm()
    top = int(args[0]) if args else 100
    return realm.list_groups(top=top)


def builtin_divine_group(interpreter, args: List[Any]) -> dict:
    """divine_group(group_id) - Get a specific group."""
    if len(args) != 1:
        raise AzureRealmError("divine_group requires 1 argument (group_id)")
    realm = get_current_realm()
    return realm.get_group(str(args[0]))


def builtin_conjure_group(interpreter, args: List[Any]) -> dict:
    """conjure_group(display_name, mail_nickname, [description]) - Create a security group."""
    if len(args) < 2:
        raise AzureRealmError("conjure_group requires at least 2 arguments (display_name, mail_nickname)")
    realm = get_current_realm()
    description = str(args[2]) if len(args) > 2 else ""
    return realm.create_group(
        display_name=str(args[0]),
        mail_nickname=str(args[1]),
        description=description
    )


def builtin_vanquish_group(interpreter, args: List[Any]) -> bool:
    """vanquish_group(group_id) - Delete a group."""
    if len(args) != 1:
        raise AzureRealmError("vanquish_group requires 1 argument (group_id)")
    realm = get_current_realm()
    return realm.delete_group(str(args[0]))


def builtin_divine_group_members(interpreter, args: List[Any]) -> List[dict]:
    """divine_group_members(group_id) - Get members of a group."""
    if len(args) != 1:
        raise AzureRealmError("divine_group_members requires 1 argument (group_id)")
    realm = get_current_realm()
    return realm.get_group_members(str(args[0]))


def builtin_bind_to_group(interpreter, args: List[Any]) -> dict:
    """bind_to_group(group_id, user_id) - Add a user to a group."""
    if len(args) != 2:
        raise AzureRealmError("bind_to_group requires 2 arguments (group_id, user_id)")
    realm = get_current_realm()
    return realm.add_group_member(str(args[0]), str(args[1]))


def builtin_unbind_from_group(interpreter, args: List[Any]) -> bool:
    """unbind_from_group(group_id, user_id) - Remove a user from a group."""
    if len(args) != 2:
        raise AzureRealmError("unbind_from_group requires 2 arguments (group_id, user_id)")
    realm = get_current_realm()
    return realm.remove_group_member(str(args[0]), str(args[1]))


# ---- License Management ----

def builtin_divine_licenses(interpreter, args: List[Any]) -> List[dict]:
    """divine_licenses() - List available licenses in the tenant."""
    realm = get_current_realm()
    return realm.list_subscribed_skus()


def builtin_divine_user_licenses(interpreter, args: List[Any]) -> List[dict]:
    """divine_user_licenses(user_id) - Get licenses assigned to a user."""
    if len(args) != 1:
        raise AzureRealmError("divine_user_licenses requires 1 argument (user_id)")
    realm = get_current_realm()
    return realm.get_user_licenses(str(args[0]))


def builtin_bestow_license(interpreter, args: List[Any]) -> dict:
    """bestow_license(user_id, sku_id) - Assign a license to a user."""
    if len(args) < 2:
        raise AzureRealmError("bestow_license requires 2 arguments (user_id, sku_id)")
    realm = get_current_realm()
    disabled_plans = args[2] if len(args) > 2 else None
    return realm.assign_license(str(args[0]), str(args[1]), disabled_plans)


def builtin_revoke_license(interpreter, args: List[Any]) -> dict:
    """revoke_license(user_id, sku_id) - Remove a license from a user."""
    if len(args) != 2:
        raise AzureRealmError("revoke_license requires 2 arguments (user_id, sku_id)")
    realm = get_current_realm()
    return realm.remove_license(str(args[0]), str(args[1]))


# ---- Directory & Organization ----

def builtin_divine_roles(interpreter, args: List[Any]) -> List[dict]:
    """divine_roles() - List directory roles."""
    realm = get_current_realm()
    return realm.list_directory_roles()


def builtin_divine_role_members(interpreter, args: List[Any]) -> List[dict]:
    """divine_role_members(role_id) - Get members of a directory role."""
    if len(args) != 1:
        raise AzureRealmError("divine_role_members requires 1 argument (role_id)")
    realm = get_current_realm()
    return realm.get_role_members(str(args[0]))


def builtin_divine_domains(interpreter, args: List[Any]) -> List[dict]:
    """divine_domains() - List domains in the tenant."""
    realm = get_current_realm()
    return realm.list_domains()


def builtin_divine_organization(interpreter, args: List[Any]) -> dict:
    """divine_organization() - Get organization/tenant details."""
    realm = get_current_realm()
    return realm.get_organization()


def builtin_divine_apps(interpreter, args: List[Any]) -> List[dict]:
    """divine_apps([top]) - List application registrations."""
    realm = get_current_realm()
    top = int(args[0]) if args else 100
    return realm.list_applications(top=top)


def builtin_divine_service_principals(interpreter, args: List[Any]) -> List[dict]:
    """divine_service_principals([top]) - List service principals."""
    realm = get_current_realm()
    top = int(args[0]) if args else 100
    return realm.list_service_principals(top=top)


# ---- Security & Audit ----

def builtin_divine_signin_logs(interpreter, args: List[Any]) -> List[dict]:
    """divine_signin_logs([top]) - Get recent sign-in logs (requires Azure AD Premium)."""
    realm = get_current_realm()
    top = int(args[0]) if args else 50
    return realm.get_signin_logs(top=top)


def builtin_divine_conditional_policies(interpreter, args: List[Any]) -> List[dict]:
    """divine_conditional_policies() - List conditional access policies."""
    realm = get_current_realm()
    return realm.list_conditional_access_policies()


# ============ Register All M365 Built-ins ============

def register_m365_builtins(environment):
    """Register all M365/Entra built-in functions."""
    builtins = [
        # Connection
        ("summon_azure_realm", builtin_summon_azure_realm, 3),
        ("banish_azure_realm", builtin_banish_azure_realm, 0),

        # User Management
        ("divine_users", builtin_divine_users, -1),
        ("divine_user", builtin_divine_user, 1),
        ("conjure_user", builtin_conjure_user, -1),
        ("transmute_user", builtin_transmute_user, 2),
        ("vanquish_user", builtin_vanquish_user, 1),
        ("silence_user", builtin_silence_user, 1),
        ("awaken_user", builtin_awaken_user, 1),
        ("reset_user_ward", builtin_reset_user_ward, -1),

        # Group Management
        ("divine_groups", builtin_divine_groups, -1),
        ("divine_group", builtin_divine_group, 1),
        ("conjure_group", builtin_conjure_group, -1),
        ("vanquish_group", builtin_vanquish_group, 1),
        ("divine_group_members", builtin_divine_group_members, 1),
        ("bind_to_group", builtin_bind_to_group, 2),
        ("unbind_from_group", builtin_unbind_from_group, 2),

        # License Management
        ("divine_licenses", builtin_divine_licenses, 0),
        ("divine_user_licenses", builtin_divine_user_licenses, 1),
        ("bestow_license", builtin_bestow_license, -1),
        ("revoke_license", builtin_revoke_license, 2),

        # Directory & Organization
        ("divine_roles", builtin_divine_roles, 0),
        ("divine_role_members", builtin_divine_role_members, 1),
        ("divine_domains", builtin_divine_domains, 0),
        ("divine_organization", builtin_divine_organization, 0),
        ("divine_apps", builtin_divine_apps, -1),
        ("divine_service_principals", builtin_divine_service_principals, -1),

        # Security & Audit
        ("divine_signin_logs", builtin_divine_signin_logs, -1),
        ("divine_conditional_policies", builtin_divine_conditional_policies, 0),
    ]

    for name, func, arity in builtins:
        environment.define(name, BuiltinFunction(name, func, arity))
