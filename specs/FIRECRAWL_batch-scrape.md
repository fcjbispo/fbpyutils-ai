[Firecrawl Docs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png)](https://firecrawl.dev/)

v1

Search or ask...

Ctrl K

Search...

Navigation

Scrape Endpoints

Batch Scrape

[Documentation](https://docs.firecrawl.dev/introduction)
[SDKs](https://docs.firecrawl.dev/sdks/overview)
[Learn](https://www.firecrawl.dev/blog/category/tutorials)
[Integrations](https://www.firecrawl.dev/app)
[API Reference](https://docs.firecrawl.dev/api-reference/introduction)

POST

/

batch

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
      --url https://api.firecrawl.dev/v1/batch/scrape \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "urls": [\
        "<string>"\
      ],
      "webhook": {
        "url": "<string>",
        "headers": {},
        "metadata": {},
        "events": [\
          "completed"\
        ]
      },
      "ignoreInvalidURLs": false,
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
    }'

200

402

429

500

Copy

    {
      "success": true,
      "id": "<string>",
      "url": "<string>",
      "invalidURLs": [\
        "<string>"\
      ]
    }

#### Authorizations

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Body

application/json

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-urls)

urls

string\[\]

required

The URL to scrape

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-webhook)

webhook

object

A webhook specification object.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-webhook-url)

webhook.url

string

required

The URL to send the webhook to. This will trigger for batch scrape started (batch\_scrape.started), every page scraped (batch\_scrape.page) and when the batch scrape is completed (batch\_scrape.completed or batch\_scrape.failed). The response will be the same as the `/scrape` endpoint.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-webhook-headers)

webhook.headers

object

Headers to send to the webhook URL.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-webhook-headers-key)

webhook.headers.{key}

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-webhook-metadata)

webhook.metadata

object

Custom metadata that will be included in all webhook payloads for this scrape

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-webhook-events)

webhook.events

enum<string>\[\]

Type of events that should be sent to the webhook URL. (default: all)

Available options:

`completed`,

`page`,

`failed`,

`started`

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-ignore-invalid-urls)

ignoreInvalidURLs

boolean

default:false

If invalid URLs are specified in the urls array, they will be ignored. Instead of them failing the entire request, a batch scrape using the remaining valid URLs will be created, and the invalid URLs will be returned in the invalidURLs field of the response.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-formats)

formats

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

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-only-main-content)

onlyMainContent

boolean

default:true

Only return the main content of the page excluding headers, navs, footers, etc.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-include-tags)

includeTags

string\[\]

Tags to include in the output.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-exclude-tags)

excludeTags

string\[\]

Tags to exclude from the output.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-headers)

headers

object

Headers to send with the request. Can be used to send cookies, user-agent, etc.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-wait-for)

waitFor

integer

default:0

Specify a delay in milliseconds before fetching the content, allowing the page sufficient time to load.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-mobile)

mobile

boolean

default:false

Set to true if you want to emulate scraping from a mobile device. Useful for testing responsive pages and taking mobile screenshots.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-skip-tls-verification)

skipTlsVerification

boolean

default:false

Skip TLS certificate verification when making requests

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-timeout)

timeout

integer

default:30000

Timeout in milliseconds for the request

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-json-options)

jsonOptions

object

Extract object

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-json-options-schema)

jsonOptions.schema

object

The schema to use for the extraction (Optional)

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-json-options-system-prompt)

jsonOptions.systemPrompt

string

The system prompt to use for the extraction (Optional)

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-json-options-prompt)

jsonOptions.prompt

string

The prompt to use for the extraction without a schema (Optional)

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-actions)

actions

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

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-actions-type)

actions.type

enum<string>

required

Wait for a specified amount of milliseconds

Available options:

`wait`

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-actions-milliseconds)

actions.milliseconds

integer

Number of milliseconds to wait

Required range: `x >= 1`

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-actions-selector)

actions.selector

string

Query selector to find the element by

Example:

`"#my-element"`

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-location)

location

object

Location settings for the request. When specified, this will use an appropriate proxy if available and emulate the corresponding language and timezone settings. Defaults to 'US' if not specified.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-location-country)

location.country

string

default:US

ISO 3166-1 alpha-2 country code (e.g., 'US', 'AU', 'DE', 'JP')

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-location-languages)

location.languages

string\[\]

Preferred languages and locales for the request in order of priority. Defaults to the language of the specified location. See [https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language)

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-remove-base64-images)

removeBase64Images

boolean

Removes all base 64 images from the output, which may be overwhelmingly long. The image's alt text remains in the output, but the URL is replaced with a placeholder.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-block-ads)

blockAds

boolean

default:true

Enables ad-blocking and cookie popup blocking.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-proxy)

proxy

enum<string>

Specifies the type of proxy to use.

*   **basic**: Proxies for scraping sites with none to basic anti-bot solutions. Fast and usually works.
*   **stealth**: Stealth proxies for scraping sites with advanced anti-bot solutions. Slower, but more reliable on certain sites.

If you do not specify a proxy, Firecrawl will automatically attempt to determine which one you need based on the target site.

Available options:

`basic`,

`stealth`

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-change-tracking-options)

changeTrackingOptions

object

Options for change tracking (Beta). Only applicable when 'changeTracking' is included in formats. The 'markdown' format must also be specified when using change tracking.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-change-tracking-options-mode)

changeTrackingOptions.mode

enum<string>

The mode to use for change tracking. 'default' performs a basic comparison, 'git-diff' provides a detailed diff, and 'json' compares extracted JSON data.

Available options:

`git-diff`,

`json`

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-change-tracking-options-schema)

changeTrackingOptions.schema

object

Schema for JSON extraction when using 'json' mode. Defines the structure of data to extract and compare.

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#body-change-tracking-options-prompt)

changeTrackingOptions.prompt

string

Prompt to use for change tracking when using 'json' mode. If not provided, the default prompt will be used.

#### Response

200

200402429500

application/json

Successful response

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#response-success)

success

boolean

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#response-id)

id

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#response-url)

url

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape#response-invalid-urls)

invalidURLs

string\[\] | null

If ignoreInvalidURLs is true, this is an array containing the invalid URLs that were specified in the request. If there were no invalid URLs, this will be an empty array. If ignoreInvalidURLs is false, this field will be undefined.

[Suggest edits](https://github.com/hellofirecrawl/docs/edit/main/api-reference/endpoint/batch-scrape.mdx)
[Raise issue](https://github.com/hellofirecrawl/docs/issues/new?title=Issue%20on%20docs&body=Path:%20/api-reference/endpoint/batch-scrape)

[Scrape](https://docs.firecrawl.dev/api-reference/endpoint/scrape)
[Get Batch Scrape Status](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape-get)

cURL

Python

JavaScript

PHP

Go

Java

Copy

    curl --request POST \
      --url https://api.firecrawl.dev/v1/batch/scrape \
      --header 'Authorization: Bearer <token>' \
      --header 'Content-Type: application/json' \
      --data '{
      "urls": [\
        "<string>"\
      ],
      "webhook": {
        "url": "<string>",
        "headers": {},
        "metadata": {},
        "events": [\
          "completed"\
        ]
      },
      "ignoreInvalidURLs": false,
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
    }'

200

402

429

500

Copy

    {
      "success": true,
      "id": "<string>",
      "url": "<string>",
      "invalidURLs": [\
        "<string>"\
      ]
    }
