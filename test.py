import urllib.request
import urllib.parse

body = b'--BOUNDARY\r\nContent-Disposition: form-data; name="xyz_file"; filename="test.xyz"\r\n\r\n2\r\ntest\r\nH 0 0 0\r\nH 1 0 0\r\n--BOUNDARY--\r\n'
req = urllib.request.Request('http://127.0.0.1:5000/analyze-xyz', data=body, headers={'Content-Type':'multipart/form-data; boundary=BOUNDARY'})
try:
    res = urllib.request.urlopen(req)
    print("Status:", res.status)
    print("Response:", res.read().decode())
except Exception as e:
    print("Exception:", e)
    if hasattr(e, 'read'):
        print(e.read().decode())
