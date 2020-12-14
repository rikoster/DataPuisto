"""
Strava settings for DataPuisto project.

"""
from datetime import datetime
from django.utils import timezone


AUTHORIZE_URL = 'https://www.strava.com/oauth/authorize'
TOKEN_URL = 'https://www.strava.com/oauth/token'
# BASE_URL = 'https://www.strava.com/api/v3'
ACTIVITIES_URL = 'https://www.strava.com/api/v3/athlete/activities'

CLIENT_ID = 30046
CLIENT_SECRET = 'c9e244080fa8b2e2044f004ffdcf06add74e6061'

ACCESS_SCOPE = 'activity:read'
EARLIEST_TO_UPDATE = timezone.make_aware(datetime(year=2018, month=1, day=1))
TIMESTAMP_EARLIEST = EARLIEST_TO_UPDATE.timestamp()