
import pytest

# path error
async def test_index_view(client):
    resp = await client[0].get('/')
    assert resp.status == 404

# swagger
async def test_swagger(client):
    resp = await client[0].get('/+-template-+/swagger')
    assert resp.status == 200

# GET "get_req, http_rc, expected"
get_testdata = [
    #happy path
    ('/+-template-+/v1/dsfgg43435/system1?inp1=20200101&inp2=1&inp3=1', 200,
     {'method': '+-template-+',
      'message_idt': 'dsfgg43435',
      'source_system': 'system1',
      'rc': 200, 'message': 'Success',
      'input_parms': {'inp1': '20200101', 'inp2': '1', 'inp3': '1'},
      'records': [{'PARM1': 'Hello1', 'PARM2': 'World1'},
                  {'PARM1': 'Hello2', 'PARM2': 'World2'},
                  {'PARM1': 'Hello3', 'PARM2': 'World3'},
                  {'PARM1': '1', 'PARM2': 'World3'}]}
     ),
    # test_get_assertion_system
    ('/+-template-+/v1/dghsew4qq345y/system_99?inp1=20200101&inp2=1&inp3=1', 412,
     {'method': '+-template-+',
      'message_idt': 'dghsew4qq345y',
      'source_system': 'system_99',
      'rc': 412, 'message': 'Inward parameter source_system does not in allowed list',
      'input_parms': {'inp1': '20200101', 'inp2': '1', 'inp3': '1'},
      'records': []}
     ),
    #test_get_assertion_date
    ('/+-template-+/v1/dfhjdf-sd53-456/system1?inp1=20202525&inp2=1&inp3=1', 412,
     {'method': '+-template-+',
      'message_idt': 'dfhjdf-sd53-456',
      'source_system': 'system1',
      'rc': 412, 'message': 'Inward parameter inp1 does not pass format assertion date=%Y%m%d',
      'input_parms': {'inp1': '20202525', 'inp2': '1', 'inp3': '1'},
      'records': []}
     ),
    #test_get_assertion_re
    ('/+-template-+/v1/49824596-fgdsgs-sfgdg/system1?inp1=20200101&inp2=abc&inp3=1', 412,
     {'method': '+-template-+',
      'message_idt': '49824596-fgdsgs-sfgdg',
      'source_system': 'system1',
      'rc': 412, 'message': 'Inward parameter inp2 does not in allowed list',
      'input_parms': {'inp1': '20200101', 'inp2': 'abc', 'inp3': '1'},
      'records': []}
     ),
    #test_get_assertion_miss_parms
    ('/+-template-+/v1/4214-sfvdb-23324/system1?inp1=20200101&inp3=1', 412,
     {'method': '+-template-+',
      'message_idt': '4214-sfvdb-23324',
      'source_system': 'system1',
      'rc': 412, 'message': 'Inward parameter inp2 does not find in input parameters',
      'input_parms': {'inp1': '20200101', 'inp3': '1'},
      'records': []}
     ),
    # test_get_assertion_invalid_parms
    ('/+-template-+/v1/4214-sfvdb-23324/system1?inp1=20200101&inp2=1&inp3=1&inp4=1', 412,
     {'method': '+-template-+',
      'message_idt': '4214-sfvdb-23324',
      'source_system': 'system1',
      'rc': 412, 'message': 'Illegal parameter name: inp4',
      'input_parms': {'inp1': '20200101', 'inp2': '1', 'inp3': '1', 'inp4': '1'},
      'records': []}
     ),
    # test_get_assertion_duplicate_parms - we take first
    ('/+-template-+/v1/4214-sfvdb-23324/system1?inp1=20200101&inp2=1&inp3=1&inp3=2', 200,
     {'method': '+-template-+',
      'message_idt': '4214-sfvdb-23324',
      'source_system': 'system1',
      'rc': 200, 'message': 'Success',
      'input_parms': {'inp1': '20200101', 'inp2': '1', 'inp3': '1'},
      'records': [{'PARM1': 'Hello1', 'PARM2': 'World1'},
                  {'PARM1': 'Hello2', 'PARM2': 'World2'},
                  {'PARM1': 'Hello3', 'PARM2': 'World3'},
                  {'PARM1': '1', 'PARM2': 'World3'}]}
     ),
    #status
    ('/+-template-+/status', 200,
     {'dbConfConPool': 10,
      'dbConfTimeout': 10000,
       'dbConnectionStatus': 'UP',
       'lastErrorInMin': -1,
       'lastSuccessInMin': -1,
       'maxConfQueue': 200,
       'meanGetSQLDurationInSec': 0,
       'meanGetTotalDurationInSec': 0.0,
       'meanPostPLSQLDurationInSec': 0,
       'meanPostTotalDurationInSec': 0.0,
        'message': 'Service is up',
        'rc': 200,
        'upTimeInMin': 0.0,
        'workQueue': 0,
        'configRelease': '2020_01_21',
        'srcVersion': '2020_11_04'
      }
     ),
    ]

