### 内置接口列表

1. self.create_business [done]
```
实际调用
{
    "data": {
        "bk_biz_name": "cc_create_app_test",
        "bk_biz_maintainer": "admin",
        "time_zone": "Asia/Shanghai",
        "bk_supplier_id": "0",
        "language": "1"
    }
}
API文档示例
{
    "bk_app_code": "esb_test",
    "bk_app_secret": "xxx",
    "bk_token": "xxx",
    "bk_supplier_account": "123456789",
    "data": {
        "bk_biz_name": "cc_app_test",
        "bk_biz_maintainer": "admin",
        "bk_biz_productor": "admin",
        "bk_biz_developer": "admin",
        "bk_biz_tester": "admin",
        "time_zone": "Asia/Shanghai"
    }
}
```



2. self.delete_business [done]
3. self.delete_host [todo 不好测试]
4. self.get_host_base_info [done]
5. self.search_biz_inst_topo [done]
6. self.search_business [done]
7. self.search_custom_query [done]
8. self.search_host [deleted]
9. self.search_inst [done]
```
添加了fields查询参数后报错
{
    "bk_obj_id":"biz",
    "bk_supplier_account":"0",
    "page":{
        "start":0,
        "limit":10,
        "sort":"bk_inst_id"
    },
    "fields":"bk_biz_id",
    "condition": {
        "biz":[
            {
                "field":"bk_biz_name",
                "operator":"$eq",
                "value":"cc_app_1"
            }
        ]
    }
}
{
    "message": "查询实例数据失败%!(EXTRA string=json: cannot unmarshal string into Go struct field AssociationParams.fields of type map[string][]string)",
    "code": "OK",
    "data": [],
    "result": false,
    "msg": "查询实例数据失败%!(EXTRA string=json: cannot unmarshal string into Go struct field AssociationParams.fields of type map[string][]string)"
}
```
10. self.search_inst_by_object
11. self.transfer_host_module
12. self.transfer_host_to_faultmodule
13. self.transfer_host_to_idlemodule
14. self.transfer_host_to_resourcemodule
15. self.update_business
16. self.update_host
17. self.add_plat_id
18. self.search_object_attribute
19. self.search_inst_association_topo

以下接口使用方法及场景
> 1. self.create_module
> 2. self.create_set
> 3. self.delete_module
> 4. self.delete_set
> 5. self.search_module
> 6. self.search_set
> 7. self.update_module
> 8. self.update_set
