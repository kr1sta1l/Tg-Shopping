class User:
    def __init__(self, user_id: int, status: str, language: str, is_admin: bool):
        self.tg_id: int = user_id
        self.status: str = status
        self.language: str = language
        self.is_admin: bool = is_admin
