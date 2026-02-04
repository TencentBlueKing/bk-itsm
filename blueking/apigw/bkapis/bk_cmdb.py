from bkapi_client_core.base import Operation
from bkapi_client_core.django_helper import _get_client_by_settings
from bkapi_client_core.django_helper import get_client_by_request as _get_client_by_request
from bkapi_client_core.django_helper import get_client_by_username as _get_client_by_username
from bkapi_client_core.property import bind_property
from bkapi_client_core.utils import generic_type_partial as _partial

from blueking.apigw.base import ApiProtocol, TenantBaseClient
from blueking.apigw.utils import get_endpoint


class Client(TenantBaseClient):
    search_business = bind_property(
        Operation,
        name="search_business",
        method="POST",
        path="api/v3/open/biz/search/{bk_supplier_account}",
    )

    search_inst_association_topo = bind_property(
        Operation,
        name="search_inst_association_topo",
        method="POST",
        path="api/v3/open/inst/association/topo/{bk_obj_id}/{bk_inst_id}",
    )

    search_object_attribute = bind_property(
        Operation,
        name="search_object_attribute",
        method="POST",
        path="api/v3/open/find/objectattr",
    )
    
    search_inst = bind_property(
        Operation,
        name="search_inst",
        method="POST",
        path="api/v3/open/find/instassociation/object/{bk_obj_id}",
    )

    
class CMDBApi(ApiProtocol):
    _api_name = "bk-cmdb"

    @classmethod
    def get_client(cls) -> Client:
        return _get_client_by_settings(Client, endpoint=get_endpoint(cls._api_name, "prod"))

    @classmethod
    def get_client_by_request(cls, request):
        return (_partial(Client, _get_client_by_request)
                (request, endpoint=get_endpoint(cls._api_name, "prod")))

    @classmethod
    def get_client_by_username(cls, username):
        return (_partial(Client, _get_client_by_username)
                (username, endpoint=get_endpoint(cls._api_name, "prod")))
