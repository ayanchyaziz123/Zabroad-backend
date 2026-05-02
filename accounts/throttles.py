from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


class OTPSendRateThrottle(AnonRateThrottle):
    scope = 'otp_send'
