[Firecrawl Docs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png)](https://firecrawl.dev/)

v1

Search or ask...

Ctrl K

Search...

Navigation

Scrape Endpoints

Get Batch Scrape Errors

[Documentation](https://docs.firecrawl.dev/introduction)
[SDKs](https://docs.firecrawl.dev/sdks/overview)
[Learn](https://www.firecrawl.dev/blog/category/tutorials)
[Integrations](https://www.firecrawl.dev/app)
[API Reference](https://docs.firecrawl.dev/api-reference/introduction)

GET

/

batch

/

scrape

/

{id}

/

errors

Try it

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request GET \
      --url https://api.firecrawl.dev/v1/batch/scrape/{id}/errors \
      --header 'Authorization: Bearer <token>'

200

402

429

500

Copy

    {
      "errors": [\
        {\
          "id": "<string>",\
          "timestamp": "<string>",\
          "url": "<string>",\
          "error": "<string>"\
        }\
      ],
      "robotsBlocked": [\
        "<string>"\
      ]
    }

#### Authorizations

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Path Parameters

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors#parameter-id)

id

string

required

The ID of the batch scrape job

#### Response

200

200402429500

application/json

Successful response

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors#response-errors)

errors

object\[\]

Errored scrape jobs and error details

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors#response-errors-id)

errors.id

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors#response-errors-timestamp)

errors.timestamp

string | null

ISO timestamp of failure

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors#response-errors-url)

errors.url

string

Scraped URL

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors#response-errors-error)

errors.error

string

Error message

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors#response-robots-blocked)

robotsBlocked

string\[\]

List of URLs that were attempted in scraping but were blocked by robots.txt

[Suggest edits](https://github.com/hellofirecrawl/docs/edit/main/api-reference/endpoint/batch-scrape-get-errors.mdx)
[Raise issue](https://github.com/hellofirecrawl/docs/issues/new?title=Issue%20on%20docs&body=Path:%20/api-reference/endpoint/batch-scrape-get-errors)

[Get Batch Scrape Status](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get)
[Crawl](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post)

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request GET \
      --url https://api.firecrawl.dev/v1/batch/scrape/{id}/errors \
      --header 'Authorization: Bearer <token>'

200

402

429

500

Copy

    {
      "errors": [\
        {\
          "id": "<string>",\
          "timestamp": "<string>",\
          "url": "<string>",\
          "error": "<string>"\
        }\
      ],
      "robotsBlocked": [\
        "<string>"\
      ]
    }
