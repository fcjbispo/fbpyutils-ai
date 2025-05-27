[Firecrawl Docs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png)](https://firecrawl.dev/)

v1

Search or ask...

Ctrl K

Search...

Navigation

Crawl Endpoints

Crawl

[Documentation](https://docs.firecrawl.dev/introduction)
[SDKs](https://docs.firecrawl.dev/sdks/overview)
[Learn](https://www.firecrawl.dev/blog/category/tutorials)
[Integrations](https://www.firecrawl.dev/app)
[API Reference](https://docs.firecrawl.dev/api-reference/introduction)

POST

/

scrape

Try it

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request POST \
      --url https://api.firecrawl.dev/v1/scrape \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "url": "<string>",
      "excludePaths": [\
        "<string>"\
      ],
      "includePaths": [\
        "<string>"\
      ],
      "maxDepth": 10,
      "maxDiscoveryDepth": 123,
      "ignoreSitemap": false,
      "ignoreQueryParameters": false,
      "limit": 10000,
      "allowBackwardLinks": false,
      "allowExternalLinks": false,
      "webhook": {
        "url": "<string>",
        "headers": {},
        "metadata": {},
        "events": [\
          "completed"\
        ]
      },
      "scrapeOptions": {
        "formats": [\
          "markdown"\
        ],
        "onlyMainContent": true,
        "includeTags": [\
          "<string>"\
        ],
        "excludeTags": [\
          "<string>"\
        ],
        "headers": {},
        "waitFor": 0,
        "mobile": false,
        "skipTlsVerification": false,
        "timeout": 30000,
        "jsonOptions": {
          "schema": {},
          "systemPrompt": "<string>",
          "prompt": "<string>"
        },
        "actions": [\
          {\
            "type": "wait",\
            "milliseconds": 2,\
            "selector": "#my-element"\
          }\
        ],
        "location": {
          "country": "US",
          "languages": [\
            "en-US"\
          ]
        },
        "removeBase64Images": true,
        "blockAds": true,
        "proxy": "basic",
        "changeTrackingOptions": {
          "mode": "git-diff",
          "schema": {},
          "prompt": "<string>"
        }
      }
    }'

200

402

429

500

Copy

    {
      "success": true,
      "id": "<string>",
      "url": "<string>"
    }

#### Authorizations

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Body

application/json

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-url)

url

string

required

The base URL to start crawling from

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-exclude-paths)

excludePaths

string\[\]

URL pathname regex patterns that exclude matching URLs from the scrape. For example, if you set "excludePaths": \["blog/.\*"\] for the base URL firecrawl.dev, any results matching that pattern will be excluded, such as [https://www.firecrawl.dev/blog/firecrawl-launch-week-1-recap](https://www.firecrawl.dev/blog/firecrawl-launch-week-1-recap)
.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-include-paths)

includePaths

string\[\]

URL pathname regex patterns that include matching URLs in the scrape. Only the paths that match the specified patterns will be included in the response. For example, if you set "includePaths": \["blog/.\*"\] for the base URL firecrawl.dev, only results matching that pattern will be included, such as [https://www.firecrawl.dev/blog/firecrawl-launch-week-1-recap](https://www.firecrawl.dev/blog/firecrawl-launch-week-1-recap)
.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-max-depth)

maxDepth

integer

default:10

Maximum depth to scrape relative to the base URL. Basically, the max number of slashes the pathname of a scraped URL may contain.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-max-discovery-depth)

maxDiscoveryDepth

integer

Maximum depth to scrape based on discovery order. The root site and sitemapped pages has a discovery depth of 0. For example, if you set it to 1, and you set ignoreSitemap, you will only scrape the entered URL and all URLs that are linked on that page.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-ignore-sitemap)

ignoreSitemap

boolean

default:false

Ignore the website sitemap when crawling

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-ignore-query-parameters)

ignoreQueryParameters

boolean

default:false

Do not re-scrape the same path with different (or none) query parameters

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-limit)

limit

