import requests
import singer
from datetime import datetime

LOGGER = singer.get_logger()

class SharepointError(Exception):
    pass

class BadRequest(SharepointError):
    pass

class InvalidAuthenticationToken(SharepointError):
    pass

class Forbidden(SharepointError):
    pass

class NotFound(SharepointError):
    pass

class Conflict(SharepointError):
    pass

class InternalServiceError(SharepointError):
    pass

ERROR_CODE_EXCEPTION_MAPPING = {
    400: BadRequest,
    401: InvalidAuthenticationToken,
    403: Forbidden,
    404: NotFound,
    409: Conflict,
    500: InternalServiceError}

def get_exception_for_error_code(status_code):
    return ERROR_CODE_EXCEPTION_MAPPING.get(status_code, SharepointError)

def raise_for_error(response):
    try:
        response.raise_for_status()
    except (requests.HTTPError, requests.ConnectionError) as error:
        try:
            content_length = len(response.content)
            if content_length == 0:
                return
            response_json = response.json()
            status_code = response.status_code
            message = 'RESPONSE: {}'.format(response_json)
            ex = get_exception_for_error_code(status_code)
            raise ex(message)
        except (ValueError, TypeError):
            raise SharepointError(error)

class SharePointClient:
    def __init__(self, config):
        self.tenant_name = config['tenant_name']
        self.client_id = config['client_id']
        self.client_secret = config['client_secret']
        self.grant_type = config['grant_type']
        self.scope = config['scope']

        self.token_url = "https://login.microsoftonline.com/{}/oauth2/v2.0/token".format(self.tenant_name)
        self.token_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": self.grant_type,
            "scope": self.scope
        }
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.session = requests.Session()
        self.logger = singer.get_logger()
        self.access_token = self.get_access_token()
        self.headers = {"content-type": "application/json", "Authorization": "Bearer " + self.access_token}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def get_access_token(self):
        response = self.session.post(self.token_url, data=self.token_data)
        if response.status_code != 200:
            LOGGER.error('Error status_code = {}'.format(response.status_code))
            raise_for_error(response)
        else:
            self.access_token = response.json()["access_token"]
            self.headers = {"content-type": "application/json", "Authorization": "Bearer " + self.access_token}
            return self.access_token

    def renew_access_token(self):
        self.access_token = self.get_access_token()
        self.headers = {"content-type": "application/json", "Authorization": "Bearer " + self.access_token}

    def get_site_id(self, siteName):
        url = self.base_url + "/sites"
        success = False
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                LOGGER.error('Connection Error. Trying to reconnect.')
                self.renew_access_token()
            else:
                if response.status_code != 200:
                    LOGGER.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renew_access_token()
                    # raise_for_error(response)
                else:
                    success = True
                    values = response.json()["value"]
                    for value in values:
                        if siteName == value["name"]:
                            return value["id"]
                    raise Exception("Coundn't find specified '{}' site in sharepoint".format(siteName))

    def get_drive_id(self, siteId, documentLibrary):
        url = self.base_url + "/sites/" + siteId + "/drives"
        success = False
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                LOGGER.error('Connection Error. Trying to reconnect.')
                self.renew_access_token()
            else:
                if response.status_code != 200:
                    LOGGER.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renew_access_token()
                    # raise_for_error(response)
                else:
                    success = True
                    values = response.json()["value"]
                    for value in values:
                        if documentLibrary == value["name"]:
                            return value["id"]
                    raise Exception("Coundn't find specified '{}' documentLibrary in sharepoint for site '{}'".format(documentLibrary, siteId))

    def get_drive_download_url(self, siteId, driveId, fileName, lastUpdatedDate=False):
        url = self.base_url + "/sites/" + siteId + "/drives/" + driveId + "/root/children"
        success = False
        while not success:
            try:
                response = self.session.get(url, headers=self.headers)
            except:
                LOGGER.error('Connection Error. Trying to reconnect.')
                self.renew_access_token()
            else:
                if response.status_code != 200:
                    LOGGER.error('Error status_code = {}. Trying to renew access token.'.format(response.status_code))
                    self.renew_access_token()
                    # raise_for_error(response)
                else:
                    success = True
                    fileExist = False
                    values = response.json()["value"]
                    for value in values:
                        if fileName == value["name"]:
                            fileExist = True
                            if lastUpdatedDate:
                                if lastUpdatedDate < datetime.strptime(value["lastModifiedDateTime"], "%Y-%m-%dT%H:%M:%SZ"):
                                    drive_download_url = value["@microsoft.graph.downloadUrl"]
                                    return drive_download_url
                            else:
                                drive_download_url = value["@microsoft.graph.downloadUrl"]
                                return drive_download_url
                    if not fileExist:
                        raise Exception(
                            "Coundn't find specified '{}' file for drive {} of site '{}' in sharepoint".format(fileName, driveId, siteId))
                    return False