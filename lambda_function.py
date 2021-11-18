import json
import requests
import uuid
import json
import bs4
import random
from wordcloud import WordCloud, STOPWORDS
from datetime import date, timedelta
import datetime
import traceback
import string
import boto3
import io
import praw
import time
from jinja2 import Template
# coding=utf-8


class Parser(object):
    def __init__(self):
        self.object = None

    def read_input_json(self, file_name):
        try:
            print("test")
            with open(file_name) as f:
                read_input_json = json.load(f)

            print(type(read_input_json))

            result = {"response": read_input_json,
                      "status": "SUCESS"
                      }
            return result
        except Exception, e:
            print(e)
            result = {"response": str(e),
                      "status": "SUCESS"
                      }

    def send_notification(self, function_response, execution_status, notification_template, email_body, job_config=None, execution_response_arn='None'):
        """
            Purpose: To send notification to the user/DL
            Input: ses job configuration, the status of the process/function, the custom response from the function
            Output: DB API Response
            :param job_config: job_config
            :param execution_status: execution_status
            :param function_response: function_response
        """
        try:
            now = datetime.date.today()
            month_name = (now.strftime("%B"))
            year = (now.year)
            day = (now.day)
            curr_date = str(month_name) + " " + str(day) + "," + " " + str(year)
            curr_date = str(curr_date)
            replacement_dict = {}
            email_subject = "Big data updates for" + " " + curr_date

            print("Starting function to send email notification")
            rand_str = lambda n: ''.join([random.choice(string.lowercase) for i in xrange(n)])
            print("The session name created for SES Client - {}".format(rand_str(6)))

            print("Notification template is {}".format(notification_template))
            if notification_template == "notification_default_template.html":
                print(
                    "For template {},Creating email subject and the list of recipients ".format(notification_template))
            elif notification_template == "test":
                print(
                    "For template {},Creating email subject and the list of recipients ".format(notification_template))
                replacement_dict = {"FUNCTION_NAME": "test",
                                    'execution_response_arn': "simple"

                                    }
            elif notification_template == "test1":
                print(
                    "For template {},Creating email subject and the list of recipients ".format(notification_template))
                replacement_dict = {"FUNCTION_NAME": "test",
                                    'execution_response_arn': "simple"

                                    }

            notification_recipient_list = ["kailasa.akhil@zs.com", "ankul.jain@zs.com"]
            print("Creating subject of the mail by replacing paramters")
            ses_client = boto3.client('ses', region_name='us-east-1')
            ses_response = ses_client.send_email(
                Source="ankul.jain@zs.com",
                Destination={'ToAddresses': notification_recipient_list},
                Message={'Subject': {'Data': email_subject}, 'Body': {'Html': {'Data': email_body}}})

            print("The response from SES's send_email - {}".format(ses_response))
            result = {
                "status": "SUCCESS",
                "result": "Email sent successfully!"
            }
            return result

        except Exception, e:
            status_message = "ERROR in send_notification function :{}".format(e)
            print(status_message)
            print(traceback.format_exc(str(e)))
            result = {
                "status": "FAILED",
                "result": e
            }
            return result

    def dzone_parser(self, file_dict, aws_parser_response):
        try:
            print("dzone_parser crawling")
            final_list_dzone = []
            json_content_final = ""
            print ("printing the input to the dzone parser method")
            print(aws_parser_response)
            for i in range(0, len(file_dict)):
                datasource = file_dict[i]["website_source"]
                if datasource == "DZone":
                    print("Index fo the file_dict list " + str(i))
                    for list in range(0, len(file_dict[i]["urls"])):
                        print("========" + "value of i = " + str(i) + "=====================================")
                        print("=================" + str(len(file_dict[i]["urls"])) + "============================")
                        print (file_dict[i]["urls"][list])
                        print("========" + "value of i = " + str(i) + "=====================================")
                        url = file_dict[i]["urls"][list]
                        r = requests.get(url)
                        data = json.loads(r.content)
                        now = datetime.datetime.now()
                        if ((now.strftime("%A")) == "Monday"):
                            delta_range = 3
                        else:
                            delta_range = 1
                        dt = date.today() - timedelta(delta_range)
                        dt = str(dt)
                        data_dict = (data["result"]["data"]["nodes"])
                        for j in range(0, len(data_dict)):
                            final_dict_dzone = {}
                            final_dict_dzone["article_published_date"] = data_dict[j]['articleDate']
                            final_dict_dzone["article_published_date"] = datetime.datetime.fromtimestamp(
                                final_dict_dzone["article_published_date"] / 1000)
                            final_dict_dzone["article_published_date"] = datetime.datetime.strftime(
                                final_dict_dzone["article_published_date"], '%Y-%m-%d')
                            final_dict_dzone["article_published_date"] = str(
                                final_dict_dzone["article_published_date"])

                            if final_dict_dzone["article_published_date"] == dt:
                                final_dict_dzone['article_related_tags'] = []
                                tag_list_dzone = data_dict[j]["tags"]
                                for tags in range(0, len(tag_list_dzone)):
                                    final_dict_dzone['article_related_tags'].append(tag_list_dzone[tags])
                                print("latest data available for the node data obtained and continue crawling")
                                final_dict_dzone["article_title"] = data_dict[j]['title']
                                final_dict_dzone["article_link"] = 'https://dzone.com' + data_dict[j]['articleLink']
                                final_dict_dzone["article_summary"] = data_dict[j]['articleContent']
                                final_dict_dzone["article_author"] = data_dict[j]['authors'][0]['realName']
                                final_dict_dzone["article_source"] = "Dzone"
                                aws_parser_response.append(final_dict_dzone)
            print("dzone")
            print("===========FINAL OUTPUT JSON================")
            print(str(aws_parser_response))
            print("============================================")
            result = {"response": aws_parser_response,
                      "status": "SUCCESS"
                      }
            return result

        except Exception, e:
            print(e)
            traceback.print_exc()

    def aws_parser(self, file_dict):
        try:
            print ("printing file dict", file_dict)
            print("aws_parser crawling")
            final_list = []
            now = datetime.datetime.now()
            if ((now.strftime("%A")) == "Monday"):
                delta_range = 3
            else:
                delta_range = 1
            dt = date.today() - timedelta(delta_range)
            for i in range(0, len(file_dict)):
                datasource = file_dict[i]["website_source"]
                if datasource == "AWSBlog":
                    for list in range(0, len(file_dict[i]["urls"])):
                        url = file_dict[i]["urls"][list]
                        dt = str(dt)
                        url = url.replace("$$dt", dt)
                        print("url", url)
                        r = requests.get(url)
                        data = json.loads(r.content)
                        list = data['items']
                        final_list = []
                        for i in range(0, len(list)):
                            final_dict = {}
                            final_dict['article_title'] = list[i]['item']['additionalFields']['title']
                            final_dict['article_link'] = list[i]['item']['additionalFields']['link']
                            final_dict['article_published_date'] = list[i]['item']['additionalFields']['createdDate'][0:10]
                            final_dict['article_author'] = list[i]['item']['author'][2:-2]
                            article_link = final_dict['article_link']
                            final_dict['article_related_tags'] = []
                            tag_list = list[i]["tags"]
                            for tags in range(0, len(tag_list)):
                                print(tag_list[tags])
                                final_dict['article_related_tags'].append(tag_list[tags]["name"])
                            final_dict['article_source'] = 'AWS'
                            page = requests.get(article_link)
                            html_doc = page.text
                            soup = bs4.BeautifulSoup(html_doc, 'html.parser')
                            test = soup.find_all('meta', {"property": "og:description"}, content=True)
                            summary_article=test[0]['content'].encode('ascii', 'ignore')
                            summary_article=str(summary_article)[0:90]
                            final_dict['article_summary'] = summary_article+"..."
                            final_list.append(final_dict)
            result = {"response": final_list,
                      "status": "SUCESS"
                      }
            return result
        except Exception, e:
            print(e)
            traceback.print_exc()

    def medium_parser(self,file_dict, medium_parser_output):
        try:
            print ("input received to medium parser output", medium_parser_output)
            now = datetime.datetime.now()
            if ((now.strftime("%A")) == "Monday"):
                delta_range = 3
            else:
                delta_range = 1
            dt = now.today() - datetime.timedelta(delta_range)
            medium_url = file_dict[2]["urls"]
            for i in range(0, len(file_dict)):
                for j in range(0, len(medium_url)):
                    print ("printing the j and i value value")
                    print i,j
                    url = medium_url[j]
                    print ("printing the url of medium parser",url)
                    page = requests.get(url)
                    text_output_json = page.text
                    text_output_json = json.loads(text_output_json[16:])
                    print ("full output json after hitting the medium url", text_output_json)
                    dict_posts = text_output_json['payload']['references']['Post']
                    dict_User = text_output_json['payload']['references']['User']
                    dict_post_keys = dict_posts.keys()
                    post_creator_id = []
                    index_store = []
                    user_name_list = []
                    unique_slug_list = []
                    author_list = []
                    article_content = []
                    article_dates = []
                    article_title = []
                    article_tag_list_new = []
                    #getting the indexes of the articles which have yesterday's date and storing them in a list
                    for l in range(0, len(dict_post_keys)):
                        print ("inside the dict post keys loop")
                        date_value = str((datetime.datetime.fromtimestamp(dict_posts[dict_post_keys[l]]['firstPublishedAt'] / 1000)))[0:11]
                        post_creator_id.append(dict_posts[dict_post_keys[l]]['creatorId'])
                        print post_creator_id
                        print ("datetime and dt")
                        print ("printing dt")
                        dt=str(dt)
                        dt=dt[0:11]
                        print("printing the date and time to be compared")
                        print l
                        print dt
                        print date_value
                        if (delta_range==1):
                            if (date_value == dt):
                                index_store.append(l)
                        else:
                            if(date_value>=dt):
                                index_store.append(l)
                    #appending the data to the above created lists user_name_list,unique_slug_list,author_list,article_content,article_dates,article_title for which the indexes are matching
                    for i in range(0, len(dict_post_keys)):
                        for j in range(0, len(index_store)):
                            if (i == index_store[j]):
                                user_name_list.append((dict_User[post_creator_id[i]]['username']))
                                author_list.append((dict_User[post_creator_id[i]]['name']))
                                unique_slug_list.append(dict_posts[dict_post_keys[i]]['uniqueSlug'])
                                article_dates.append(str((datetime.datetime.fromtimestamp(dict_posts[dict_post_keys[i]]['createdAt'] / 1000)))[0:11])
                                article_title.append(dict_posts[dict_post_keys[i]]['title'].encode('ascii', 'ignore'))
                                if (('subtitle') in (dict_posts[dict_post_keys[i]]['content'].keys())):
                                    article_content.append(dict_posts[dict_post_keys[i]]['content']['subtitle'])
                                else:
                                    article_content.append([])
                                if (('tags') in (dict_posts[dict_post_keys[i]]['virtuals'].keys())):
                                    test_val = dict_posts[dict_post_keys[i]]['virtuals']['tags']
                                    article_tag_list_new.append(test_val)
                                else:
                                    article_tag_list_new.append([])
                    list_of_tags_list = []
                    for i in range(0, len(article_tag_list_new)):
                        j = article_tag_list_new[i]
                        tag_list_in = []
                        for k in range(0, len(j)):
                            tag_list_in.append(j[k]['slug'])
                        list_of_tags_list.append(tag_list_in)
                    for i in range(0, len(article_dates)):
                        final_dict_medium = {}
                        final_dict_medium["article_related_tags"] = []
                        user_name = user_name_list[i]
                        slug = unique_slug_list[i]
                        static = "https://medium.com/@"
                        final_dict_medium["article_published_date"] = article_dates[i]
                        final_dict_medium["article_title"] = article_title[i]
                        final_dict_medium["article_link"] = static + user_name + "/" + slug
                        final_dict_medium["article_summary"] = article_content[i]
                        final_dict_medium["article_author"] = author_list[i]
                        final_dict_medium["article_related_tags"] = list_of_tags_list[i]
                        final_dict_medium["article_source"] = "Medium"
                        print ("printing the dict that is going to get appended to input medium json")
                        medium_parser_output.append(final_dict_medium)
                        random.shuffle(medium_parser_output)
            print("medium parser crawl completed")
            result = {"response": medium_parser_output,
                        "status": "SUCCESS"
                            }
            return result

        except Exception, e:
            status_message = "Error in execution of Medium Parser"
            print status_message
            print(e)
            traceback.print_exc()
            raise e

    def word_cloud_parser(self, file_dict):
        try:
            print("word_cloud_parser")
            # text = '''amazon-workspaces,aws-directory-service,desktop-app-streaming,intermediate-200,advanced-300,security-identity-compliance,learning-levels,security,how-to,amazon-cloudfront,devops,aws-mobile-development,networking-content-delivery,video-applications,amplify,media-services,how-to,open-source,aws-cloudhsm,docker,java,pkcs11,aws-cloudhsm,containers,security-identity-compliance,cloud-computing,aws,azure,google-cloud,technology,aws,lambda,serverless,aws,lambda,serverless,aws,lambda,serverless,cloud-computing,aws,nginix,elasticsearch,metadata,http request,big data'''
            # text=file_dict
            list_contents = list (file_dict)
            test =""
            for i in range (0, len (list_contents)):
                test = test + list_contents[i] + ","
            test= test.rstrip (",")
            # test="'''"+test+"'''"
            text='''amazon-redshift-analytics,microservices,spring batch tutorial,spring boot tutorial,aws-marketplace,chatbot,big-data,webinar,restful apis,aws-waf,predictive-analytics,analytics,devops,cloud foundry,cloud deployment,spring batch,apache,web-app-development,web app bot,open source,conversational ai,big data,flask,tools,big-data-analysis,storage,hadoop,security-identity-compliance,amazon-redshift,big-data-market-research,sagemaker,5g,development,front end development,devsecops,sans-institute,artificial-intelligence,python,iot,aws,aws-datasync,conversational interfaces,nginx,microservices tutorial java,amazon-efs,mobile-network,web-server,amazon-s3,google maps,advanced-300,mythbusting,mobile,data ingestion,cloud-computing,learning-levels,ai chatbot,azure,security,conversational agents,software'''
            # test=test.encode('ascii','ignore')
            print type(text)
            print("before convertion",text)
            wordcloud = WordCloud (relative_scaling=0,
                                   stopwords=set (STOPWORDS)
                                   ).generate (test)
            print ("image converted")
            result = wordcloud.to_file ("WordCloud.png")
            # s3 = boto3.resource (service_name='s3')
            # s3.meta.client.upload_file (Filename='poc_tech_crawling/Word_Cloud/s.png', Bucket='app-test-bdpod-data',
            #                             Key='s.png')
            # s3=boto3.client('s3')
            # upload_result=s3.put_object (Bucket="app-test-bdpod-data", Key="poc_tech_crawling/Word_Cloud", Body="s.png")
            # print(upload_result)

            result = {"response": "done successfully",
                      "status": "SUCCESS"
                      }
            return result

        except Exception, e:
            status_message = "Error in execution of WordCloud Function"
            print status_message
            print(e)
            traceback.print_exc ()
            raise e


    def reddit_parser(self,file_dict,reddit_parser_response):
        try:

            list = file_dict[3]["urls"]
            reddit = praw.Reddit(client_id='YDLuGeDLGPh1qA',
                                 client_secret='TpKtE9p_lMX4-3kp9tSFf6fKCCk',
                                 user_agent='santosh',
                                 username='santoshnalgonda',
                                 password='zsa@2019')
            no_subreddit = reddit.subreddit('all')
            hot = no_subreddit.hot(limit=1000)
            print(hot)


            for reddit_key in list:
                subreddit1 = reddit.subreddit(reddit_key)
                python_subreddit = subreddit1.hot(limit=10)

                now = datetime.datetime.now()
                if ((now.strftime("%A")) == "Monday"):
                    delta_range = 3
                else:
                    delta_range = 1
                dt = date.today()-timedelta(delta_range)

                for j in python_subreddit:
                    final_dict_redshift = {}

                    final_dict_redshift["article_published_date"] = time.strftime("%Y-%m-%d",time.localtime(j.created_utc))

                    final_dict_redshift["article_published_date"] = str(
                        final_dict_redshift["article_published_date"])
                    if(delta_range==1):
                        if (final_dict_redshift["article_published_date"]) == str(dt):
                            if len(j.selftext) != 0:
                                final_dict_redshift["article_link"] = j.url
                                final_dict_redshift["article_title"] = j.title
                                reddit_summary=j.selftext
                                reddit_summary=reddit_summary[0:50]
                                final_dict_redshift["article_summary"] = reddit_summary
                                final_dict_redshift["article_author"] = str(j.author)
                                final_dict_redshift["article_source"] = "Reddit"
                                reddit_parser_response.append(final_dict_redshift)
                            else:
                                print("No-text information found to crawl")
                    else:
                        if (final_dict_redshift["article_published_date"]) >= str(dt):
                            if len(j.selftext) != 0:
                                final_dict_redshift["article_link"] = j.url
                                final_dict_redshift["article_title"] = j.title
                                reddit_summary = j.selftext
                                reddit_summary = reddit_summary[0:50]
                                final_dict_redshift["article_summary"] = reddit_summary
                                final_dict_redshift["article_author"] = str(j.author)
                                final_dict_redshift["article_source"] = "Reddit"
                                reddit_parser_response.append(final_dict_redshift)
                            else:
                                print("No-text information found to crawl")
            result = {"response": json.dumps(reddit_parser_response,encoding='utf-8'),
                      "status": "SUCCESS"
                      }
            return result
        except Exception, e:
            print(e)
            traceback.print_exc()

    def create_email_template(self, output_json):
        try:
            color_list = ["#cbf1f5", "#a6e3e9", "#cbf1f5", "#a6e3e9"]
            output_json = output_json['response']
            output_json = json.loads(output_json)
            print type(output_json)
            final_str = ""
            title_of_articles_aws = []
            links_of_articles_aws = []
            summary_of_articles_aws = []
            title_of_articles_dzone = []
            links_of_articles_dzone = []
            summary_of_articles_dzone = []
            title_of_articles_medium = []
            links_of_articles_medium = []
            summary_of_articles_medium = []
            title_of_articles_reddit = []
            links_of_articles_reddit = []
            summary_of_articles_reddit = []
            article_tags_aws = []
            article_tags_dzone = []
            article_tags_medium = []
            final_articles_tag_list=[]
            for i in range(0, len(output_json)):
                if (output_json[i]['article_source'] == "AWS"):
                    title_of_articles_aws.append(output_json[i]['article_title'])
                    links_of_articles_aws.append(output_json[i]['article_link'])
                    summary_of_articles_aws.append(output_json[i]['article_summary'])
                    article_tags_aws.append(output_json[i]['article_related_tags'])
                elif (output_json[i]['article_source'] == "Dzone"):
                    title_of_articles_dzone.append(output_json[i]['article_title'])
                    links_of_articles_dzone.append(output_json[i]['article_link'])
                    summary_of_articles_dzone.append(output_json[i]['article_summary'])
                    article_tags_dzone.append(output_json[i]['article_related_tags'])
                elif(output_json[i]['article_source'] == "Medium"):
                    title_of_articles_medium.append(output_json[i]['article_title'])
                    links_of_articles_medium.append(output_json[i]['article_link'])
                    summary_of_articles_medium.append(output_json[i]['article_summary'])
                    article_tags_medium.append(output_json[i]['article_related_tags'])
                else:
                    title_of_articles_reddit.append(output_json[i]['article_title'])
                    links_of_articles_reddit.append(output_json[i]['article_link'])
                    summary_of_articles_reddit.append(output_json[i]['article_summary'])
            final_str = final_str + str("""<!DOCTYPE html>
                            <html>
                            <head>
                            <style>
                            table, td, th {text-align: left;}table {border-spacing:12px;margin:15px;width:50%;}th, td {padding: 10px;  text-align:center;}.link{font-size:12px;}.para{font-weight:normal;}}
                            </style>
                            </head>
                            <body>
                            <img src="https://drive.google.com/file/d/1XwE5onGqf9xSesA-aq7gaA6NLmnXn7sF/view" alt="loading word cloud image....." style="width:300px;height:300px; align="middle">""")
            if (len(title_of_articles_aws) != 0):
                len_aws = 4
                final_str = final_str + str("""<table cellspacing="15" align="center">
                                    <tr>
                             <th bgcolor='#ffffff' font-size='10px' colspan='1'""")
                final_str = final_str + ("""text-align:center><span style=font-size:20px>AWS Blogs</span></th>
                                                             </tr><tr>""")
                print ("printing the length of aws articles")
                print (len(links_of_articles_aws))
                for i in range(0, 4):
                    final_str = final_str + str("""
                        <th bgcolor=" """)
                    t = Template("{{results}}")
                    testone = t.render(results=color_list[i])
                    final_str = final_str + (testone) + '"'
                    final_str = final_str + str("""class="link"><a href=""")
                    t = Template("{{results}}")
                    testone = t.render(results=links_of_articles_aws[i])
                    final_str = final_str + (testone)
                    final_str = final_str + str("""><span class="link-u" style="color:#000000;"><multiline>""")
                    t = Template("{{results}}")
                    testone = t.render(results=title_of_articles_aws[i])
                    final_str = final_str + (testone)
                    final_str = final_str + str("""</multiline></span></a><p class="para">""")
                    t = Template("{{results}}")
                    testone = t.render(results=summary_of_articles_aws[i])
                    final_str = final_str + (testone)
                    final_str = final_str + str("""</p></th>""")
                    L = article_tags_aws[i]
                    final_articles_tag_list.append(L)
                final_str = final_str + str("""</tr></table>""")
            if (len(title_of_articles_medium) != 0):
                final_str = final_str + str("""<table cellspacing="15" align="center">
                                    <tr>
                             <th bgcolor='#ffffff' font-size='10px' colspan='1' """)
                final_str = final_str + ("""text-align:center><span style=font-size:20px>Medium</span></th></tr><tr>""")
                for i in range(0, 4):
                    final_str = final_str + str("""
                        <th bgcolor=" """)
                    t = Template("{{results}}")
                    testone = t.render(results=color_list[i])
                    final_str = final_str + (testone) + '"'
                    final_str = final_str + str("""
                        class="link">
                         <a href=""")
                    t = Template("{{results}}")
                    testone = t.render(results=links_of_articles_medium[i])
                    final_str = final_str + (testone)
                    final_str = final_str + str("""><span class="link-u" style="color:#000000;"><multiline>""")
                    t = Template("{{results}}")
                    testone = t.render(results=title_of_articles_medium[i])
                    final_str = final_str + (testone)
                    final_str = final_str + str("""</multiline></span></a><p class="para">""")
                    t = Template("{{results}}")
                    testone = t.render(results=summary_of_articles_medium[i])
                    final_str = final_str + (testone)
                    L = article_tags_medium[i]
                    final_articles_tag_list.append(L)
                final_str = final_str + str("""</th></tr></table>""")
            if (len(title_of_articles_dzone) != 0):
                final_str = final_str + str("""<table cellspacing="15" align="center">
                                    <tr>
                             <th bgcolor='#ffffff' font-size='10px' colspan='1' """)
                final_str = final_str + ("""text-align:center><span style=font-size:20px>Dzone</span></th>
                                                             </tr><tr>""")
                for i in range(0, 4):
                    final_str = final_str + str("""
                        <th bgcolor=" """)
                    t = Template("{{results}}")
                    print ("printing the value of i",i)
                    testone = t.render(results=color_list[i])
                    final_str = final_str + (testone) + '"'
                    final_str = final_str + str("""
                       class="link">
                         <a href=""")
                    t = Template("{{results}}")
                    testone = t.render(results=links_of_articles_dzone[i])
                    final_str = final_str + (testone)
                    final_str = final_str + str("""><span class="link-u" style="color:#000000;"><multiline>""")
                    t = Template("{{results}}")
                    testone = t.render(results=title_of_articles_dzone[i])
                    final_str = final_str + (testone)
                    final_str = final_str + str("""</multiline></span></a><p class="para">""")
                    t = Template("{{results}}")
                    testone = t.render(results=summary_of_articles_dzone[i])
                    final_str = final_str + (testone)
                    L = article_tags_dzone[i]
                    final_articles_tag_list.append(L)
                    final_str = final_str + ("""</p></th>""")
                    # test_element = ",".join(str(x) for x in L)
                    # final_str = final_str + str("""<p>""")
                    # final_str = final_str + str("""Tagged in:""")
                    # t = Template("{{results}}")
                    # testone = t.render(results=test_element)
                    # final_str = final_str + (testone)
                    # final_str = final_str + str("""</p>""")
                final_str = final_str + str("""</tr></table>""")
            if (len(title_of_articles_reddit) != 0):
                len_reddit = 1
                final_str = final_str + str("""<table cellspacing="15" align="center">
                                                <tr>
                                         <th bgcolor='#ffffff' font-size='10px' colspan='""")
                t = Template("{{results}}")
                testone = t.render(results=len_reddit)
                final_str = final_str + (testone)
                final_str = final_str + "'"
                final_str = final_str + ("""text-align:center><span style=font-size:20px>Reddit</span></th>
                                                                         </tr><tr>""")
                for i in range(0, 4):
                    final_str = final_str +str("""
                                    <th bgcolor=" """)
                    t = Template("{{results}}")
                    testone = t.render(results=color_list[i])
                    final_str = final_str + (testone) + '"'
                    final_str = final_str + str("""class="link">
                                     <a href=""")
                    t = Template("{{results}}")
                    testone = t.render(results=links_of_articles_reddit[i])
                    final_str = final_str + (testone)
                    final_str = final_str + str("""><span class="link-u" style="color:#000000;"><multiline>""")
                    t = Template("{{results}}")
                    testone = t.render(results=title_of_articles_reddit[i])
                    final_str = final_str + (testone)
                    reddit_summary_content = summary_of_articles_reddit[i]
                    len_content = len(reddit_summary_content)
                    reddit_summary_content = reddit_summary_content+ "...."
                    final_str = final_str + str("""</multiline></span></a><p class="para">""")
                    t = Template("{{results}}")
                    testone = t.render(results=summary_of_articles_reddit[i])
                    final_str = final_str + (testone)
                    final_str = final_str + str("""</p></th>""")
                final_str = final_str + str("""</tr></table>""")
            final_str = final_str + str("""</body></html>""")
            results_union = set().union(*final_articles_tag_list)
            print("final", final_str)
            return final_str,results_union
        except Exception, e:
            print(e)
            traceback.print_exc()

    def main(self):
        try:
            file_name = "Input.json"
            result = self.read_input_json(file_name)
            file_dict = result["response"]
            print("printing file dict")
            print(file_dict)
            aws_parser_output = self.aws_parser(file_dict)
            print(aws_parser_output)
            aws_parser_response = aws_parser_output["response"]
            print ("aws_output", aws_parser_response)
            dzone_parser_output = self.dzone_parser(file_dict, aws_parser_response)
            medium_parser_output = self.medium_parser(file_dict,dzone_parser_output['response'])
            print ("print the final medium parser output")
            print json.dumps((medium_parser_output))
            reddit_parser_response = self.reddit_parser(file_dict, medium_parser_output['response'])
            print ("print the final reddit parser output")
            print json.dumps(reddit_parser_response["response"])
            final_html_output_file,set_of_elements = self.create_email_template(reddit_parser_response)
            wordcloud_result=self.word_cloud_parser(set_of_elements)
            print ("priniting set of tags")
            print set_of_elements
            print ("final_html_file", final_html_output_file)
            result = self.send_notification(function_response=None
                                            , execution_status=None,
                                            notification_template="notification_default_template.html",
                                            email_body=reddit_parser_response, job_config=None,
                                            execution_response_arn='None')
        except Exception, e:
            print(e)
            traceback.print_exc()

def lambda_handler(event, context):
    PO = Parser()
    PO.main()
    return "SUCCESS"