integer

default:10000

Maximum number of pages to scrape. Default limit is 10000.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-allow-backward-links)

allowBackwardLinks

boolean

default:false

Enables the crawler to navigate from a specific URL to previously linked pages.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-allow-external-links)

allowExternalLinks

boolean

default:false

Allows the crawler to follow links to external websites.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-webhook)

webhook

object

A webhook specification object.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-webhook-url)

webhook.url

string

required

The URL to send the webhook to. This will trigger for scrape started (scrape.started), every page crawled (scrape.page) and when the scrape is completed (scrape.completed or scrape.failed). The response will be the same as the `/scrape` endpoint.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-webhook-headers)

webhook.headers

object

Headers to send to the webhook URL.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-webhook-headers-key)

webhook.headers.{key}

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-webhook-metadata)

webhook.metadata

object

Custom metadata that will be included in all webhook payloads for this scrape

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-webhook-events)

webhook.events

enum<string>\[\]

Type of events that should be sent to the webhook URL. (default: all)

Available options:

`completed`,

`page`,

`failed`,

`started`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options)

scrapeOptions

object

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-formats)

scrapeOptions.formats

enum<string>\[\]

Formats to include in the output.

Available options:

`markdown`,

`html`,

`rawHtml`,

`links`,

`screenshot`,

`screenshot@fullPage`,

`json`,

`changeTracking`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-only-main-content)

scrapeOptions.onlyMainContent

boolean

default:true

Only return the main content of the page excluding headers, navs, footers, etc.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-include-tags)

scrapeOptions.includeTags

string\[\]

Tags to include in the output.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-exclude-tags)

scrapeOptions.excludeTags

string\[\]

Tags to exclude from the output.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-headers)

scrapeOptions.headers

object

Headers to send with the request. Can be used to send cookies, user-agent, etc.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-wait-for)

scrapeOptions.waitFor

integer

default:0

Specify a delay in milliseconds before fetching the content, allowing the page sufficient time to load.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-mobile)

scrapeOptions.mobile

boolean

default:false

Set to true if you want to emulate scraping from a mobile device. Useful for testing responsive pages and taking mobile screenshots.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-skip-tls-verification)

scrapeOptions.skipTlsVerification

boolean

default:false

Skip TLS certificate verification when making requests

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-timeout)

scrapeOptions.timeout

integer

default:30000

Timeout in milliseconds for the request

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-json-options)

scrapeOptions.jsonOptions

object

Extract object

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-json-options-schema)

scrapeOptions.jsonOptions.schema

object

The schema to use for the extraction (Optional)

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-json-options-system-prompt)

scrapeOptions.jsonOptions.systemPrompt

string

The system prompt to use for the extraction (Optional)

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-json-options-prompt)

scrapeOptions.jsonOptions.prompt

string

The prompt to use for the extraction without a schema (Optional)

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-actions)

scrapeOptions.actions

object\[\]

Actions to perform on the page before grabbing the content

*   Wait
*   Screenshot
*   Click
*   Write text
*   Press a key
*   Scroll
*   Scrape
*   Execute JavaScript

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-actions-type)

scrapeOptions.actions.type

enum<string>

required

Wait for a specified amount of milliseconds

Available options:

`wait`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-actions-milliseconds)

scrapeOptions.actions.milliseconds

integer

Number of milliseconds to wait

Required range: `x >= 1`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-actions-selector)

scrapeOptions.actions.selector

string

Query selector to find the element by

Example:

`"#my-element"`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-location)

scrapeOptions.location

object

Location settings for the request. When specified, this will use an appropriate proxy if available and emulate the corresponding language and timezone settings. Defaults to 'US' if not specified.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-location-country)

scrapeOptions.location.country

string

default:US

ISO 3166-1 alpha-2 country code (e.g., 'US', 'AU', 'DE', 'JP')

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-location-languages)

scrapeOptions.location.languages

string\[\]

Preferred languages and locales for the request in order of priority. Defaults to the language of the specified location. See [https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language)

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-remove-base64-images)

