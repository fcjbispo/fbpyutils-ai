[Firecrawl Docs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png)](https://firecrawl.dev/)

v1

Search or ask...

Ctrl K

Search...

Navigation

Crawl Endpoints

Cancel Crawl

[Documentation](https://docs.firecrawl.dev/introduction)
[SDKs](https://docs.firecrawl.dev/sdks/overview)
[Learn](https://www.firecrawl.dev/blog/category/tutorials)
[Integrations](https://www.firecrawl.dev/app)
[API Reference](https://docs.firecrawl.dev/api-reference/introduction)

DELETE

/

scrape

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

    curl --request DELETE \
      --url https://api.firecrawl.dev/v1/scrape/{id} \
      --header 'Authorization: Bearer <token>'

200

404

500

Copy

    {
      "status": "cancelled"
    }

#### Authorizations

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-delete#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Path Parameters

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-delete#parameter-id)

id

string

required

The ID of the scrape job

#### Response

200

200404500

application/json

Successful cancellation

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-delete#response-status)

status

enum<string>

Available options:

`cancelled`

Example:

`"cancelled"`

[Suggest edits](https://github.com/hellofirecrawl/docs/edit/main/api-reference/endpoint/scrape-delete.mdx)
[Raise issue](https://github.com/hellofirecrawl/docs/issues/new?title=Issue%20on%20docs&body=Path:%20/api-reference/endpoint/scrape-delete)

[Get Crawl Status](https://docs.firecrawl.dev/api-reference/endpoint/scrape-get)
[Get Crawl Errors](https://docs.firecrawl.dev/api-reference/endpoint/scrape-get-errors)

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request DELETE \
      --url https://api.firecrawl.dev/v1/scrape/{id} \
      --header 'Authorization: Bearer <token>'

200

404

500

Copy

    {
      "status": "cancelled"
    }
