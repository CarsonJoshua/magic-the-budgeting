import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import requests
import time
import yaml

#@author Joshua Carson
#quite a bit of code taken from the following tutorials
#https://developers.google.com/sheets/api/quickstart/python

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# The ID and range of a sample spreadsheet.

with open("config.yml", "r") as ymlfile:
  cfg = yaml.safe_load(ymlfile)
  # print(cfg)

DECK_NAME = cfg["deck_name"]
SPREADSHEET_ID = cfg["spreadsheet_id"]
CARD_RANGE = DECK_NAME + "!A2:B"


def main():
  # print(fetch_card_prices([["Alloy Anim"]]))
  # return
  #TODO file read for sheet id and rang
  sheet = get_sheet(get_credentials())
  cards = fetch_card_names(sheet)
  cards = fetch_card_prices(cards)
#   print(cards)
#   return
  upload_card_prices(cards, sheet);
  return
  

def get_credentials():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())
  return creds

def get_sheet(creds):
  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    return service.spreadsheets()
  except HttpError as err:
    print(err)

def fetch_card_names(sheet):
    result = (
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=CARD_RANGE)
        .execute()
    )
    # return result
    return result.get("values", [])


def fetch_card_prices(cards):
#   print(cards)
  for card in cards:
    # print(card)
    if len(card) == 2:
      continue
    time.sleep(0.100)
    while len(card) < 2:
      card.append(0)
    response = requests.get("https://api.scryfall.com/cards/search?unique=prints&order=usd&q="+card[0])
    # if response.status_code == 404:
    #   time.sleep(0.100)
    #   response = requests.get("https://api.scryfall.com/cards/named?fuzzy="+card[0])
    #   print(response.json())
    #   return

      
    # with open("out.json", "w") as outfile:
    #   outfile.write(json.dumps(response.json()))
    if response.status_code == 404:
      card[1] = 'ERR: Card Not Found'
    else:
      printings = response.json()["data"]
      printings.reverse();
      price = None
      index = 0
      while index < len(printings) and price == None:
        price = printings[index]["prices"]["usd"]
        index += 1
      if price == None:
        card[1] = "ERR: Price Not Found"
      else:
        card[1] = price
    #   card[1] = response.json()["prices"]["usd"]
#   print(cards)
  return cards

#   req = {
#     "identifiers":[
#       {
#         "name": "Palladium Myr"
#       }
#     ]
#   }
#   response = requests.post("https://api.scryfall.com/cards/collection", json=req)
#   print(response.json())

#   prices = []
#   for card in cards:
#     time.sleep(0.100)#TODO could be more efficient, only waiting between requests,
#     response = requests.get("https://api.scryfall.com/cards/named?fuzzy="+card[0])
#     if response.status_code == 404:
#       prices.append('ERR')
#     else:
#       prices.append(response.json()["prices"]["usd"])
#   return prices

def upload_card_prices(cards, sheet):
  
  body = {
       'value_input_option': 'USER_ENTERED',
       'data': [
       {
           'majorDimension': 'ROWS',
           'range': CARD_RANGE,
           'values': cards,
       },
   ]}
  response = sheet.values().batchUpdate(spreadsheetId = SPREADSHEET_ID, body = body).execute()
  # print(response)
  return

#   sheet.values().update(spreadsheetId=SPREADSHEET_ID, range=CARD_RANGE, valueInputOption="USER_ENTERED", body=body).execute()
  return

if __name__ == "__main__":
  main()