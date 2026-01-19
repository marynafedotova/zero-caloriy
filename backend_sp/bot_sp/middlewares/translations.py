from typing import Optional
from asgiref.sync import sync_to_async
from aiogram_i18n.managers import BaseManager
from aiogram.types import User as TeleUser

from users.models import User

class TgUserManager(BaseManager):
    async def get_locale(self, event_from_user: Optional[TeleUser]):
        if not event_from_user:
         return self.default_locale
        
        user = await sync_to_async(
           lambda: User.objects.filter(user_id=event_from_user.id).first()
        )()

        if user and user.language:
           return user.language
        
        return event_from_user.language_code or self.default_locale
    
    
    async def set_locale(self, locale: str, event_from_user: Optional[TeleUser] = None) -> None:
        """Цей метод автоматично оновить БД, коли ви зміните мову в боті"""
        if not event_from_user:
            return

        await sync_to_async(
            lambda: User.objects.update_or_create(
                user_id=event_from_user.id,
                defaults={'language': locale}
            )
        )()
        