# utils-api-cloudflare

This python script faciliates retrieving domain data from Cloudflare via its API. Requires reference to a file containing API key data. Will retrieve live/active domains and all records for each of those domains. The resulting record sets are saved as a CSV.

The API key data file should contain the following three values in the specified order. These values are needed for the API calls to be made against your specific account. Any lines in the file that start with a hashtag (#) are treated as comments and ignored.

1. Cloudflare Account ID
2. API key owner's email address
3. API key

Example API key data file contents:
```
#CF ACC ID
7c277xxxxxxxxxxxxxxxxxxxxxx5f2da
#Email
apikeyholder@myemaildomain.com
#API key
D1A9FxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxNJ3IK
```

Usage:
```
python utils-api-cloudflare.py -k cfapikey.cfg
python utils-api-cloudflare.py -k /home/jdjalm/cfapikey.cfg -s /var/backups/cloudflare/
```

Possible future features:

1. Add option to attempt to retrieve any status domain
2. Add option to retrieve records for <=60 domains without artificial delay
3. Add option to save all records in one file
4. Support pagination on the call responses
