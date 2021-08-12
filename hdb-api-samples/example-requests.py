import base64
import datetime
import os

import requests
from tabulate import tabulate

bto_details_urls = [
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_SEdfTjFDMTUxNjExMjg5NTAwNDE2',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_SEdfTjJDMTExNjExMjg5ODA0MjY4',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_SkVfTjJDMjYxNjExMjkwMTAwNDE5',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_VEFQX045QzEwMTYxMTI5MTAwMDQ2Mw',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_S1dOX041QzUyMTYxMTI5MDQwMDUxOQ',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_UVRfTjJDMTE2MTEyOTA3MDA0MDY',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_VEFQX045QzE5MTYxMTI5MTMwMzk2NQ',
    'https://homes.hdb.gov.sg/home/bto/details/2020-11_BTO_VEdfRDJDNDE2MDgwMjI2NDc1MjQ',
    'https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTUxNjEwODg2NjAzNzE0',
    'https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz',
    'https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTMxNjEwODg2MzAzNTUw',
    'https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng',
    'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_SEdfTjFDMTVfMTYyNzU2NTE2MjYxNA',
    'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_SEdfTjJDMTFfMTYyNzU2MzcyMjcwNQ',
    'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_UVRfTjJDMV8xNjI3NTYzOTAyOTMz',
    'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_VEFQX045QzE5XzE2Mjc1NjQwMjMyMjc',
    'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_VEFQX045QzEwXzE2Mjc1NjM5NjI5MzI',
    'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_SkVfTjJDMjZfMTYyNzU2Mzc4MzAxNA',
    'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_S1dOX041QzUyXzE2Mjc1NjM4NDI3ODk',
]


def fetch(url, params):
    """
    dummy function badly mimicking javascript fetch
    ignores most of the params
    just exists for linting

    :param url:
    :param params:
    :return:
    """
    # method = params.pop('method')
    # headers = params.pop('headers')
    # return requests.request(method, url, headers=headers)
    pass


fetch("https://resources.homes.hdb.gov.sg/nf/2021-05/bto/unit_xml/UNIT_2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng.xml",
      {
          "headers":        {
              "accept":           "*/*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-site"
          },
          "referrer":       "https://homes.hdb.gov.sg/",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           None,
          "method":         "GET",
          "mode":           "cors",
          "credentials":    "omit"
      })

fetch("https://resources.homes.hdb.gov.sg/nf/2021-05/bto/gl_n1c13/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng.xml",
      {
          "headers":        {
              "accept":           "*/*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-site"
          },
          "referrer":       "https://homes.hdb.gov.sg/",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           None,
          "method":         "GET",
          "mode":           "cors",
          "credentials":    "omit"
      })

fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getSelectionProjectAvailabilityAndEthnic",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\"}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home/assets/GeoJSON/MP14_REGION_WEB_PL.geojson",
      {
          "headers":        {
              "accept":           "*/*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           None,
          "method":         "GET",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getFlatTypeUnitAvailability",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\"}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getLaunchProjectsInSameTown",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"salesMode\":\"BTO\",\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\"}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getFloorAreaAndPriceRange",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\",\"flatType\":\"2F\",\"type\":1}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getFloorAreaAndPriceRange",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\",\"flatType\":\"4\",\"type\":0}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/protected/v1/login/insertUpdateSalesApplication",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"headers\":{\"normalizedNames\":{},\"lazyUpdate\":None}}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/protected/v1/login/login",
      {
          "headers":        {
              "accept":                       "application/json, text/plain, */*",
              "accept-language":              "en-US,en;q=0.9",
              "access-control-allow-headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
              "access-control-allow-origin":  "https://homes.hdb.gov.sg/home",
              "cache-control":                "no-cache",
              "content-type":                 "application/json",
              "pragma":                       "no-cache",
              "sec-ch-ua":                    "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile":             "?0",
              "sec-fetch-dest":               "empty",
              "sec-fetch-mode":               "cors",
              "sec-fetch-site":               "same-origin",
              "sessionid":                    "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"loginDevice\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36\",\"sessionId\":\"LI1626000000000XXXXXXXXXXXXXXXX\"}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/public/v1/cookie/checkSPCPCookie",
      {
          "headers":        {
              "accept":                       "application/json, text/plain, */*",
              "accept-language":              "en-US,en;q=0.9",
              "access-control-allow-headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
              "access-control-allow-origin":  "https://homes.hdb.gov.sg/home",
              "cache-control":                "no-cache",
              "content-type":                 "application/json",
              "pragma":                       "no-cache",
              "sec-ch-ua":                    "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile":             "?0",
              "sec-fetch-dest":               "empty",
              "sec-fetch-mode":               "cors",
              "sec-fetch-site":               "same-origin",
              "sessionid":                    "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           None,
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/protected/v1/person/getPersonContactDetails",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/my-profile/buyer-overview",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           None,
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getLaunchProjectsInSameTown",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"salesMode\":\"BTO\",\"projectId\":\"2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz\"}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getFlatsSelectionTownLevel",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/my-profile/buyer-overview",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getApplicationDeadlineAndLinkByProjectId",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"projectId\":\"2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz\"}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getApplicationDeadlineAndLinkByProjectId",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_SkVfTjJDMjYxNjExMjkwMTAwNDE5",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"projectId\":\"2021-02_UPB_SkVfTjJDMjYxNjExMjkwMTAwNDE5\"}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/protected/v1/map/getSalesApplicationProjects",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"ballotQtr\":\"2021-05\"}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home/assets/GeoJSON/MP14_REGION_WEB_PL.geojson",
      {
          "headers":        {
              "accept":           "*/*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           None,
          "method":         "GET",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getSalesPastApplicationRate",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"  # seems to be 'LI' + timestamp + random b64
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_SkVfTjJDMjYxNjExMjkwMTAwNDE5",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"salesMode\":\"BTO\",\"townCode\":\"Jurong East\",\"flatTypes\":[\"2F\",\"3\",\"4\"]}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getSalesApplicationStatusByProjectId",
      {
          "headers":        {
              "accept":           "application/json, text/plain, */*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "content-type":     "application/json",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin",
              "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\"}",
          "method":         "POST",
          "mode":           "cors",
          "credentials":    "include"
      })

fetch("https://homes.hdb.gov.sg/home/assets/GeoJSON/MP14_REGION_WEB_PL.geojson",
      {
          "headers":        {
              "accept":           "*/*",
              "accept-language":  "en-US,en;q=0.9",
              "cache-control":    "no-cache",
              "pragma":           "no-cache",
              "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
              "sec-ch-ua-mobile": "?0",
              "sec-fetch-dest":   "empty",
              "sec-fetch-mode":   "cors",
              "sec-fetch-site":   "same-origin"
          },
          "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
          "referrerPolicy": "strict-origin-when-cross-origin",
          "body":           None,
          "method":         "GET",
          "mode":           "cors",
          "credentials":    "include"
      })

if __name__ == '__main__':
    rows = []
    for url in bto_details_urls:
        path_segment = url.rsplit('/', 1)[-1]
        month, project_type, b64_chunk = path_segment.split('_')
        town, rest = base64.b64decode(b64_chunk + '===').decode('ascii').split('_', 1)
        project_code, timestamp = rest[:-13], rest[-13:]

        # month = '2021-08'
        # project_type = 'BTO'

        r1 = requests.get(f'https://resources.homes.hdb.gov.sg/nf/{month}/bto/'
                          f'unit_xml/'
                          f'UNIT_{month}_{project_type}_{b64_chunk}.xml')
        if r1.status_code == 200:
            with open(f'hdb_downloads/{os.path.basename(r1.url)}', 'wb') as f:
                f.write(r1.content)

        r2 = requests.get(f'https://resources.homes.hdb.gov.sg/nf/{month}/bto/'
                          f'{town.lower()}_{project_code.lower().rstrip("_")}/'
                          f'{month}_{project_type}_{b64_chunk}.xml')
        if r2.status_code == 200:
            with open(f'hdb_downloads/{os.path.basename(r2.url)}', 'wb') as f:
                f.write(r2.content)

        # map_url = 'https://resources.homes.hdb.gov.sg/nf/2021-02/upcoming-bto/qt_n2c1/townmap/townmap_qt_n2c1.jpg'
        r3 = requests.get(f'https://resources.homes.hdb.gov.sg/nf/{month}/'
                          f'upcoming-bto/{town.lower()}_{project_code.lower()}/'
                          f'townmap/townmap_{town.lower()}_{project_code.lower()}.jpg')
        if r3.status_code == 200:
            with open(f'hdb_downloads/{os.path.basename(r3.url)}', 'wb') as f:
                f.write(r3.content)

        rows.append((url,
                     month,
                     project_type,
                     town,
                     project_code,
                     datetime.datetime.utcfromtimestamp(int(timestamp) / 1000),
                     r1.status_code,
                     r2.status_code,
                     r3.status_code,
                     ))

        # with open(r3.url.rsplit('/')[-1], 'wb') as f:
        #     f.write(r3.content)

    print(tabulate(rows, headers=['url', 'month', 'type', 'town', 'code', 'timestamp', 'xml1', 'xml2', 'jpg']))
