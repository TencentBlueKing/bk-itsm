## 接口自测

https://gist.github.com/subfuzion/08c5d85437d5d4f00e58

### get_services
curl -X GET https://{{host}}/api/c/compapi/v2/itsm/get_services/?bk_app_code=bk_itsm&bk_app_secret=ca5abdd4-5641-4799-aed7-422a374b8008&bk_username=admin | python -m json.tool

### get_service_catalogs
curl -X GET https://{{host}}/api/c/compapi/v2/itsm/get_service_catalogs/?&bk_app_code=bk_itsm&bk_app_secret=ca5abdd4-5641-4799-aed7-422a374b8008&bk_username=admin | python -m json.tool

### get_service_detail
curl -X GET https://{{host}}/api/c/compapi/v2/itsm/get_service_detail/?service_id=2&bk_app_code=bk_itsm&bk_app_secret=ca5abdd4-5641-4799-aed7-422a374b8008&bk_username=admin | python -m json.tool

### create_ticket
curl -X POST -H "Content-Type: application/json"  -d @data.json  https://{{host}}/api/c/compapi/v2/itsm/create_ticket/ | python -m json.tool

### get_ticket_info
curl -X GET https://{{host}}/api/c/compapi/v2/itsm/get_ticket_info/?sn=NO2019092715461354&bk_app_code=bk_itsm&bk_app_secret=ca5abdd4-5641-4799-aed7-422a374b8008&bk_username=admin | python -m json.tool

### get_ticket_logs
curl -X GET https://{{host}}/api/c/compapi/v2/itsm/get_ticket_logs/?sn=NO2019092715461354&bk_app_code=bk_itsm&bk_app_secret=ca5abdd4-5641-4799-aed7-422a374b8008&bk_username=admin | python -m json.tool

### get_ticket_status
curl -X GET https://{{host}}/api/c/compapi/v2/itsm/get_ticket_status/?sn=NO2019092715461354&bk_app_code=bk_itsm&bk_app_secret=ca5abdd4-5641-4799-aed7-422a374b8008&bk_username=admin | python -m json.tool
