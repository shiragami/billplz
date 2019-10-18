# -*- coding: utf-8 -*-
# Authors: Rafiq Rahim, Syukran Hakim

import hmac
import hashlib
import requests

# Bank codes
BankCodes = {
    "PHBMMYKL": "Affin Bank Berhad",
    "BPMBMYKL": "Agrobank / Bank Pertanian Malaysia Berhad",
    "MFBBMYKL": "Alliance Bank Malaysia Berhad",
    "RJHIMYKL": "Al Rajhi Banking & Investment Corp. (M) Berhad",	
    "ARBKMYKL": "AmBank (M) Berhad",
    "BIMBMYKL": "Bank Islam Malaysia Berhad",
    "BKRMMYKL": "Bank Rakyat Malaysia Berhad",
    "BMMBMYKL": "Bank Muamalat (M) Berhad",
    "BSNAMYK1": "Bank Simpanan Nasional Berhad",
    "CIBBMYKL": "CIMB Bank Berhad",
    "CITIMYKL": "Citibank Berhad",
    "HLBBMYKL": "Hong Leong Bank Berhad",	
    "HBMBMYKL": "HSBC Bank Malaysia Berhad",
    "KFHOMYKL": "Kuwait Finance House",
    "MBBEMYKL": "Maybank / Malayan Banking Berhad",
    "OCBCMYKL": "OCBC Bank (M) Berhad",	
    "PBBEMYKL": "Public Bank Berhad",
    "RHBBMYKL": "RHB Bank Berhad",	
    "SCBLMYKX": "Standard Chartered Bank (M) Berhad",
    "UOVBMYKL": "United Overseas Bank (M) Berhad",
}


# Class for Billplz Bill
class Billplz(object):

    def __init__(self, api_key, signature_key, sandbox=True):
        if sandbox:
            self.api_url = 'https://www.billplz-sandbox.com/api'
        else:
            self.api_url = 'https://www.billplz.com/api'
        self.api_key = api_key
        self.signature_key = signature_key


    # Get bank account status
    # Query Billplz Bank Account Direct Verification Service by passing single account number argument. 
    # This API will only return latest, single matched bank account.
    def get_bank_record(self,bank_account):
        url = f'{self.api_url}/v3/bank_verification_services/{bank_account}'
        r = requests.get(url, auth=(self.api_key, ''))
        return r.json()
        
    
    # Create payout request
    def create_payout(self,payout_collection_id,bank_code,bank_account_number,identity_number,name,description,total,email):
        url = f'{self.api_url}/v4/mass_payment_instructions'
        #print(url)
        assert total<=10000 # Safety

        data = {
            "mass_payment_instruction_collection_id":payout_collection_id,
            "bank_code": bank_code,
            "bank_account_number": bank_account_number,
            "identity_number": identity_number,
            "name": name,
            "description": description,
            "total": total,
            "email": email
        }

        r = requests.post(url, data=data, auth=(self.api_key, ''))

        return r.json()


    # Create bank account for payout
    # Recipient bank details
    def create_bank_account(self,name,identity_number,bank_account_number,bank_code):
        url = f'{self.api_url}/v3/bank_verification_services'

        data = {
            "name": name,
            "id_no": identity_number,
            "acc_no": bank_account_number,
            "code": bank_code,
            "organization" : False
        }

        r = requests.post(url, data=data, auth=(self.api_key, ''))
        return r.json()


    # Create new collection 
    def create_collection(self, title):
        data = { 'title': title }
        r = requests.post(f'{self.api_url}/v3/collections', data=data, auth=(self.api_key, ''))
        try:
            out = r.json()
            collection_id = out['id']
            return collection_id
        except Exception:
            return None


    # Create bill
    def create_bill(self, collection_id, name, amount, callback_url, description, email=None, mobile=None, redirect_url=None,
                    reference_1_label=None, reference_1=None, reference_2_label=None, reference_2=None):

        assert email is not None or phone is not None, 'Email or phone must be specified'

        data = {
            'collection_id': collection_id,
            'name': name,
            'amount': amount,
            'callback_url': callback_url,
            'description': description,


            # Semi - optional parameters
            'email': email,
            'mobile': mobile,

            # Optional parameters
            'redirect_url': redirect_url,
            'reference_1_label': reference_1_label,
            'reference_1' : reference_1,
            'reference_2_label': reference_2_label,
            'reference_2' : reference_2,
        }

       
        r = requests.post(f'{self.api_url}/v3/bills', data=data, auth=(self.api_key, ''))
        try:
            out = r.json()
            bill_id = out['id']
            url = out['url']
            return bill_id, url
        except Exception:
            print(r.content)
            return None, None


    # Get bill details
    def get_bill(self, bill_id):
        r = requests.get(f'{self.api_url}/v3/bills/{bill_id}', auth=(self.api_key, ''))
        if r.status_code == 200:
            return r.json()


    # Incoherent Billplz with stupid nested parameters
    # Mode: callback/redirect
    def verify_x_signature(self, form_data, mode):
        assert mode in ('redirect','callback'), "Invalid mode"

        if mode == 'redirect':
            x_signature = form_data.pop('billplz[x_signature]')
            data = [f'billplz{k[8:-1]}{v}' for k, v in form_data.items()]
        elif mode == 'callback':
            x_signature = form_data.pop('x_signature')
            data = [f'{k}{v}' for k, v in form_data.items()]

        body = '|'.join(sorted(data)).encode('utf-8')
        sign = self.signature_key.encode('utf-8')

        # Calculate signature
        c_signature = hmac.new(sign, body, hashlib.sha256).hexdigest()
        return x_signature == c_signature
