[Firecrawl Docs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png)](https://firecrawl.dev/)

v1

Search or ask...

Ctrl K

Search...

Navigation

Map Endpoints

Map

[Documentation](https://docs.firecrawl.dev/introduction)
[SDKs](https://docs.firecrawl.dev/sdks/overview)
[Learn](https://www.firecrawl.dev/blog/category/tutorials)
[Integrations](https://www.firecrawl.dev/app)
[API Reference](https://docs.firecrawl.dev/api-reference/introduction)

POST

/

map

Try it

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request POST \
      --url https://api.firecrawl.dev/v1/map \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "url": "<string>",
      "search": "<string>",
      "ignoreSitemap": true,
      "sitemapOnly": false,
      "includeSubdomains": false,
      "limit": 5000,
      "timeout": 123
    }'

200

402

429

500

Copy

    {
      "success": true,
      "links": [\
        "<string>"\
      ]
    }

#### Authorizations

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Body

application/json

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#body-url)

url

string

required

The base URL to start crawling from

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#body-search)

search

string

Search query to use for mapping. During the Alpha phase, the 'smart' part of the search functionality is limited to 1000 search results. However, if map finds more results, there is no limit applied.

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#body-ignore-sitemap)

ignoreSitemap

boolean

default:true

Ignore the website sitemap when crawling.

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#body-sitemap-only)

sitemapOnly

boolean

default:false

Only return links found in the website sitemap

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#body-include-subdomains)

includeSubdomains

boolean

default:false

Include subdomains of the website

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#body-limit)

limit

integer

default:5000

Maximum number of links to return

Required range: `x <= 5000`

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#body-timeout)

timeout

integer

Timeout in milliseconds. There is no timeout by default.

#### Response

200

200402429500

application/json

Successful response

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#response-success)

success

boolean

[​](https://docs.firecrawl.dev/api-reference/endpoint/map#response-links)

links

string\[\]

[Suggest edits](https://github.com/hellofirecrawl/docs/edit/main/api-reference/endpoint/map.mdx)
[Raise issue](https://github.com/hellofirecrawl/docs/issues/new?title=Issue%20on%20docs&body=Path:%20/api-reference/endpoint/map)

[Get Crawl Errors](https://docs.firecrawl.dev/api-reference/endpoint/scrape-get-errors)
[Extract](https://docs.firecrawl.dev/api-reference/endpoint/extract)

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request POST \
      --url https://api.firecrawl.dev/v1/map \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "url": "<string>",
      "search": "<string>",
      "ignoreSitemap": true,
      "sitemapOnly": false,
      "includeSubdomains": false,
      "limit": 5000,
      "timeout": 123
    }'

200

402

429

500

Copy

    {
      "success": true,
      "links": [\
        "<string>"\
      ]
    }
