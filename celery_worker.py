#!/usr/bin/env python
import os
from app import create_celery_app
from app.models import get_currbj_time, mBus, mStation
from datetime import datetime, timedelta

celery = create_celery_app()


@celery.task()
def cleangps(inputdata):
    nowtime = get_currbj_time()
    print('11111111')

    #transfer to datetime object
    strprefix = nowtime.strftime('%Y-%m-%dT')

    busrec = mBus.query.all()
    for item in busrec:
        stationrec = item.stations.all()
        tohmstartStation = None
        tohmendStation = None
        tocmpstartStation = None
        tocmpendStation = None
        for item2 in stationrec:
            #find to home start and to company start station
            if item2.dirtocompany == True:
                if tocmpstartStation is None:
                    tocmpstartStation = item2
                elif item2.time < tocmpstartStation.time:
                    tocmpstartStation = item2

                if tocmpendStation is None:
                    tocmpendStation = item2
                elif item2.time > tocmpendStation.time:
                    tocmpendStation = item2
            else:
                if tohmstartStation is None:
                    tohmstartStation = item2
                elif item2.time < tohmstartStation.time:
                    tohmstartStation = item2

                if tohmendStation is None:
                    tohmendStation = item2
                elif item2.time > tohmendStation.time:
                    tohmendStation = item2
        #clean gps data 30 min ahead of bus start time
        nowtime = nowtime.replace(tzinfo=None)

        print(nowtime)
        
        #clean gps data 30 minutes before shuttlbus time or 60 minutes after shuttlebus time
        if tocmpstartStation is not None:
            tocmptime = tocmpstartStation.time.strftime('%H:%M:%S')
            tocmptimeobj = datetime.strptime(strprefix+tocmptime, '%Y-%m-%dT%H:%M:%S')
            print(item.name)
            print(tocmptimeobj)
            if ((nowtime >= (tocmptimeobj-timedelta(minutes=30)))
                and (nowtime <= (tocmptimeobj-timedelta(minutes=10)))):
                item.curridx = 0xFF
                print('clean cmp start ')
        if tocmpendStation is not None:
            tocmptime = tocmpendStation.time.strftime('%H:%M:%S')
            tocmptimeobj = datetime.strptime(strprefix+tocmptime, '%Y-%m-%dT%H:%M:%S')
            print(item.name)
            print(tocmptimeobj)
            if ((nowtime >= (tocmptimeobj+timedelta(minutes=60)))
                and (nowtime <= (tocmptimeobj+timedelta(minutes=80)))):
                item.curridx = 0xFF
                print('clean cmp end ')
        if tohmstartStation is not None:
            tohmtime = tohmstartStation.time.strftime('%H:%M:%S')
            tohmtimeobj = datetime.strptime(strprefix+tohmtime, '%Y-%m-%dT%H:%M:%S')
            print(item.name)
            print(tohmtimeobj)
            if ((nowtime >= (tohmtimeobj-timedelta(minutes=30)))
                and (nowtime <= (tohmtimeobj-timedelta(minutes=10)))):
                item.curridx = 0xFF
                print('clean hm start')
        if tohmendStation is not None:
            tohmtime = tohmendStation.time.strftime('%H:%M:%S')
            tohmtimeobj = datetime.strptime(strprefix+tohmtime, '%Y-%m-%dT%H:%M:%S')
            print(item.name)
            print(tohmtimeobj)
            if ((nowtime >= (tohmtimeobj+timedelta(minutes=60)))
                and (nowtime <= (tohmtimeobj+timedelta(minutes=80)))):
                item.curridx = 0xFF
                print('clean hm end')

'''
@celery.task()
def calcbusdata(inputdata):
'''


#app = create_app(os.getenv('FLASK_CONFIG') or 'default')
#app.app_context().push()