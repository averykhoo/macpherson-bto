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
    # 'https://homes.hdb.gov.sg/home/bto/details/2020-11_BTO_VEdfRDJDNDE2MDgwMjI2NDc1MjQ',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTUxNjEwODg2NjAzNzE0',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTMxNjEwODg2MzAzNTUw',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_SEdfTjFDMTVfMTYyNzU2NTE2MjYxNA',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_SEdfTjJDMTFfMTYyNzU2MzcyMjcwNQ',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_UVRfTjJDMV8xNjI3NTYzOTAyOTMz',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_VEFQX045QzE5XzE2Mjc1NjQwMjMyMjc',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_VEFQX045QzEwXzE2Mjc1NjM5NjI5MzI',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_SkVfTjJDMjZfMTYyNzU2Mzc4MzAxNA',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-08_BTO_S1dOX041QzUyXzE2Mjc1NjM4NDI3ODk',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-11_UPB_R0xfTjRDNTBfMTYzNDgxNjE2NzMwNw',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-11_UPB_S1dOX04yQzM2XzE2MzUzOTQ1MDQ5ODc',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-11_UPB_VEdfRDFDNl8xNjM0ODE4OTg0OTMz',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-11_UPB_VEdfRDNDNV8xNjM2NjE1NTA1Mzkx',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-11_UPB_WVNfTjNDMjdfMTYzNDgxOTEwNDQ1Mg',
    # 'https://homes.hdb.gov.sg/home/bto/details/2021-11_UPB_WVNfTjRDMjNfMTYzNTQxODY4NDUwMw',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-05_BTO_VFBfTjFDMjdfMTY1MDI3NDMyODA4Mw',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-05_BTO_UVRfTjZDOF8xNjUwMjc0MjY4MjEx',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-05_BTO_Qk1fTjZDNThfMTY1MDI3NDA4OTUyMA',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-05_BTO_SldfTjNDMzFfMTY1MDI3NDIwODU5Nw',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-05_BTO_WVNfTjlDM18xNjUwMjc0Mzg4ODkz',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-11_UPB_S1dOX042QzU0XzE2NjY3MDE1NjAzNzY',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-11_UPB_UVRfTjhDMV8xNjY2NzAxNjI2ODEw',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-11_UPB_SldfTjlDMjFfMTY2NjcwMDg0MTA5Mg',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-11_UPB_S1dOX04xQzQ1QV8xNjY2NzAxMjAxMDQ1',
    # 'https://homes.hdb.gov.sg/home/bto/details/2022-11_UPB_VEdfRDVDMl8xNjY2NzAxNjgwNTEz',
    'https://homes.hdb.gov.sg/home/bto/details/2023-05_BTO_QkRfTjJDMTNfMTY4MjMxNzg3MDk1OQ',
    'https://homes.hdb.gov.sg/home/bto/details/2023-05_BTO_S1dOX04xQzQ2XzE2ODIzMTc5NDgzMjc',
    'https://homes.hdb.gov.sg/home/bto/details/2023-05_BTO_VEdfRDNDMV8xNjgxNzE2NDQ4NzUy',
    'https://homes.hdb.gov.sg/home/bto/details/2023-05_BTO_VEdfRDFDOF8xNjgyMzE4MDYyMDc1',
    'https://homes.hdb.gov.sg/home/bto/details/2023-05_BTO_U0dOX04xQzIxXzE2ODIzMTgwMDIxNjI',
]

