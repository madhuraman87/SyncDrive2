from flask import *
import urllib2
import json
import requests
import urllib

SECRET_KEY = 'synergy'
app = Flask(__name__)
app.config.from_object(__name__)

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

@app.route('/')
def welcome_page():
        return render_template('welcome.html')

@app.route('/sign_up')
def signup_page():
        return render_template('sign_up.html')

@app.route('/login')
def login_page():
        return render_template('login.html')

@app.route('/entry',methods = ['POST'] )
def store_user():
	username = request.form['username']
	password = request.form['password']
	return render_template('entry.html',username=username,password=password)

#@app.route('/login')
#def input_page():
#	return render_template('login.html') 

@app.route('/callback')
def callback():
	return render_template('callback.html')


@app.route('/callback_google')
def callback_google():

 	code = request.args.get('code')
	print "heyyyyyyyyyyyyyyyyyyyy %s" % code

	values = {
            'code':code,
            'client_id':'485476280210.apps.googleusercontent.com' ,
            'client_secret':'I_fk8bSDc0S2mjaGuJcV3k-6',
            'redirect_uri':'http://ec2.socialphotos.net:5000/callback_google',
            'grant_type':'authorization_code'
        }
	headers = {'content-type': 'application/x-www-form-urlencoded'}
        url = "https://accounts.google.com/o/oauth2/token"


	data = urllib.urlencode(values)
	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	raw_data = response.read()
	response = json.loads(raw_data)
	access_token=response['access_token']	

	raw_data = urllib2.urlopen("https://www.googleapis.com/drive/v2/about?access_token=%s" % access_token).read()	
	response = json.loads(raw_data)
	name = response["name"]
	quota_mb = sizeof_fmt(int(response["quotaBytesTotal"]))

	raw_data = urllib2.urlopen("https://www.googleapis.com/drive/v2/files?access_token=%s" % access_token).read()
	response = json.loads(raw_data)
	print response
	
	
	listFiles = []
        for record in response["items"]:
                fileRecord = {}
                fileRecord["id"]=record["id"]
                fileRecord["name"]=record["title"]
                fileRecord["raw_link"]=record.get("webContentLink","")
		fileRecord["size"]=record.get("fileSize","")
                listFiles.append(fileRecord)
	

	return render_template('hello.html',name=name,quota=quota_mb,listFiles=listFiles,response=response)


@app.route('/callback_dropbox')
def callback_dropbox():
	dropbox_token = request.args.get('token','')	
	print dropbox_token
	raw_data = urllib2.urlopen("https://api.dropbox.com/1/account/info?access_token=%s" % dropbox_token).read()
	data = json.loads(raw_data)
	print data		
	quota=data["quota_info"]["quota"]
	print quota	
	return render_template('dropbox.html',user=data["display_name"], emailId=data["email"], quotaDisplay = sizeof_fmt(int(quota)))

        
@app.route('/access_token')
def skydrive_access_token():
	session["token"] = request.args.get('token','')
	print session["token"]
	return redirect(url_for('list_files'))	

@app.route('/list_files')
def list_files():
	token = session["token"]
	try:
		folder = request.args.get('folder')
	except KeyError:
		print "no folder variable"

	if(folder == None):
		raw_data = urllib2.urlopen("https://apis.live.net/v5.0/me/skydrive/files?access_token=%s" % token).read()
	else:
		raw_data = urllib2.urlopen("https://apis.live.net/v5.0/%s/files?access_token=%s" % (folder,token)).read()

	response = json.loads(raw_data)		
	listFiles = []
	
	for record in response["data"]:
		fileRecord = {}
		fileRecord["id"]=record["id"]
		fileRecord["name"]=record["name"]
		fileRecord["raw_link"]=record.get("source","")
		fileRecord["size"]=sizeof_fmt(int(record["size"]))
		listFiles.append(fileRecord)
	
	raw_data1 = urllib2.urlopen("https://apis.live.net/v5.0/me/skydrive/quota?access_token=%s" % token).read()
	quota = json.loads(raw_data1)
	quota_mb = sizeof_fmt(int(quota["available"]))
	#return render_template('page.html',response=response,quota=quota_mb)
	return render_template('list_files.html',listFiles=listFiles,user=response["data"][0]["from"]["name"],quota=quota_mb)


if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
