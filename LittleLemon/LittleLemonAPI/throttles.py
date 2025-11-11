from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class TenCallsPerMinuteUserThrottle(UserRateThrottle):
    scope = 'ten' #This scope is put in the settings.py file