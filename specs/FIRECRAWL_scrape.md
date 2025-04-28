[Firecrawl Docs home page![light logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo.png)![dark logo](https://mintlify.s3.us-west-1.amazonaws.com/firecrawl/logo/logo-dark.png)](https://firecrawl.dev/)

v1

Search or ask...

Ctrl K

Search...

Navigation

Scrape Endpoints

Scrape

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
      "data": {
        "markdown": "<string>",
        "html": "<string>",
        "rawHtml": "<string>",
        "screenshot": "<string>",
        "links": [\
          "<string>"\
        ],
        "actions": {
          "screenshots": [\
            "<string>"\
          ],
          "scrapes": [\
            {\
              "url": "<string>",\
              "html": "<string>"\
            }\
          ],
          "javascriptReturns": [\
            {\
              "type": "<string>",\
              "value": "<any>"\
            }\
          ]
        },
        "metadata": {
          "title": "<string>",
          "description": "<string>",
          "language": "<string>",
          "sourceURL": "<string>",
          "<any other metadata> ": "<string>",
          "statusCode": 123,
          "error": "<string>"
        },
        "llm_extraction": {},
        "warning": "<string>",
        "changeTracking": {
          "previousScrapeAt": "2023-11-07T05:31:56Z",
          "changeStatus": "new",
          "visibility": "visible",
          "diff": "<string>",
          "json": {}
        }
      }
    }

#### Authorizations

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#authorization-authorization)

Authorization

string

header

required

Bearer authentication header of the form `Bearer <token>`, where `<token>` is your auth token.

#### Body

application/json

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-url)

url

string

required

The URL to scrape

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-formats)

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

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-only-main-content)

onlyMainContent

boolean

default:true

Only return the main content of the page excluding headers, navs, footers, etc.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-include-tags)

includeTags

string\[\]

Tags to include in the output.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-exclude-tags)

excludeTags

string\[\]

Tags to exclude from the output.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-headers)

headers

object

Headers to send with the request. Can be used to send cookies, user-agent, etc.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-wait-for)

waitFor

integer

default:0

Specify a delay in milliseconds before fetching the content, allowing the page sufficient time to load.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-mobile)

mobile

boolean

default:false

Set to true if you want to emulate scraping from a mobile device. Useful for testing responsive pages and taking mobile screenshots.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-skip-tls-verification)

skipTlsVerification

boolean

default:false

Skip TLS certificate verification when making requests

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-timeout)

timeout

integer

default:30000

Timeout in milliseconds for the request

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-json-options)

jsonOptions

object

Extract object

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-json-options-schema)

jsonOptions.schema

object

The schema to use for the extraction (Optional)

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-json-options-system-prompt)

jsonOptions.systemPrompt

string

The system prompt to use for the extraction (Optional)

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-json-options-prompt)

jsonOptions.prompt

string

The prompt to use for the extraction without a schema (Optional)

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-actions)

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

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-actions-type)

actions.type

enum<string>

required

Wait for a specified amount of milliseconds

Available options:

`wait`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-actions-milliseconds)

actions.milliseconds

integer

Number of milliseconds to wait

Required range: `x >= 1`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-actions-selector)

actions.selector

string

Query selector to find the element by

Example:

`"#my-element"`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-location)

location

object

Location settings for the request. When specified, this will use an appropriate proxy if available and emulate the corresponding language and timezone settings. Defaults to 'US' if not specified.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-location-country)

location.country

string

default:US

ISO 3166-1 alpha-2 country code (e.g., 'US', 'AU', 'DE', 'JP')

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-location-languages)

location.languages

string\[\]

Preferred languages and locales for the request in order of priority. Defaults to the language of the specified location. See [https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language)

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-remove-base64-images)

removeBase64Images

boolean

Removes all base 64 images from the output, which may be overwhelmingly long. The image's alt text remains in the output, but the URL is replaced with a placeholder.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-block-ads)

blockAds

boolean

default:true

Enables ad-blocking and cookie popup blocking.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-proxy)

proxy

enum<string>

Specifies the type of proxy to use.

*   **basic**: Proxies for scraping sites with none to basic anti-bot solutions. Fast and usually works.
*   **stealth**: Stealth proxies for scraping sites with advanced anti-bot solutions. Slower, but more reliable on certain sites.

If you do not specify a proxy, Firecrawl will automatically attempt to determine which one you need based on the target site.

Available options:

`basic`,

`stealth`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-change-tracking-options)

changeTrackingOptions

object

Options for change tracking (Beta). Only applicable when 'changeTracking' is included in formats. The 'markdown' format must also be specified when using change tracking.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-change-tracking-options-mode)

changeTrackingOptions.mode

enum<string>

The mode to use for change tracking. 'default' performs a basic comparison, 'git-diff' provides a detailed diff, and 'json' compares extracted JSON data.

Available options:

`git-diff`,

`json`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-change-tracking-options-schema)

changeTrackingOptions.schema

object

Schema for JSON extraction when using 'json' mode. Defines the structure of data to extract and compare.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#body-change-tracking-options-prompt)

changeTrackingOptions.prompt

