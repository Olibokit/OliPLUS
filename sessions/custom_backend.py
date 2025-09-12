import logging

from asgiref.sync import sync_to_async
from django.contrib.sessions.backends.base import CreateError, SessionBase, UpdateError
from django.core.exceptions import SuspiciousOperation
from django.db import DatabaseError, IntegrityError, router, transaction
from django.utils import timezone
from django.utils.functional import cached_property


class SessionStore(SessionBase):
    """
    Backend personnalisé pour la gestion des sessions Django en base de données,
    avec support synchrone et asynchrone.
    """

    def __init__(self, session_key=None):
        super().__init__(session_key)

    @classmethod
    def get_model_class(cls):
        from django.contrib.sessions.models import Session
        return Session

    @cached_property
    def model(self):
        return self.get_model_class()

    def _handle_suspicious(self, e):
        if isinstance(e, SuspiciousOperation):
            logger = logging.getLogger(f"django.security.{e.__class__.__name__}")
            logger.warning(str(e))
        self._session_key = None

    def _get_session_from_db(self):
        try:
            return self.model.objects.get(
                session_key=self.session_key, expire_date__gt=timezone.now()
            )
        except (self.model.DoesNotExist, SuspiciousOperation) as e:
            self._handle_suspicious(e)

    async def _aget_session_from_db(self):
        try:
            return await self.model.objects.aget(
                session_key=self.session_key, expire_date__gt=timezone.now()
            )
        except (self.model.DoesNotExist, SuspiciousOperation) as e:
            self._handle_suspicious(e)

    def load(self):
        session = self._get_session_from_db()
        return self.decode(session.session_data) if session else {}

    async def aload(self):
        session = await self._aget_session_from_db()
        return self.decode(session.session_data) if session else {}

    def exists(self, session_key):
        return self.model.objects.filter(session_key=session_key).exists()

    async def aexists(self, session_key):
        return await self.model.objects.filter(session_key=session_key).aexists()

    def create_model_instance(self, data):
        return self.model(
            session_key=self._get_or_create_session_key(),
            session_data=self.encode(data),
            expire_date=self.get_expiry_date(),
        )

    async def acreate_model_instance(self, data):
        return self.model(
            session_key=await self._aget_or_create_session_key(),
            session_data=self.encode(data),
            expire_date=await self.aget_expiry_date(),
        )

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    async def acreate(self):
        while True:
            self._session_key = await self._aget_new_session_key()
            try:
                await self.asave(must_create=True)
            except CreateError:
                continue
            self.modified = True
            return

    def save(self, must_create=False):
        if self.session_key is None:
            return self.create()
        data = self._get_session(no_load=must_create)
        obj = self.create_model_instance(data)
        using = router.db_for_write(self.model, instance=obj)
        try:
            with transaction.atomic(using=using):
                obj.save(
                    force_insert=must_create,
                    force_update=not must_create,
                    using=using,
                )
        except IntegrityError:
            if must_create:
                raise CreateError
            raise
        except DatabaseError:
            if not must_create:
                raise UpdateError
            raise

    async def asave(self, must_create=False):
        if self.session_key is None:
            return await self.acreate()
        data = await self._aget_session(no_load=must_create)
        obj = await self.acreate_model_instance(data)
        using = router.db_for_write(self.model, instance=obj)

        @sync_to_async
        def sync_transaction():
            with transaction.atomic(using=using):
                obj.save(
                    force_insert=must_create,
                    force_update=not must_create,
                    using=using,
                )

        try:
            await sync_transaction()
        except IntegrityError:
            if must_create:
                raise CreateError
            raise
        except DatabaseError:
            if not must_create:
                raise UpdateError
            raise

    def delete(self, session_key=None):
        session_key = session_key or self.session_key
        if not session_key:
            return
        try:
            self.model.objects.get(session_key=session_key).delete()
        except self.model.DoesNotExist:
            pass

    async def adelete(self, session_key=None):
        session_key = session_key or self.session_key
        if not session_key:
            return
        try:
            obj = await self.model.objects.aget(session_key=session_key)
            await obj.adelete()
        except self.model.DoesNotExist:
            pass

    @classmethod
    def clear_expired(cls):
        cls.get_model_class().objects.filter(expire_date__lt=timezone.now()).delete()

    @classmethod
    async def aclear_expired(cls):
        await cls.get_model_class().objects.filter(
            expire_date__lt=timezone.now()
        ).adelete()
