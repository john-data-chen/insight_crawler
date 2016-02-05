from flask import *
import json
from bson import json_util
app = Flask(__name__)
from subprocess import Popen, PIPE, STDOUT, check_call
import os
from flask import request
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from pprintpp  import pprint  as pp
#from signal import CTRL_BREAK_EVENT
import datetime
import socket
import copy
import string
import random
from crawler import settings
import optparse
from pprintpp import pprint as pp
import requests


process_pool = {}
max_process = 2
running_process_dict = {}
json_tmp_dir = "/tmp/"
job_id_accu = 0

if settings.MODE == 'CLUSTER':
    import redis
    # http://xiaorui.cc/2014/11/10/%E4%BD%BF%E7%94%A8redis-py%E7%9A%84%E4%B8%A4%E4%B8%AA%E7%B1%BBredis%E5%92%8Cstrictredis%E6%97%B6%E9%81%87%E5%88%B0%E7%9A%84%E5%9D%91/
    # Pagination https://github.com/zatosource/zato-redis-paginator
    pool = redis.ConnectionPool(host = settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
    r = redis.StrictRedis(connection_pool=pool)
    #r = redis.StrictRedis(host = settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

@app.route("/")
def hello():
    return "Hello World!"

def update_finished_time(job_id=None):
    if job_id is None:
        return "error"
    global process_pool
    process_pool[job_id]["close_time"] =datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

def get_running_process():
    process_pool = update_process_status()
    running_process_list = []
    for job_id, _process in process_pool.items():
        if process_pool[job_id]["status"] == "running":
            running_process_list.append(job_id)
    return running_process_list


@app.route("/update_process_status")
def update_process_status():
    global process_pool
    result = {}
    for job_id, _process in process_pool.items():
        if process_pool[job_id]["status"] in ["finished", "killed"]:
            continue
        if process_pool[job_id]["process"].poll() is None:
            # still running
            continue
        else:
            # process has been finished but w/o update status
            process_pool[job_id]["status"] = "finished"
            update_finished_time(job_id)
            process_pool[job_id]["return_code"] = process_pool[job_id]["process"].returncode
            del process_pool[job_id]["process"]
    return process_pool


@app.route("/list_job")
def list_job():
    #update_process_status()
    process_pool = update_process_status()
    result = {}
    args = request.args
    job_id = int(request.args.get('job_id', -1))
    if job_id == -1:
        # list all process
        result["result"] = []
        for job_id , _process in process_pool.items():
            if process_pool[job_id]["status"] in ["finished", "killed"]:
                result["result"].append(_process)
            else:
                _ = copy.deepcopy(_process)
                del _["process"]
                result["result"].append(_)
            #result["job_id"] = update_process_status()

    elif job_id in process_pool:
        #result =  process_pool[job_id]
        #result["status"] =  process_pool[job_id]["status"]
        # check if process still running
        _ = copy.deepcopy(process_pool[job_id])
        if "process" in _ and process_pool[job_id]["process"].poll() == None:
            # if still running return still running
            del _["process"]
        result["result"] = _
    elif settings.MODE == "CLUSTER":
        try:
            host = r.hget('jid_host_mapping', str(job_id))
            if host is None:
                result["result"] = "not exists"
            else:
                req_url = 'http://%s/list_job?job_id=%s' % (host, str(job_id))
                req = requests.get(req_url, timeout=3)
                result["result"] = req.json()["result"]
        except Exception as e:
            print str(e)
            result["result"] = str(e)
    else:
        result["result"] = "not exists"
    return generate_json(result)


@app.route("/kill")
def kill():
    generate_json(kill_job_id())


def kill_job_id(job_id=None):
    global process_pool
    if job_id is None:
        #args = request.args
        #job_id = args["job_id"]
        job_id = int(request.args.get('job_id', -1))
        if job_id == -1:
            return ""
    if job_id not in process_pool:
        return {"result": "no such process"}
    if process_pool[job_id]["status"] in ["finished" , "killed"]:
        return process_pool[job_id]
    else:
        if process_pool[job_id]["process"].poll() is None:
            # print "case1"
            # still running
            pid = process_pool[job_id]['pid']
            Popen("kill -9 %s" % pid, shell=True)
            process_pool[job_id]["return_code"] = "-9"
            process_pool[job_id]["status"] = "killed"
        else:
            # print "case2"
            # finished but not updated
            process_pool[job_id]["return_code"] = process_pool[job_id]["process"].returncode
            process_pool[job_id]["status"] = "finished"
        update_finished_time(job_id)
        del process_pool[job_id]["process"]
        return process_pool[job_id]
    return ""


@app.route("/kill_all")
def kill_all():
    #global process_pool
    result = {}
    result["result"] = []
    running_job_id_list = get_running_process()
    for job_id in running_job_id_list:
        #kill(job_id)
        #pp(kill_job_id(job_id))
        result["result"].append(kill_job_id(job_id))

    """
    for job_id, _process in process_pool.items():
        Popen("kill -9 %s" % pid, shell=True)
        #process_pool[pid].terminate()
        #process_pool[pid].send_signal(CTRL_BREAK_EVENT)
        #del process_pool[pid]
        process_pool[pid]["status"] = "finished"
    return list_job()
    """
    return generate_json(result)

@app.route("/run")
def run():
    """
    process = CrawlerProcess(get_project_settings())

    # 'followall' is the name of one of the spiders of the project.
    process.crawl('crawler', scraper='Facebook_Article_Scraper')
    process.start() # the script will block here until the crawling is finished
    """
    result = {}
    global counter
    global process_list
    global max_process

    scraper = request.args.get('scraper', 'Facebook_Article_Scraper')
    return_json = int(request.args.get('return_json', 0))
    start_urls = request.args.get('start_urls', '')

    if len(get_running_process()) < max_process:
        #server = Popen('uname -a', shell=True, stdout=PIPE)
        FNULL = open("/dev/null", 'w')
        cmd = "cd crawler && scrapy crawl crawler -a scraper='%s' -a CRAWLER_COUNT=1 -a CRAWLER_ID=0 --nolog" % scraper
        if start_urls != "":
            cmd += " -a start_urls=%s" % start_urls
        if return_json != 0:
            def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
                return ''.join(random.choice(chars) for _ in range(size))
            tmp_filename = id_generator() + ".json"
            tmp_json_path = json_tmp_dir + tmp_filename
            cmd += " -o %s -t json" % (tmp_json_path)
        process = Popen(cmd, stdout=FNULL, shell=True)
        #server = Popen("ls -al", stdout=FNULL, shell=True)
        job_id = get_job_id()
        process_pool[job_id] = {}
        process_pool[job_id]["job_id"] = job_id
        process_pool[job_id]["status"] = "running"
        process_pool[job_id]["process"] = process
        process_pool[job_id]["scraper"] = scraper
        process_pool[job_id]["pid"] = process.pid
        process_pool[job_id]["start_time"] = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        process_pool[job_id]["server_ip"] = socket.gethostbyname(socket.gethostname())
        if return_json != 0:
            process_pool[job_id]["json_path"] = tmp_json_path
        #process_pool[job_id]["meta"]["job_id"] = job_id
        process_pool[job_id]["cmd"] = cmd

        if settings.MODE == "CLUSTER":
            # IT MAY TAKE A WHILE
            r.hset('jid_host_mapping',str(job_id), process_pool[job_id]["server_ip"] + ":" + str(port))

        result["job_id"] = job_id
        if return_json == 1:
            server.communicate()
            with open(tmp_json_path) as data_file:
                data = json.load(data_file)
                result["result"] = data
    else:
        result["result"] = "process count exceed max_process "
    return generate_json(result)


def get_job_id():
    try:
        if settings.MODE == 'CLUSTER':
            global r
            idx = r.incr('')
            return idx
    except Exception as e:
        print str(e)
    global job_id_accu
    job_id_accu += 1
    return job_id_accu

def generate_json(f):
    result = json.dumps(f, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None,
    indent=True, separators=None, encoding="utf-8", sort_keys=False, default=json_util.default)
    resp = make_response(result)
    if request.headers.get('Accept', '').find('application/json') > -1:
        resp.mimetype = 'application/json'
    else:
        resp.mimetype = 'text/plain'
    return resp

if __name__ == "__main__":
    parser = optparse.OptionParser()
    default_port = 8000
    parser.add_option("-P", "--port",
                      help="Port for the Flask app " + \
                      "[default %s]" % default_port,
                      default=default_port)
    options, _ = parser.parse_args()
    #global port
    port=int(options.port)
    if settings.MODE == "CLUSTER":
        r.hset('server_list', socket.gethostbyname(socket.gethostname()) + ":" + str(port), "1")
    app.run(host='0.0.0.0',  port=port, threaded=True, debug=True)

"""
from dmoz_spider import DmozSpider

# scrapy api
from scrapy import signals, log
from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy.settings import Settings

def spider_closing(spider):
    #Activates on spider closed signal
    log.msg("Closing reactor", level=log.INFO)
    reactor.stop()

log.start(loglevel=log.DEBUG)
settings = Settings()

# crawl responsibly
settings.set("USER_AGENT", "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36")
crawler = Crawler(settings)

# stop reactor when spider closes
crawler.signals.connect(spider_closing, signal=signals.spider_closed)

crawler.configure()
crawler.crawl(DmozSpider())
crawler.start()
reactor.run()
"""

