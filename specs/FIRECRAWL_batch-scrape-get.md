[Firecrawl Docs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png)](https://firecrawl.dev/)

v1

Search or ask...

Ctrl K

Search...

Navigation

Scrape Endpoints

Get Batch Scrape Status

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

Try it

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request GET \
      --url https://api.firecrawl.dev/v1/batch/scrape/{id} \
      --header 'Authorization: Bearer <token>'

200

402

429

500

Copy

    {
      "status": "<string>",
      "total": 123,
      "completed": 123,
      "creditsUsed": 123,
      "expiresAt": "2023-11-07T05:31:56Z",
      "next": "<string>",
      "data": [\
        {\
          "markdown": "<string>",\
          "html": "<string>",\
          "rawHtml": "<string>",\
          "links": [\
            "<string>"\
          ],\
          "screenshot": "<string>",\
          "metadata": {\
            "title": "<string>",\
            "description": "<string>",\
            "language": "<string>",\
            "sourceURL": "<string>",\
            "<any other metadata> ": "<string>",\
            "statusCode": 123,\
            "error": "<string>"\
          }\
        }\
      ]
    }

#### Authorizations

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Path Parameters

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#parameter-id)

id

string

required

The ID of the batch scrape job

#### Response

200

200402429500

application/json

Successful response

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-status)

status

string

The current status of the batch scrape. Can be `scraping`, `completed`, or `failed`.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-total)

total

integer

The total number of pages that were attempted to be scraped.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-completed)

completed

integer

The number of pages that have been successfully scraped.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-credits-used)

creditsUsed

integer

The number of credits used for the batch scrape.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-expires-at)

expiresAt

string

The date and time when the batch scrape will expire.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-next)

next

string | null

The URL to retrieve the next 10MB of data. Returned if the batch scrape is not completed or if the response is larger than 10MB.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data)

data

object\[\]

The data of the batch scrape.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-markdown)

data.markdown

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-html)

data.html

string | null

HTML version of the content on page if `includeHtml` is true

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-raw-html)

data.rawHtml

string | null

Raw HTML content of the page if `includeRawHtml` is true

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-links)

data.links

string\[\]

List of links on the page if `includeLinks` is true

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-screenshot)

data.screenshot

string | null

Screenshot of the page if `includeScreenshot` is true

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-metadata)

data.metadata

object

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-metadata-title)

data.metadata.title

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-metadata-description)

data.metadata.description

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-metadata-language)

data.metadata.language

string | null

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-metadata-source-url)

data.metadata.sourceURL

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-metadata-any-other-metadata)

data.metadata.<any other metadata>

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-metadata-status-code)

data.metadata.statusCode

integer

The status code of the page

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get#response-data-metadata-error)

data.metadata.error

string | null

The error message of the page

[Suggest edits](https://github.com/hellofirecrawl/docs/edit/main/api-reference/endpoint/batch-scrape-get.mdx)
[Raise issue](https://github.com/hellofirecrawl/docs/issues/new?title=Issue%20on%20docs&body=Path:%20/api-reference/endpoint/batch-scrape-get)

[Batch Scrape](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape)
[Get Batch Scrape Errors](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors)

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request GET \
      --url https://api.firecrawl.dev/v1/batch/scrape/{id} \
      --header 'Authorization: Bearer <token>'

200

402

429

500

Copy

    {
      "status": "<string>",
      "total": 123,
      "completed": 123,
      "creditsUsed": 123,
      "expiresAt": "2023-11-07T05:31:56Z",
      "next": "<string>",
      "data": [\
        {\
          "markdown": "<string>",\
          "html": "<string>",\
          "rawHtml": "<string>",\
          "links": [\
            "<string>"\
          ],\
          "screenshot": "<string>",\
          "metadata": {\
            "title": "<string>",\
            "description": "<string>",\
            "language": "<string>",\
            "sourceURL": "<string>",\
            "<any other metadata> ": "<string>",\
            "statusCode": 123,\
            "error": "<string>"\
          }\
        }\
      ]
    }