string

Prompt to use for change tracking when using 'json' mode. If not provided, the default prompt will be used.

#### Response

200

200402429500

application/json

Successful response

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-success)

success

boolean

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data)

data

object

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-markdown)

data.markdown

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-html)

data.html

string | null

HTML version of the content on page if `html` is in `formats`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-raw-html)

data.rawHtml

string | null

Raw HTML content of the page if `rawHtml` is in `formats`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-screenshot)

data.screenshot

string | null

Screenshot of the page if `screenshot` is in `formats`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-links)

data.links

string\[\]

List of links on the page if `links` is in `formats`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-actions)

data.actions

object | null

Results of the actions specified in the `actions` parameter. Only present if the `actions` parameter was provided in the request

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-actions-screenshots)

data.actions.screenshots

string\[\]

Screenshot URLs, in the same order as the screenshot actions provided.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-actions-scrapes)

data.actions.scrapes

object\[\]

Scrape contents, in the same order as the scrape actions provided.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-actions-scrapes-url)

data.actions.scrapes.url

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-actions-scrapes-html)

data.actions.scrapes.html

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-actions-javascript-returns)

data.actions.javascriptReturns

object\[\]

JavaScript return values, in the same order as the executeJavascript actions provided.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-actions-javascript-returns-type)

data.actions.javascriptReturns.type

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-actions-javascript-returns-value)

data.actions.javascriptReturns.value

any

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-metadata)

data.metadata

object

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-metadata-title)

data.metadata.title

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-metadata-description)

data.metadata.description

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-metadata-language)

data.metadata.language

string | null

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-metadata-source-url)

data.metadata.sourceURL

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-metadata-any-other-metadata)

data.metadata.<any other metadata>

string

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-metadata-status-code)

data.metadata.statusCode

integer

The status code of the page

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-metadata-error)

data.metadata.error

string | null

The error message of the page

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-llm-extraction)

data.llm\_extraction

object | null

Displayed when using LLM Extraction. Extracted data from the page following the schema defined.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-warning)

data.warning

string | null

Can be displayed when using LLM Extraction. Warning message will let you know any issues with the extraction.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-change-tracking)

data.changeTracking

object | null

Change tracking information if `changeTracking` is in `formats`. Only present when the `changeTracking` format is requested.

Show child attributes

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-change-tracking-previous-scrape-at)

data.changeTracking.previousScrapeAt

string | null

The timestamp of the previous scrape that the current page is being compared against. Null if no previous scrape exists.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-change-tracking-change-status)

data.changeTracking.changeStatus

enum<string>

The result of the comparison between the two page versions. 'new' means this page did not exist before, 'same' means content has not changed, 'changed' means content has changed, 'removed' means the page was removed.

Available options:

`new`,

`same`,

`changed`,

`removed`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-change-tracking-visibility)

data.changeTracking.visibility

enum<string>

The visibility of the current page/URL. 'visible' means the URL was discovered through an organic route (links or sitemap), 'hidden' means the URL was discovered through memory from previous crawls.

Available options:

`visible`,

`hidden`

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-change-tracking-diff)

data.changeTracking.diff

string | null

Git-style diff of changes when using 'git-diff' mode. Only present when the mode is set to 'git-diff'.

[​](https://docs.firecrawl.dev/api-reference/endpoint/scrape#response-data-change-tracking-json)

data.changeTracking.json

object | null

JSON comparison results when using 'json' mode. Only present when the mode is set to 'json'. This will emit a list of all the keys and their values from the `previous` and `current` scrapes based on the type defined in the `schema`. Example [here](https://docs.firecrawl.dev/features/change-tracking)

[Suggest edits](https://github.com/hellofirecrawl/docs/edit/main/api-reference/endpoint/scrape.mdx)
[Raise issue](https://github.com/hellofirecrawl/docs/issues/new?title=Issue%20on%20docs&body=Path:%20/api-reference/endpoint/scrape)

[Introduction](https://docs.firecrawl.dev/api-reference/introduction)
[Batch Scrape](https://docs.firecrawl.dev/api-reference/endpoint/batch-scrape)

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
      "data": {
        "markdown": "<string>",
        "html": "<string>",
        "rawHtml": "<string>",
        "screenshot": "<string>",
        "links": [\
          "<string>"\
        ],
        "actions": {
          "screenshots": [\
            "<string>"\
          ],
          "scrapes": [\
            {\
              "url": "<string>",\
              "html": "<string>"\
            }\
          ],
          "javascriptReturns": [\
            {\
              "type": "<string>",\
              "value": "<any>"\
            }\
          ]
        },
        "metadata": {
          "title": "<string>",
          "description": "<string>",
          "language": "<string>",
          "sourceURL": "<string>",
          "<any other metadata> ": "<string>",
          "statusCode": 123,
          "error": "<string>"
        },
        "llm_extraction": {},
        "warning": "<string>",
        "changeTracking": {
          "previousScrapeAt": "2023-11-07T05:31:56Z",
          "changeStatus": "new",
          "visibility": "visible",
          "diff": "<string>",
          "json": {}
        }
      }
    }