from requests_oauthlib import OAuth2Session
from NavigantAnalyzer.common import get_fromtimestamp, get_strava_date
from StravaAnalyzer.stravasettings import CLIENT_ID, CLIENT_SECRET, TOKEN_URL, ACTIVITIES_URL, TIMESTAMP_EARLIEST
from StravaAnalyzer.models import Athlete, Token, Activity
from django.utils import timezone
from datetime import datetime, timedelta

import logging

logger = logging.getLogger(__name__)

#
# -------------------------------------------------------------------
#
# Main functions for key view implementation
#
# -------------------------------------------------------------------

def update_or_create_athlete(code):
    # Documented here: https://developers.strava.com/docs/authentication/
    session = OAuth2Session(client_id=CLIENT_ID)
    
    # These four parameters are set according to the Strava specification
    # (see the link above)
    fetch_token_payload = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
            }
    try:
        r = session.post(TOKEN_URL, data=fetch_token_payload)
    except:
        # come up with something later
        pass
    
    data = r.json()
    
    a_obj = None

    if 'athlete' in data: # Success
        a_obj = update_or_create_athlete_from_strava(data['athlete'])
        t_obj = update_or_create_token_from_strava(data)
        
        a_obj.token = t_obj
        a_obj.save()

    return a_obj

#
# -------------------------------------------------------------------
#
# Fetching activities, after athlete creation (or every night)
#
# -------------------------------------------------------------------

def fetch_all_activities():
    logger.info("--- fetch_all_activities() starts ---")
    for athlete in Athlete.objects.all():
        
        # ---- additional codelines start ---- 2019-04-26
        # These lines were added to prevent double fetching of
        # activities, which happened probably for HTML reasons.
        #
        dt_now = timezone.now()
        dt_then = athlete.activities_fetched
        if dt_now - dt_then > timedelta(minutes=1):
            athlete.activities_fetched = dt_now
            athlete.save()
            # ---- additional codelines end ----
            #
            logger.info("--- Iteration for athlete {}---".format(athlete.id))
            activity_list = fetch_athlete_activities(athlete)
            for activity in activity_list:
                update_or_create_activity_from_strava(activity)

def fetch_athlete_activities(athlete):
    activities = list()
    strava_token = athlete.token.get_strava_token()
    strava_session_extra = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
        }
    session = OAuth2Session(
            client_id=CLIENT_ID,
            token=strava_token,
            auto_refresh_url=TOKEN_URL,
            auto_refresh_kwargs=strava_session_extra, 
            token_updater=update_or_create_token_from_strava ### a function
            )
    page = 1
    while page <= 20: # 20 is a lot
        params = {
                'page': page,
                'per_page': 100,
                'after': TIMESTAMP_EARLIEST
                }
        try:
            r = session.get(ACTIVITIES_URL, params=params)
            logger.info("--- Fetching activities, page {}".format(page))
            if len(r.json()) == 0:
                break
            activities.extend(r.json())
            page += 1
        except:
            logger.info("--- EXCEPTION, returning {} activities".format(
                len(activities)))
            return activities

    logger.info("--- Returning {} activities".format(len(activities)))
    return activities

#
# -------------------------------------------------------------------
#
# Updating or creating model objects from Strava
#
# -------------------------------------------------------------------

def update_or_create_token_from_strava(strava_dict):
    token = Token()
    for key, value in strava_dict.items():
        if key == 'expires_at':
            # translate a timestamp to a Django datetime
            token.expires_at = get_fromtimestamp(value)
        # all items shall be copied, save 'athlete'
        elif hasattr(token, key):
            setattr(token, key, value)
    token.save()
    return token

def update_or_create_athlete_from_strava(strava_dict):
    athlete = Athlete()
    for key, value in strava_dict.items():
        if hasattr(athlete, key):
            setattr(athlete, key, value)
    athlete.save()
    return athlete

def update_or_create_activity_from_strava(strava_dict):
    activity = Activity()
    for key, value in strava_dict.items():
        if key == 'athlete':
            activity.athlete = Athlete.objects.get(id=value['id'])
        elif key == 'end_latlng':
            if not value is None:
                activity.end_latitude = value[0]
                activity.end_longitude = value[1]
        elif key == 'timezone':
            #Only the last part of strava tz string
            activity.timezone = value.split(" ")[-1]
        elif key == 'start_date':
            activity.start_date = get_strava_date(
                                    strava_dict['start_date_local'],
                                    strava_dict['timezone']
                                    )
        #Most fields handled by this
        elif hasattr(activity, key):
            setattr(activity, key, value)

    activity.save()
    return activity
