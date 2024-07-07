# stdlib

# third party

# relative
from ...serde.serializable import serializable
from ...store.db.db import DBManager
from ...store.db.stash import ObjectStash
from ...store.document_store import PartitionSettings
from ...types.uid import UID
from ..context import AuthedServiceContext
from ..response import SyftSuccess
from ..service import AbstractService
from ..service import TYPE_TO_SERVICE
from ..service import service_method
from ..user.user_roles import ADMIN_ROLE_LEVEL
from ..user.user_roles import GUEST_ROLE_LEVEL
from .user_code import UserCodeStatusCollection


@serializable(canonical_name="StatusSQLStash", version=1)
class StatusStash(ObjectStash[UserCodeStatusCollection]):
    settings: PartitionSettings = PartitionSettings(
        name=UserCodeStatusCollection.__canonical_name__,
        object_type=UserCodeStatusCollection,
    )


@serializable(canonical_name="UserCodeStatusService", version=1)
class UserCodeStatusService(AbstractService):
    stash: StatusStash

    def __init__(self, store: DBManager):
        self.stash = StatusStash(store=store)

    @service_method(path="code_status.create", name="create", roles=ADMIN_ROLE_LEVEL)
    def create(
        self,
        context: AuthedServiceContext,
        status: UserCodeStatusCollection,
    ) -> UserCodeStatusCollection:
        return self.stash.set(
            credentials=context.credentials,
            obj=status,
        ).unwrap()

    @service_method(
        path="code_status.get_by_uid", name="get_by_uid", roles=GUEST_ROLE_LEVEL
    )
    def get_status(
        self, context: AuthedServiceContext, uid: UID
    ) -> UserCodeStatusCollection:
        """Get the status of a user code item"""
        return self.stash.get_by_uid(context.credentials, uid=uid).unwrap()

    @service_method(path="code_status.get_all", name="get_all", roles=ADMIN_ROLE_LEVEL)
    def get_all(self, context: AuthedServiceContext) -> list[UserCodeStatusCollection]:
        """Get all user code item statuses"""
        return self.stash.get_all(context.credentials).unwrap()

    @service_method(
        path="code_status.remove",
        name="remove",
        roles=ADMIN_ROLE_LEVEL,
        unwrap_on_success=False,
    )
    def remove(self, context: AuthedServiceContext, uid: UID) -> SyftSuccess:
        """Remove a user code item status"""
        self.stash.delete_by_uid(context.credentials, uid=uid).unwrap()
        return SyftSuccess(message=f"{uid} successfully deleted", value=uid)


TYPE_TO_SERVICE[UserCodeStatusCollection] = UserCodeStatusService