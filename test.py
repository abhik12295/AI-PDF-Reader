import jwt

token = "eyJhbGciOiJIUzI1NiIsImtpZCI6Ik5pWmxxSE1LclJpdXcxckkiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3FmcWN1amN4dnF1Y3FxeHdmb2FrLnN1cGFiYXNlLmNvL2F1dGgvdjEiLCJzdWIiOiI3OTAyZDcyZi1lYThlLTQ2MDctODUzMC02MDAwN2Q0ZWE5Y2EiLCJhdWQiOiJhdXRoZW50aWNhdGVkIiwiZXhwIjoxNzQ2MjQ1OTQ5LCJpYXQiOjE3NDYyNDIzNDksImVtYWlsIjoiYWsyc3BlY2lhbEBnbWFpbC5jb20iLCJwaG9uZSI6IiIsImFwcF9tZXRhZGF0YSI6eyJwcm92aWRlciI6ImVtYWlsIiwicHJvdmlkZXJzIjpbImVtYWlsIl19LCJ1c2VyX21ldGFkYXRhIjp7ImVtYWlsIjoiYWsyc3BlY2lhbEBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwicGhvbmVfdmVyaWZpZWQiOmZhbHNlLCJzdWIiOiI3OTAyZDcyZi1lYThlLTQ2MDctODUzMC02MDAwN2Q0ZWE5Y2EifSwicm9sZSI6ImF1dGhlbnRpY2F0ZWQiLCJhYWwiOiJhYWwxIiwiYW1yIjpbeyJtZXRob2QiOiJwYXNzd29yZCIsInRpbWVzdGFtcCI6MTc0NjI0MjM0OX1dLCJzZXNzaW9uX2lkIjoiNjMxNjAzOWYtYmZmZi00NjhmLWEwY2MtMWM3NmZjMGJkZGU1IiwiaXNfYW5vbnltb3VzIjpmYWxzZX0.nTCWxQDViwSViOtomUuEFIDfDqLylfmLZXXTd4DA8R0"
JWT_KEY = "CqAlI0Bu2uYraQUuM6RyvDfw3cu+NuR6wQRhVsJxHYNqvYMLdrxxf6bZdXOzJIFkiQItldtnmEI4A3Iv+FTgYw=="
try:
    payload = jwt.decode(
        token,
        JWT_KEY,
        algorithms=['HS256'],
        options={'verify_signature': False, 'verify_aud': False, 'verify_exp': False}
    )
    print(payload)
except jwt.PyJWTError as e:
    print(f"JWT Error: {str(e)}")

'''
{'iss': 'https://qfqcujcxvqucqqxwfoak.supabase.co/auth/v1', 
'sub': '7902d72f-ea8e-4607-8530-60007d4ea9ca', 'aud': 'authenticated', 
'exp': 1746245949, 'iat': 1746242349, 'email': 'ak2special@gmail.com', 'phone': '', 
'app_metadata': {'provider': 'email', 'providers': ['email']}, 
'user_metadata': {'email': 'ak2special@gmail.com', 'email_verified': True, 'phone_verified': False, 
'sub': '7902d72f-ea8e-4607-8530-60007d4ea9ca'}, 'role': 'authenticated', 
'aal': 'aal1', 'amr': [{'method': 'password', 'timestamp': 1746242349}], 
'session_id': '6316039f-bfff-468f-a0cc-1c76fc0bdde5', 'is_anonymous': False}
'''