import requests
import os
import datetime
import getpass
import re
import time

session = requests.Session()

try:
    username = os.environ['simon_user']
except KeyError:
    print('Enviroment variable simon_user')
    username = input('Simon Username: ')

try:
    password = os.environ['simon_password']
except KeyError:
    print('Enviroment variable simon_password')
    password = getpass.getpass('Simon Password: ')

try:
    url = os.environ['simon_url']
except KeyError:
    url = 'intranet.stpats.vic.edu.au'

asp_cookie_raw = {
    'name': 'ASP.NET_SessionId',
    'value': 't1faudtd5tikb3fecmlo2mqq'
}
asp_cookie = requests.cookies.create_cookie(**asp_cookie_raw)
session.cookies.set_cookie(asp_cookie)

logon_headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

logon_data = {
  'curl': 'Z2F',
  'flags': '0',
  'forcedownlevel': '0',
  'formdir': '3',
  'trusted': '1',
  'username': username,
  'password': password,
  'SubmitCreds': 'Log On'
}

logon = session.post('https://'+url+'/CookieAuth.dll?Logon', headers=logon_headers, data=logon_data)
auth_cookie_raw = {
    'name': 'adAuthCookie',
    'value': 'E3E7EFDDB586EFB22D25B40EF10FC516EF893706C5FB36DC642787CACDFF2F29D691E740D4B51D3B5B30B47041A06F260DA078EB56239DA491E504744302BCACBF11B9A9001DD5A81861E44D6879020F5F93E2FF0C5C938A34B8D81B54498983',
}
auth_cookie = requests.cookies.create_cookie(**auth_cookie_raw)
session.cookies.set_cookie(auth_cookie)

today = datetime.datetime.today().strftime('%Y-%m-%d')
def get_TT(date):
    timetable_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://'+url+'/',
        'Content-Type': 'application/json; charset=utf-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }
    timetable_data = '{"selectedDate":"'+date+'","selectedGroup":"STURT"}'
    
    
    return(session.post('https://'+url+'/Default.asmx/GetTimetable', headers=timetable_headers,  data=timetable_data))

def print_TT(timetable):
    print(timetable.json()['d']['Info'])
    periods = timetable.json()['d']['Periods']
    for period in periods:
        for schClass in period['Classes']:
            print('-------------------------')
            print(schClass['TimeTableClass'])
            print(schClass['TeacherName'])
            print(schClass['Room'])

def print_mark():
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://'+url+'/WebModules/LearningAreas/Tasks/Assessment/SubmitTask.aspx?NavBarItem=ViewAssessmentTasks&TaskID=15605&Class=18998&Inactive=False',
        'Content-Type': 'application/json; charset=utf-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
    }
    
    data = '{"taskID":"15717","subjectClassID":"19484"}'
    
    response = session.post('https://'+url+'/WebModules/LearningAreas/Tasks/Assessment/SubmitTask.aspx/GetTaskSubmissionInfo', headers=headers, data=data)
    print(response.json()['d']['TaskResult']['FinalResult'])

def get_average(guid, sem):
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://'+url+'/WebModules/Profiles/Student/LearningResources/LearningAreaTasks.aspx?UserGUID=cf3e1f97-210f-4e35-a693-b4c176d9d94d',
    'Content-Type': 'application/json; charset=utf-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Connection': 'keep-alive',
}

    data = '{"guidString":"'+guid+'","fileSeq":'+str(sem)+'}'

    response = session.post('https://'+url+'/WebModules/Profiles/Student/LearningResources/LearningAreaTasks.aspx/getClasses', headers=headers, data=data) 
    
    resultRegx = re.compile(r'(?:\d+ \/ \d+ \((\d+)%\)|(\d+)%)')
    scoreList = []    

    for subjClass in response.json()['d']['SubjectClasses']:
        for task in subjClass['Tasks']:
            finalScore = int([ x for x in resultRegx.findall(task['FinalResult'])[0] if x != ''][0]) if resultRegx.findall(task['FinalResult']) else None 
            if finalScore:
            	scoreList.append(finalScore)

    try:
        print(sum(scoreList) / len(scoreList)) 
    except ZeroDivisionError:
        print('No Tasks this semester')

def get_guid():
    print(username)
    print(password)
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:62.0) Gecko/20100101 Firefox/62.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://'+url+'/WebModules/Profiles/Student/LearningResources/LearningAreaTasks.aspx?UserGUID=cf3e1f97-210f-4e35-a693-b4c176d9d94d',
        'Content-Type': 'application/json; charset=utf-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
    }
    
    params = (
        # Gets the current time since epoch of 1901, 1, 1
	    (time.time() * 1000, ''),
    )
    
    response = session.post('https://'+url+'/Default.asmx/GetUserInfo', headers=headers, params=params)
    print(response)
    guidRegx = re.compile(r'.*?GUID=(.*)')
    print(response.json()['d'])
    return(guidRegx.search(response.json()['d']['UserPhotoUrl']).group(1))

# timetable = get_TT(today)
# print_TT(timetable)
# print_mark()
guid = get_guid()
# 29 = 2016, 1st Semester
# semester = int(input('Semester Code: '))
# get_average(guid, semester)
