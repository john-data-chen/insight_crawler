
[![build status](https://ci.gitlab.com/projects/5001/status.png?ref=master)](https://ci.gitlab.com/projects/5001?ref=master)
[![Codacy Badge](https://www.codacy.com/project/badge/03beb8b8b5bf46ec9f063b6115d064c8)](https://www.codacy.com)
[![codecov.io](http://codecov.io/gitlab/Huang/talos/coverage.svg?branch=master)](https://codecov.io/gitlab/ebc/insight_crawler)

## Install

   - System Package
     - sudo apt-get install libncurses5-dev
     - sudo apt-get install libxml2-dev libxslt1-dev
     - sudo apt-get install python-dev libffi-dev libssl-dev 

   - Python Package 
     - virtualenv .
     - source bin/activate 
     - pip install -r requirements.txt 
    
   - Redis(CLUSTER MODE)
     - http://redis.io/topics/quickstart
     - NOTE: Redis is only accessible within local lan

   - Known Issues
     - use 'requests[security]' or just use requests==2.5.3 instead
        - Reference:
           - http://stackoverflow.com/questions/29099404/ssl-insecureplatform-error-when-using-requests-package
     - problem while installing scrapy on osx
        - Reference:
           - https://www.google.com.tw/webhp?sourceid=chrome-instant&ion=1&espv=2&es_th=1&ie=UTF-8#q=pip+install+functools32+requirements.txt
           - https://cryptography.io/en/latest/installation/#using-your-own-openssl-on-os-x
           - https://github.com/eventmachine/eventmachine/issues/602

## Configuration

   - Configurate settings
     - cp crawler/crawler/settings.sample.py crawler/crawler/settings.py 
     - modify settings.py according to your env

   - Configuration for CloudSearch (Optional)
     - aws configure 
     - Ref: http://boto3.readthedocs.org/en/latest/guide/quickstart.html    
   - Create essential database and tables
     - python core/abstract_db.py  -c -s
 
## Execution
   - Single Mode
     - Switch to crawler/crawler and issue command as following rules
       - Rule 
         - scrapy crawl crawler -a scraper={Domain}_{Type}_Scraper, where 
           - Domain: [PTT, Facebook, Youtube]
           - Type: {Board, Article}

       - Example
         - Board Crawler
           - scrapy crawl crawler -a scraper=PTT_Board_Scraper
         - Article Crawler 
           - scrapy crawl crawler -a scraper=PTT_Article_Scraper 

   - Server Mode
     - python application.py -port 8000
     - You can then access end point as follow:
        - http://\<IP\>:\<PORT\>/list_job
        - http://\<IP\>:\<PORT\>/run  
            - start_urls : urls 
            - scraper : Facebook_Article_Scraper 
            - return_json: true or falise
        - http://\<IP\>:\<PORT\>/kill_all 

   - cluster Mode
     - python application.py -port 8000
     - API List 
        - http://tinyurl.com/p7b4lcl
