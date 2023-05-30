from auth_app.services import AccountService


class AccountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.account = None
        if account_id := request.headers.get("Account-ID"):
            account = AccountService.get_account_by_id(account_id)
            request.account = account
        response = self.get_response(request)
        return response