scrapeOptions.removeBase64Images

boolean

Removes all base 64 images from the output, which may be overwhelmingly long. The image's alt text remains in the output, but the URL is replaced with a placeholder.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-block-ads)

scrapeOptions.blockAds

boolean

default:true

Enables ad-blocking and cookie popup blocking.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-proxy)

scrapeOptions.proxy

enum<string>

Specifies the type of proxy to use.

*   **basic**: Proxies for scraping sites with none to basic anti-bot solutions. Fast and usually works.
*   **stealth**: Stealth proxies for scraping sites with advanced anti-bot solutions. Slower, but more reliable on certain sites.

If you do not specify a proxy, Firecrawl will automatically attempt to determine which one you need based on the target site.

Available options:

`basic`,

`stealth`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-change-tracking-options)

scrapeOptions.changeTrackingOptions

object

Options for change tracking (Beta). Only applicable when 'changeTracking' is included in formats. The 'markdown' format must also be specified when using change tracking.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-change-tracking-options-mode)

scrapeOptions.changeTrackingOptions.mode

enum<string>

The mode to use for change tracking. 'default' performs a basic comparison, 'git-diff' provides a detailed diff, and 'json' compares extracted JSON data.

Available options:

`git-diff`,

`json`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-change-tracking-options-schema)

scrapeOptions.changeTrackingOptions.schema

object

Schema for JSON extraction when using 'json' mode. Defines the structure of data to extract and compare.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#body-scrape-options-change-tracking-options-prompt)

scrapeOptions.changeTrackingOptions.prompt

string

Prompt to use for change tracking when using 'json' mode. If not provided, the default prompt will be used.

#### Response

200

200402429500

application/json

Successful response

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#response-success)

success

boolean

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#response-id)

id

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape-post#response-url)

url

string

[Suggest edits](https://github.com/hellofirecrawl/docs/edit/main/api-reference/endpoint/scrape-post.mdx)
[Raise issue](https://github.com/hellofirecrawl/docs/issues/new?title=Issue%20on%20docs&body=Path:%20/api-reference/endpoint/scrape-post)

[Get Batch Scrape Errors](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get-errors)
[Get Crawl Status](https://docs.firecrawl.dev/api-reference/endpoint/scrape-get)

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request POST \
      --url https://api.firecrawl.dev/v1/scrape \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "url": "<string>",
      "excludePaths": [\
        "<string>"\
      ],
      "includePaths": [\
        "<string>"\
      ],
      "maxDepth": 10,
      "maxDiscoveryDepth": 123,
      "ignoreSitemap": false,
      "ignoreQueryParameters": false,
      "limit": 10000,
      "allowBackwardLinks": false,
      "allowExternalLinks": false,
      "webhook": {
        "url": "<string>",
        "headers": {},
        "metadata": {},
        "events": [\
          "completed"\
        ]
      },
      "scrapeOptions": {
        "formats": [\
          "markdown"\
        ],
        "onlyMainContent": true,
        "includeTags": [\
          "<string>"\
        ],
        "excludeTags": [\
          "<string>"\
        ],
        "headers": {},
        "waitFor": 0,
        "mobile": false,
        "skipTlsVerification": false,
        "timeout": 30000,
        "jsonOptions": {
          "schema": {},
          "systemPrompt": "<string>",
          "prompt": "<string>"
        },
        "actions": [\
          {\
            "type": "wait",\
            "milliseconds": 2,\
            "selector": "#my-element"\
          }\
        ],
        "location": {
          "country": "US",
          "languages": [\
            "en-US"\
          ]
        },
        "removeBase64Images": true,
        "blockAds": true,
        "proxy": "basic",
        "changeTrackingOptions": {
          "mode": "git-diff",
          "schema": {},
          "prompt": "<string>"
        }
      }
    }'

200

402

429

500

Copy

    {
      "success": true,
      "id": "<string>",
      "url": "<string>"
    }
