from tornado import httpclient



def main():
  http_client = httpclient.HTTPClient()
  for i in range(5):
    try:
      response = http_client.fetch("http://localhost:64839/")
      print response.body
    except httpclient.HTTPError, e:
      print "Error:", e
  
if __name__ == '__main__':
  main()