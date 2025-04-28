[Firecrawl Docs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png)](https://firecrawl.dev/)

v1

Search or ask...

Ctrl K

Search...

Navigation

Search Endpoints

Search

[Documentation](https://docs.firecrawl.dev/introduction)
[SDKs](https://docs.firecrawl.dev/sdks/overview)
[Learn](https://www.firecrawl.dev/blog/category/tutorials)
[Integrations](https://www.firecrawl.dev/app)
[API Reference](https://docs.firecrawl.dev/api-reference/introduction)

POST

/

search

Try it

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request POST \
      --url https://api.firecrawl.dev/v1/search \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "query": "<string>",
      "limit": 5,
      "tbs": "<string>",
      "lang": "en",
      "country": "us",
      "location": "<string>",
      "timeout": 60000,
      "scrapeOptions": {}
    }'

200

408

500

Copy

    {
      "success": true,
      "data": [\
        {\
          "title": "<string>",\
          "description": "<string>",\
          "url": "<string>",\
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
            "sourceURL": "<string>",\
            "statusCode": 123,\
            "error": "<string>"\
          }\
        }\
      ],
      "warning": "<string>"
    }

The search endpoint combines web search (SERP) with Firecrawl’s scraping capabilities to return full page content for any query.

Include `scrapeOptions` with `formats: ["markdown"]` to get complete markdown content for each search result otherwise you will default to getting the SERP results (url, title, description).

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#supported-query-operators)

Supported query operators
--------------------------------------------------------------------------------------------------------------------

We support a variety of query operators that allow you to filter your searches better.

| Operator | Functionality | Examples |
| --- | --- | --- |
| `""` | Non-fuzzy matches a string of text | `"Firecrawl"` |
| `-` | Excludes certain keywords or negates other operators | `-bad`, `-site:firecrawl.dev` |
| `site:` | Only returns results from a specified website | `site:firecrawl.dev` |
| `inurl:` | Only returns results that include a word in the URL | `inurl:firecrawl` |
| `allinurl:` | Only returns results that include multiple words in the URL | `allinurl:git firecrawl` |
| `intitle:` | Only returns results that include a word in the title of the page | `intitle:Firecrawl` |
| `allintitle:` | Only returns results that include multiple words in the title of the page | `allintitle:firecrawl playground` |
| `related:` | Only returns results that are related to a specific domain | `related:firecrawl.dev` |

#### Authorizations

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Body

application/json

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#body-query)

query

string

required

The search query

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#body-limit)

limit

integer

default:5

Maximum number of results to return

Required range: `1 <= x <= 50`

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#body-tbs)

tbs

string

Time-based search parameter

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#body-lang)

lang

string

default:en

Language code for search results

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#body-country)

country

string

default:us

Country code for search results

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#body-location)

location

string

Location parameter for search results

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#body-timeout)

timeout

integer

default:60000

Timeout in milliseconds

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#body-scrape-options)

scrapeOptions

object

Options for scraping search results

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#body-scrape-options-formats)

scrapeOptions.formats

enum<string>\[\]

Formats to include in the output

Available options:

`markdown`,

`html`,

`rawHtml`,

`links`,

`screenshot`,

`screenshot@fullPage`,

`extract`

#### Response

200

200408500

application/json

Successful response

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-success)

success

boolean

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data)

data

object\[\]

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-title)

data.title

string

Title from search result

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-description)

data.description

string

Description from search result

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-url)

data.url

string

URL of the search result

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-markdown)

data.markdown

string | null

Markdown content if scraping was requested

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-html)

data.html

string | null

HTML content if requested in formats

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-raw-html)

data.rawHtml

string | null

Raw HTML content if requested in formats

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-links)

data.links

string\[\]

Links found if requested in formats

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-screenshot)

data.screenshot

string | null

Screenshot URL if requested in formats

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-metadata)

data.metadata

object

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-metadata-title)

data.metadata.title

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-metadata-description)

data.metadata.description

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-metadata-source-url)

data.metadata.sourceURL

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-metadata-status-code)

data.metadata.statusCode

integer

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-data-metadata-error)

data.metadata.error

string | null

[​](https://docs.firecrawl.dev/api-reference/endpoint/search#response-warning)

warning

string | null

Warning message if any issues occurred

[Suggest edits](https://github.com/hellofirecrawl/docs/edit/main/api-reference/endpoint/search.mdx)
[Raise issue](https://github.com/hellofirecrawl/docs/issues/new?title=Issue%20on%20docs&body=Path:%20/api-reference/endpoint/search)

[Get Extract Status](https://docs.firecrawl.dev/api-reference/endpoint/extract-get)
[Credit Usage](https://docs.firecrawl.dev/api-reference/endpoint/credit-usage)

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request POST \
      --url https://api.firecrawl.dev/v1/search \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "query": "<string>",
      "limit": 5,
      "tbs": "<string>",
      "lang": "en",
      "country": "us",
      "location": "<string>",
      "timeout": 60000,
      "scrapeOptions": {}
    }'

200

408

500

Copy

    {
      "success": true,
      "data": [\
        {\
          "title": "<string>",\
          "description": "<string>",\
          "url": "<string>",\
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
            "sourceURL": "<string>",\
            "statusCode": 123,\
            "error": "<string>"\
          }\
        }\
      ],
      "warning": "<string>"
    }