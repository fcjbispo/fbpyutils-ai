[Firecrawl Docs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png)](https://firecrawl.dev/)

v1

Search or ask...

Ctrl K

Search...

Navigation

Extract Endpoints

Get Extract Status

[Documentation](https://docs.firecrawl.dev/introduction)
[SDKs](https://docs.firecrawl.dev/sdks/overview)
[Learn](https://www.firecrawl.dev/blog/category/tutorials)
[Integrations](https://www.firecrawl.dev/app)
[API Reference](https://docs.firecrawl.dev/api-reference/introduction)

GET

/

extract

/

{id}

Try it

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request GET \
      --url https://api.firecrawl.dev/v1/extract/{id} \
      --header 'Authorization: Bearer <token>'

200

Copy

    {
      "success": true,
      "data": {},
      "status": "completed",
      "expiresAt": "2023-11-07T05:31:56Z"
    }

#### Authorizations

[​](https://docs.firecrawl.dev/api-reference/endpoint/extract-get#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Path Parameters

[​](https://docs.firecrawl.dev/api-reference/endpoint/extract-get#parameter-id)

id

string

required

The ID of the extract job

#### Response

200 - application/json

Successful response

[​](https://docs.firecrawl.dev/api-reference/endpoint/extract-get#response-success)

success

boolean

[​](https://docs.firecrawl.dev/api-reference/endpoint/extract-get#response-data)

data

object

[​](https://docs.firecrawl.dev/api-reference/endpoint/extract-get#response-status)

status

enum<string>

The current status of the extract job

Available options:

`completed`,

`processing`,

`failed`,

`cancelled`

[​](https://docs.firecrawl.dev/api-reference/endpoint/extract-get#response-expires-at)

expiresAt

string

[Suggest edits](https://github.com/hellofirecrawl/docs/edit/main/api-reference/endpoint/extract-get.mdx)
[Raise issue](https://github.com/hellofirecrawl/docs/issues/new?title=Issue%20on%20docs&body=Path:%20/api-reference/endpoint/extract-get)

[Extract](https://docs.firecrawl.dev/api-reference/endpoint/extract)
[Search](https://docs.firecrawl.dev/api-reference/endpoint/search)

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request GET \
      --url https://api.firecrawl.dev/v1/extract/{id} \
      --header 'Authorization: Bearer <token>'

200

Copy

    {
      "success": true,
      "data": {},
      "status": "completed",
      "expiresAt": "2023-11-07T05:31:56Z"
    }