@pytest.mark.parametrize("get_req, http_rc, expected", get_testdata)
async def test_get(client,get_req, http_rc, expected):
    resp = await client[0].get(get_req)
    data = await resp.json()
    assert data == expected
    assert resp.status == http_rc


# POST "post_req, http_rc, expected"
post_testdata = [
    #happy path
    ('/+-template-+/v1/2435647546rtr/system4?sleep_from=0.1&sleep_to=0.1', 200,
     {"method": "+-template-+",
      "message_idt": "2435647546rtr",
         "source_system": "system4",
         "rc": 200,
         "message": "Success",
         "input_parms": {
             "sleep_from": "0.1",
             "sleep_to": "0.1"
         },
         "addRC": "0",
         "addRefId": ".1"
      }
     ),
    # test_post_assertion_system
    ('/+-template-+/v1/2435647546rtr/system_99?sleep_from=0.1&sleep_to=0.2', 412,
     {"method": "+-template-+",
      "message_idt": "2435647546rtr",
         "source_system": "system_99",
         "rc": 412,
         "message": "Inward parameter source_system does not in allowed list",
         "input_parms": {
             "sleep_from": "0.1",
             "sleep_to": "0.2"
         }
      }
     ),
    #test_post_assertion_re
    ('/+-template-+/v1/2435647546rtr/system4?sleep_from=0.1&sleep_to=abc', 412,
     {"method": "+-template-+",
      "message_idt": "2435647546rtr",
         "source_system": "system4",
         "rc": 412,
         "message": "Inward parameter sleep_to does not pass format assertion "\
                    're=[0-9,\\.]+',
         "input_parms": {
             "sleep_from": "0.1",
             "sleep_to": "abc"
         }
      }
     ),
    #test_post_assertion_miss_parms
    ('/+-template-+/v1/2435647546rtr/system4?sleep_from=0.1', 412,
     {"method": "+-template-+",
      "message_idt": "2435647546rtr",
      "source_system": "system4",
      "rc": 412,
      "message": "Inward parameter sleep_to does not find in input parameters",
      "input_parms": {
          "sleep_from": "0.1"
      }
      }
     ),
    ]

@pytest.mark.parametrize("post_req, http_rc, expected", post_testdata)
async def test_post(client,post_req, http_rc, expected):
    resp = await client[0].post(post_req)
    assert resp.status == http_rc
    data = await resp.json()
    assert data == expected

# try send request after disconnect
post_testdata = [
    #happy path
    ('/+-template-+/v1/2435647546rtr/system4?sleep_from=0.1&sleep_to=0.1', 200,
     {"method": "+-template-+",
      "message_idt": "2435647546rtr",
         "source_system": "system4",
         "rc": 200,
         "message": "Success",
         "input_parms": {
             "sleep_from": "0.1",
             "sleep_to": "0.1"
         },
         "addRC": "0",
         "addRefId": ".1"
      }
     )
    ]
@pytest.mark.parametrize("post_req, http_rc, expected", post_testdata)
async def test_post_after_disconnect(client, post_req, http_rc, expected):
    client[1].db_disconnect()
    resp = await client[0].post(post_req)
    assert resp.status == http_rc
    data = await resp.json()
    assert data == expected

get_testdata = [
    #happy path
    ('/+-template-+/v1/546uhfgddgdhf/system1?inp1=20200101&inp2=1&inp3=1', 200,
     {"method": "+-template-+",
      'message_idt': '546uhfgddgdhf',
      'source_system': 'system1',
      'rc': 200, 'message': 'Success',
      'input_parms': {'inp1': '20200101', 'inp2': '1', 'inp3': '1'},
      'records': [{'PARM1': 'Hello1', 'PARM2': 'World1'},
                  {'PARM1': 'Hello2', 'PARM2': 'World2'},
                  {'PARM1': 'Hello3', 'PARM2': 'World3'},
                  {'PARM1': '1', 'PARM2': 'World3'}]}
     )
]
@pytest.mark.parametrize("get_req, http_rc, expected", get_testdata)
async def test_get_after_disconnect(client,get_req, http_rc, expected):
    client[1].db_disconnect()
    resp = await client[0].get(get_req)
    data = await resp.json()
    assert data == expected
    assert resp.status == http_rc


async def test_series(client):
    resp404 = await client[0].get('/')
    assert resp404.status == 404
    resp_swagger = await client[0].get('/+-template-+/swagger')
    assert resp_swagger.status == 200
    resp_status = await client[0].get('/+-template-+/status')
    assert resp_status.status == 200
    resp_get = await client[0].get('/+-template-+/v1/e78oghjfgfdf/system1?inp1=20200101&inp2=1&inp3=1')
    assert resp_get.status == 200
    resp_post = await client[0].post('/+-template-+/v1/2435647546rtr/system4?sleep_from=0.1&sleep_to=0.1')
    assert resp_post.status == 200