# def fetch(url, params):
#     """
#     dummy function badly mimicking javascript fetch
#     ignores most of the params
#     just exists for linting
#
#     :param url:
#     :param params:
#     :return:
#     """
#     # method = params.pop('method')
#     # headers = params.pop('headers')
#     # return requests.request(method, url, headers=headers)
#     pass
#
#
# fetch("https://resources.homes.hdb.gov.sg/nf/2021-05/bto/unit_xml/UNIT_2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng.xml",
#       {
#           "headers":        {
#               "accept":           "*/*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-site"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           None,
#           "method":         "GET",
#           "mode":           "cors",
#           "credentials":    "omit"
#       })
#
# fetch("https://resources.homes.hdb.gov.sg/nf/2021-05/bto/gl_n1c13/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng.xml",
#       {
#           "headers":        {
#               "accept":           "*/*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-site"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           None,
#           "method":         "GET",
#           "mode":           "cors",
#           "credentials":    "omit"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getSelectionProjectAvailabilityAndEthnic",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\"}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home/assets/GeoJSON/MP14_REGION_WEB_PL.geojson",
#       {
#           "headers":        {
#               "accept":           "*/*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           None,
#           "method":         "GET",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getFlatTypeUnitAvailability",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\"}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getLaunchProjectsInSameTown",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"salesMode\":\"BTO\",\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\"}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getFloorAreaAndPriceRange",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\",\"flatType\":\"2F\",\"type\":1}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getFloorAreaAndPriceRange",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\",\"flatType\":\"4\",\"type\":0}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/protected/v1/login/insertUpdateSalesApplication",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"headers\":{\"normalizedNames\":{},\"lazyUpdate\":None}}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/protected/v1/login/login",
#       {
#           "headers":        {
#               "accept":                       "application/json, text/plain, */*",
#               "accept-language":              "en-US,en;q=0.9",
#               "access-control-allow-headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
#               "access-control-allow-origin":  "https://homes.hdb.gov.sg/home",
#               "cache-control":                "no-cache",
#               "content-type":                 "application/json",
#               "pragma":                       "no-cache",
#               "sec-ch-ua":                    "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile":             "?0",
#               "sec-fetch-dest":               "empty",
#               "sec-fetch-mode":               "cors",
#               "sec-fetch-site":               "same-origin",
#               "sessionid":                    "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"loginDevice\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36\",\"sessionId\":\"LI1626000000000XXXXXXXXXXXXXXXX\"}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/public/v1/cookie/checkSPCPCookie",
#       {
#           "headers":        {
#               "accept":                       "application/json, text/plain, */*",
#               "accept-language":              "en-US,en;q=0.9",
#               "access-control-allow-headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
#               "access-control-allow-origin":  "https://homes.hdb.gov.sg/home",
#               "cache-control":                "no-cache",
#               "content-type":                 "application/json",
#               "pragma":                       "no-cache",
#               "sec-ch-ua":                    "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile":             "?0",
#               "sec-fetch-dest":               "empty",
#               "sec-fetch-mode":               "cors",
#               "sec-fetch-site":               "same-origin",
#               "sessionid":                    "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           None,
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/protected/v1/person/getPersonContactDetails",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/my-profile/buyer-overview",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           None,
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getLaunchProjectsInSameTown",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"salesMode\":\"BTO\",\"projectId\":\"2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz\"}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getFlatsSelectionTownLevel",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/my-profile/buyer-overview",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getApplicationDeadlineAndLinkByProjectId",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"projectId\":\"2021-02_BTO_VFBfTjlDMTgxNjExMTE1ODAxMDAz\"}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getApplicationDeadlineAndLinkByProjectId",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_SkVfTjJDMjYxNjExMjkwMTAwNDE5",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"projectId\":\"2021-02_UPB_SkVfTjJDMjYxNjExMjkwMTAwNDE5\"}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/protected/v1/map/getSalesApplicationProjects",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"ballotQtr\":\"2021-05\"}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home/assets/GeoJSON/MP14_REGION_WEB_PL.geojson",
#       {
#           "headers":        {
#               "accept":           "*/*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           None,
#           "method":         "GET",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/public/v1/launch/getSalesPastApplicationRate",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"  # seems to be 'LI' + timestamp + random b64
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-02_UPB_SkVfTjJDMjYxNjExMjkwMTAwNDE5",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"salesMode\":\"BTO\",\"townCode\":\"Jurong East\",\"flatTypes\":[\"2F\",\"3\",\"4\"]}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home-api/protected/v1/newFlat/getSalesApplicationStatusByProjectId",
#       {
#           "headers":        {
#               "accept":           "application/json, text/plain, */*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "content-type":     "application/json",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin",
#               "sessionid":        "LI1626000000000XXXXXXXXXXXXXXXX"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/bto/details/2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           "{\"projectId\":\"2021-05_BTO_R0xfTjFDMTNfMTYxOTUwMjc4NDU1Ng\"}",
#           "method":         "POST",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# fetch("https://homes.hdb.gov.sg/home/assets/GeoJSON/MP14_REGION_WEB_PL.geojson",
#       {
#           "headers":        {
#               "accept":           "*/*",
#               "accept-language":  "en-US,en;q=0.9",
#               "cache-control":    "no-cache",
#               "pragma":           "no-cache",
#               "sec-ch-ua":        "\"Chromium\";v=\"91\", \" Not;A Brand\";v=\"99\"",
#               "sec-ch-ua-mobile": "?0",
#               "sec-fetch-dest":   "empty",
#               "sec-fetch-mode":   "cors",
#               "sec-fetch-site":   "same-origin"
#           },
#           "referrer":       "https://homes.hdb.gov.sg/home/finding-a-flat?ballotQtr=2021-05",
#           "referrerPolicy": "strict-origin-when-cross-origin",
#           "body":           None,
#           "method":         "GET",
#           "mode":           "cors",
#           "credentials":    "include"
#       })
#
# # https://www20.hdb.gov.sg/hdbvsf/eap001.nsf/0/21MAYBTO_pdf_selection/$FILE/MACPHERSON_WEAVE.pdf
# """
# curl 'https://services2.hdb.gov.sg/webapp/BP13PPortal/BP13P_RegnDetails' \
#       -H 'Connection: keep-alive' \
#       -H 'Pragma: no-cache' \
#       -H 'Cache-Control: no-cache' \
#       -H 'sec-ch-ua: "Chromium";v="93", " Not;A Brand";v="99"' \
#       -H 'sec-ch-ua-mobile: ?0' \
#       -H 'sec-ch-ua-platform: "Windows"' \
#       -H 'Origin: https://services2.hdb.gov.sg' \
#       -H 'Upgrade-Insecure-Requests: 1' \
#       -H 'DNT: 1' \
#       -H 'Content-Type: application/x-www-form-urlencoded' \
#       -H 'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.83 Safari/537.36' \
#       -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9' \
#       -H 'Sec-Fetch-Site: same-origin' \
#       -H 'Sec-Fetch-Mode: navigate' \
#       -H 'Sec-Fetch-User: ?1' \
#       -H 'Sec-Fetch-Dest: document' \
#       -H 'Referer: https://services2.hdb.gov.sg/webapp/BP13PPortal/BP13P_Enquiry' \
#       -H 'Accept-Language: en-US,en;q=0.9' \
#       -H $'Cookie: TS01620995=01e2ec192a95925f0967943e893da2170d94a960e578a65878b3a2742063aa6778d6a558fad5a1bbabee257565d80fcce11e1e949b; PD_STATEFUL_448d0de4-a870-11ea-98b2-74fe48228f8b=%2Fwebapp; TS0173a313=01e2ec192a95925f0967943e893da2170d94a960e578a65878b3a2742063aa6778d6a558fad5a1bbabee257565d80fcce11e1e949b; rxVisitor=16262753971622AHCDP6AEV5R0O69H7AV7A418MAHB6NK; PD_STATEFUL_c1b1031a-94b2-11e5-8b7f-74fe48068c63=%2Fweb; PD_STATEFUL_c1cfe488-94b2-11e5-8b7f-74fe48068c63=%2Fweb; PD_STATEFUL_c1924bfa-94b2-11e5-8b7f-74fe48068c63=%2Fweb; _ga=GA1.3.1888794804.1626275965; PD_STATEFUL_9c33b43e-aa5b-11ea-807d-74fe48228f8b=%2Fwebapp%2FFI10AWCOMMON; PD_STATEFUL_9bf118c2-aa5b-11ea-807d-74fe48228f8b=%2Fwebapp%2FFI10AWCOMMON; PD_STATEFUL_284fe648-3fc0-11e9-bf91-74fe48228f8d=%2FFIM; AMCVS_DF38E5285913269B0A495E5A%40AdobeOrg=1; _gcl_au=1.1.908193898.1626275992; dtCookie=v_4_srv_1_sn_FC60042721E6CD8B597027AD2B969741_perc_100000_ol_0_mul_1_app-3A7703e52476c3deab_1_app-3A2710b44d13c226a6_1; rxvt=1626278091672|1626275397166; _sp_id.1902=0c4920d3-cf97-4f99-a3cc-498c3b1ea518.1626275986.1.1626276292.1626275986.878e44c0-a085-4740-abd7-6d4f364f0839; dtPC=$276289790_563h-vRUOUGKDICHCFFDHFRQJUEWJRFOSLHNLH-0e22; dtLatC=2; dtSa=true%7CD%7C-1%7CHousing%20%26%20Development%20BoardHomeMy%20Flat%20DashboardFinding%20a%20FlatMy%20ProfileCalculatorsFAQAlert%7C-%7C1626276300334%7C276289790_563%7Chttps%3A%2F%2Fhomes.hdb.gov.sg%2Fhome%2Ffinding-a-flat%3FballotQtr%3D2021-05%7CHDB%20%5Ep%20Finding%20a%20Flat%7C1626276294255%7C%7C; PD_STATEFUL_2e8689d2-98e7-11ea-8e95-74fe48228f8b=%2Fwebapp%2FBF08CESS; AMWEBJCT\u0021%2FFIM\u0021JSESSIONID=0000xhN3yVPFK4-7lecSGKTpxNa:f4b0030e-7b2e-4176-a1bb-08648f38e718:b9baba69-8cd8-429d-8e48-252e6fe86a37:95a67e95-61a8-4f52-ba3c-4046b1ca6167; PD_STATEFUL_97f5805c-edce-11eb-ae11-74fe48342003=%2Fwebapp%2FFI10PPORTAL; info-msg-2183B92C5216FAED482585110032624D=true; info-msg-0D3E28920507F1714825875600105539=true; info-msg-0867254671B198BA482583590030C3FF=true; JSESSIONIDP1=0000_vmPFOIBfzPdfvDqziF9P3P:19nr4sk5u; SPCP=SP; AMWEBJCT\u0021%2FFIM\u0021https%3A%2F%2Fservices2.hdb.gov.sg%2FFIM%2Fsps%2FHDBEserviceProd%2Fsaml20FIMSAML20=uuid3c5eb2a3-017c-1007-be7e-ea5cf4d74e5f; HDB-RP-S-SESSION-ID=1_mu0/66BurOQLZq68fYfK4kiHDmnbBT5s6dlMilYRquWibiOEhqM=_AAAAAAA=_N/5DvbfAEGJ8ISfuCmhVdh6WZN0=; JSESSIONIDAIASP1=0000E3lJ-1DStKl5bdtKfy3np6B:1d71i54uh; persona=011,046,011; PD_STATEFUL_69cb8492-edce-11eb-8651-74fe48228f8b=%2Fwebapp%2FFI10PPORTAL; TS01170d4d=01e2ec192ac00d6c171c5913b7de84f2bab7d87a4aed92be96b9eb3721f826477ef49d3463fb190e6d16c98b6a9d44c8fc2a076aea; sessionTS=16331011998271633100412516; AMCV_DF38E5285913269B0A495E5A%40AdobeOrg=1075005958%7CMCIDTS%7C18902%7CMCMID%7C01636302418336544857871012306330678798%7CMCAAMLH-1626880786%7C3%7CMCAAMB-1633100359%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1633108410s%7CNONE%7CvVersion%7C4.4.1; SPINS_ActTS=1633101212000; isg003=\u0021abrvVTrJNuXSSEHNhFRxISnxSW3SmcKY7RsLfS+6AbCPDGRfqDVyXtHfRMGhR0lH7pS1nKq0g0CXoTk=' \
#       --data-raw 'numregn=4401189A' \
#       --compressed
# """
# fetch("https://services2.hdb.gov.sg/webapp/BP13PPortal/BP13P_RegnDetails", {
#     "referrer":       "https://services2.hdb.gov.sg/webapp/BP13PPortal/BP13P_Enquiry",
#     "referrerPolicy": "strict-origin-when-cross-origin",
#     "body":           "numregn=4401189A",
#     "method":         "POST",
#     "mode":           "cors",
#     "credentials":    "include",
#     "headers":        {
#         "accept":                    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
#         "accept-language":           "en-US,en;q=0.9",
#         "cache-control":             "no-cache",
#         "content-type":              "application/x-www-form-urlencoded",
#         "pragma":                    "no-cache",
#         "sec-ch-ua":                 "\"Chromium\";v=\"93\", \" Not;A Brand\";v=\"99\"",
#         "sec-ch-ua-mobile":          "?0",
#         "sec-ch-ua-platform":        "\"Windows\"",
#         "sec-fetch-dest":            "document",
#         "sec-fetch-mode":            "navigate",
#         "sec-fetch-site":            "same-origin",
#         "sec-fetch-user":            "?1",
#         "upgrade-insecure-requests": "1",
#     }})

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
                          f'UNIT_{month}_{project_type}_{b64_chunk}.xml',
                          verify=False)
        if r1.status_code != 200:
            r1 = requests.get(f'https://resources.homes.hdb.gov.sg/nf/{month}/upcoming-bto/'
                              f'unit_xml/'
                              f'UNIT_{month}_{project_type}_{b64_chunk}.xml',
                              verify=False)
        if r1.status_code == 200:
            with open(f'hdb_downloads/{os.path.basename(r1.url)}', 'wb') as f:
                f.write(r1.content)

        r2 = requests.get(f'https://resources.homes.hdb.gov.sg/nf/{month}/bto/'
                          f'{town.lower()}_{project_code.lower().rstrip("_")}/'
                          f'{month}_{project_type}_{b64_chunk}.xml',
                          verify=False)
        if r2.status_code != 200:
            r2 = requests.get(f'https://resources.homes.hdb.gov.sg/nf/{month}/upcoming-bto/'
                              f'{town.lower()}_{project_code.lower().rstrip("_")}/'
                              f'{month}_{project_type}_{b64_chunk}.xml',
                              verify=False)
        if r2.status_code == 200:
            with open(f'hdb_downloads/{os.path.basename(r2.url)}', 'wb') as f:
                f.write(r2.content)

        # map_url = 'https://resources.homes.hdb.gov.sg/nf/2021-02/upcoming-bto/qt_n2c1/townmap/townmap_qt_n2c1.jpg'
        r3 = requests.get(f'https://resources.homes.hdb.gov.sg/nf/{month}/'
                          f'upcoming-bto/{town.lower()}_{project_code.lower()}/'
                          f'townmap/townmap_{town.lower()}_{project_code.lower()}.jpg',
                          verify=False)
        if r3.status_code != 200:
            r3 = requests.get(f'https://resources.homes.hdb.gov.sg/nf/{month}/'
                              f'upcoming-bto/{town.lower()}_{project_code.lower().rstrip("_")}/'
                              f'townmap/townmap_{town.lower()}_{project_code.lower().rstrip("_")}.jpg',
                              verify=False)
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
