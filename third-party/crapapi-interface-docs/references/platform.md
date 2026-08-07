# CrapAPI platform reference

## Fixed scope

- Base URL: `https://test.95598pay.top:29943/crapapi`
- Project: `电e宝移动端接口服务（deb-api-rest）`
- Project ID: `156939461626807001127`
- Project-level interface list: `admin.do#/user/interface/list?pageName=接口&dataType=interface&menu_a=menu-project&menu_b=menu_interface&projectName=电e宝移动端接口服务（deb-api-rest）&projectId=156939461626807001127&moduleId=`

## Read-only HTTP flow

1. POST `visitorSearch.do` with form fields `keyword=<normalized full API path>` and `currentPage=1`.
2. Keep results whose `type` is `Interface` and `projectId` matches the fixed project.
3. GET `visitor/interface/detail.do?id=<interface id>` for each candidate.
4. Accept only a detail whose `data.fullUrl` exactly equals the normalized target.

Use normal TLS verification. Do not add insecure certificate bypasses.

Important structured fields:

- `crShowHeaderList`: request headers
- `crShowParamList`: input parameters
- `crShowResponseParamList`: response parameters
- `deep`: response nesting level
- `errors`: JSON-encoded project error list
- `requestExam`, `trueExam`, `falseExam`: examples

## Browser fallback flow

1. Open `loginOrRegister.do#/login` and let the user's installed login helper or the user complete login.
2. Select `电e宝移动端接口服务（deb-api-rest）`.
3. Select the project-level `接口` entry, not a specific module.
4. Fill the `URL` textbox and click `查询`.
5. Match the result row by exact full URL; do not confuse prefix matches such as `zfbSign` and `zfbSignQuery`.
6. Open the row's read-only detail action, not edit or debug.
7. Extract basic metadata, inputs, outputs, examples, and error codes.

If login or a CAPTCHA blocks the browser path, stop and ask the user to complete it.
