from rest_framework.authentication import (
    TokenAuthentication as RestapiTokenAuthentication)


class TokenAuthentication(RestapiTokenAuthentication):
    keyword = 'Bearer'