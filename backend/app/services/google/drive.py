from googleapiclient.discovery import build

from .auth import get_credentials


def create_folder(folder_name: str) -> str:
    """
    Creates a folder in the authenticated user's Google Drive.

    Returns:
        Folder URL
    """

    service = build(
        "drive",
        "v3",
        credentials=get_credentials(),
    )

    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
    }

    folder = (
        service.files()
        .create(
            body=metadata,
            fields="id, webViewLink",
        )
        .execute()
    )

    return folder["webViewLink"]