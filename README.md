# fin_crawler2
financial crawlers


# Prepare
1. install chromedriver
2. install selenium
```
pip install selenium
```

# Rakuten Crawler
## usage
```
python rakuten_crawler.py YOUR-USER-ID YOUR-PASSWORD [--outdir <dir>]
```

# VIEW Card Crawler
## usage
```
python view_crawler.py YOUR-USER-ID YOUR-PASSWORD [--outdir <dir>]
```

# AEON Card Crawler
## usage
```
python aeon_crawler.py YOUR-USER-ID YOUR-PASSWORD [--outdir <dir>]
```

# Password Encrypt Hint(for Linux)
## prepare(generate key pair)
``
ssh-keygen -t rsa -b 4096 -m PEM
```
```
ssh-keygen -t rsa
ssh-keygen -e -m PEM -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pem
ssh-keygen -e -m PKCS8 -f ~/.ssh/id_rsa.pub  > ~/.ssh/id_rsa.pub.pem
```

## generate encrypted password file
```
echo "yourpassword" | openssl rsautl -encrypt -pubin -inkey ~/.ssh/id_rsa.pub.pem -out secretfile
```

## use password file
```
echo `openssl rsautl -decrypt -inkey ~/.ssh/id_rsa -in secretfile`
```

## see also
https://qiita.com/kugyu10/items/b27d99f6df67a3b6c348
https://www.masatom.in/pukiwiki/Linux/%25B8%25F8%25B3%25AB%25B8%25B0%25B0%25C5%25B9%25E6/
