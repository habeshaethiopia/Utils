from msal import ConfidentialClientApplication
from office365.sharepoint.client_context import ClientContext

def list_sharepoint_libraries(client_id, client_secret, authority, site_url):
    """
    Authenticate with SharePoint using MSAL and list available document libraries.

    Args:
        client_id (str): Azure AD Application (Client) ID.
        client_secret (str): Azure AD Application Client Secret.
        authority (str): Azure AD authority URL (e.g., "https://login.microsoftonline.com/tenant-id").
        site_url (str): SharePoint site URL.

    Returns:
        list: A list of document library names if successful, otherwise None.
    """
    try:
        # Initialize MSAL application
        app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=authority
        )

        # Acquire token for client
        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" not in result:
            raise Exception(f"Failed to authenticate: {result.get('error_description')}")

        token = result["access_token"]
        print("Authentication successful")

        # Use the token to authenticate with SharePoint
        ctx = ClientContext(site_url).with_access_token(token)

        # Fetch available document libraries
        web = ctx.web
        ctx.load(web.lists)
        ctx.execute_query()

        libraries = [lib.properties["Title"] for lib in web.lists if lib.properties.get("BaseTemplate") == 101]  # 101 is for document libraries
        return libraries

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Usage example
CLIENT_ID = "your-client-id"
CLIENT_SECRET = "your-client-secret"
AUTHORITY = "https://login.microsoftonline.com/your-tenant-id"
SHAREPOINT_SITE_URL = "https://yourtenant.sharepoint.com/sites/yoursite"

libraries = list_sharepoint_libraries(CLIENT_ID, CLIENT_SECRET, AUTHORITY, SHAREPOINT_SITE_URL)
if libraries is not None:
    print("Available Document Libraries:")
    for library in libraries:
        print(f"- {library}")
else:
    print("Failed to retrieve libraries.")
