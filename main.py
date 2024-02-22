import jenkins
import requests
from requests.auth import HTTPBasicAuth
import xml.etree.ElementTree as ET

JENKINS_SERVER_URL = 'https://jenkins.domain-company.com/'
username = 'username'
password = '****'
server = jenkins.Jenkins(JENKINS_SERVER_URL, username, password)

def account():
    user = server.get_whoami()
    jenkins_version = server.get_version()
    print('Hello from Jenkins (%s)... Initiating connection as %s' % (jenkins_version, user['fullName']))

def get_projects():
    list_jobs = server.get_jobs(folder_depth=0, folder_depth_per_request=10)

    # 1
    for first_jobs in list_jobs:

        url_job_1 = first_jobs['name']

        config_url_1 = f'https://jenkins.domain-company.com/job/{url_job_1}/config.xml'
        config_response_1 = requests.get(config_url_1, auth=HTTPBasicAuth(username, password))
        if config_response_1.status_code == 200:

            root_1 = ET.fromstring(config_response_1.text)
            if root_1.tag == "com.cloudbees.hudson.plugins.folder.Folder":
                print(url_job_1 + " is a folder")

                # 2
                for second_jobs in first_jobs['jobs']:
                    
                    url_job_2 = second_jobs['name']

                    config_url_2 = f'https://jenkins.domain-company.com/job/{url_job_1}/job/{url_job_2}/config.xml'
                    config_response_2 = requests.get(config_url_2, auth=HTTPBasicAuth(username, password))
                    if config_response_2.status_code == 200:

                        root_2 = ET.fromstring(config_response_2.text)
                        if root_2.tag == "com.cloudbees.hudson.plugins.folder.Folder":
                            print(url_job_1 + "/" + url_job_2 + " is a folder")

                            # 3
                            for third_jobs in second_jobs['jobs']:
                                
                                url_job_3 = third_jobs['name']

                                config_url_3 = f'https://jenkins.domain-company.com/job/{url_job_1}/job/{url_job_2}/job/{url_job_3}config.xml'
                                config_response_3 = requests.get(config_url_3, auth=HTTPBasicAuth(username, password))
                                if config_response_3.status_code == 200:
                                    
                                    root_3 = ET.fromstring(config_response_3.text)
                                    if root_3.tag == "com.cloudbees.hudson.plugins.folder.Folder":
                                        print(url_job_1 + "/" + url_job_2 + "/" + url_job_3 + " is a folder")

                                        # 4
                                        # *** fourth for loop here ***

                                    elif root_3.tag == "org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject":
                                        print(url_job_1 + "/" + url_job_2 + "/" + url_job_3 + " is a multibranch")
                                        url_job_123 = url_job_1 + "/" + url_job_2 + "/" + url_job_3
                                        # read multibranch config.xml
                                        read_config(config_url_2,url_job_123)
                                
                                else:
                                    print("Se perdio la conexion a Jenkins - Flujo 3")
                                    break


                        elif root_2.tag == "org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject":
                            print(url_job_1 + "/" + url_job_2 + " is a multibranch")
                            url_job_12 = url_job_1 + "/" + url_job_2
                            # read multibranch config.xml
                            read_config(config_url_2,url_job_12)
                    
                    else:
                        print("Se perdio la conexion a Jenkins - Flujo 2")
                        break


            elif root_1.tag == "org.jenkinsci.plugins.workflow.multibranch.WorkflowMultiBranchProject":
                print(url_job_1 + " is a multibranch")
                # read multibranch config.xml
                read_config(config_url_1,url_job_1)

            else:
                print("ups")
        
        else:
            print("Se perdio la conexion a Jenkins - Flujo 1")
            break

def read_config(config_url,job_path):

    print(config_url)
    config_response = requests.get(config_url, auth=HTTPBasicAuth(username, password))
    if config_response.status_code == 200:

        root = ET.fromstring(config_response.text)
        count = 0
        for element in root:

            if element.tag == "sources":
                source_id = ""
                source_repository = ""
                traits_BranchDiscoveryTrait = ""
                traits_OriginPullRequestDiscoveryTrait = ""
                traits_WildcardSCMHeadFilterTrait = ""
                try:
                    for child_element in element[0][0][0]:

                        if child_element.tag == "id":
                            source_id = child_element.text
                        elif child_element.tag == "repository":
                            source_repository = child_element.text
                        elif child_element.tag == "traits":
                            traits_BranchDiscoveryTrait = child_element[0][0].text
                            traits_OriginPullRequestDiscoveryTrait = child_element[1][0].text
                            traits_WildcardSCMHeadFilterTrait = child_element[2][0].text
                
                except IndexError as ie:
                    print("source - Script index error") 
                    print(ie)
                except Exception as e:
                    print("source Script error")
                    print(e)

                with open('result.txt', 'a') as file:
                    file.write( str(job_path) + "," + str(source_id) + "," + str(source_repository) + "," + str(traits_BranchDiscoveryTrait) + "," + str(traits_OriginPullRequestDiscoveryTrait) + "," + str(traits_WildcardSCMHeadFilterTrait) + ",")
                print("add sources values")

            elif element.tag == "factory":
                factory_scriptPath = ""
                factory_remoteJenkinsFile = ""
                factory_UserRemoteConfig = ""
                factory_BranchSpec = ""

                if element.attrib['class'] == "org.jenkinsci.plugins.workflow.multibranch.extended.RemoteJenkinsFileWorkflowBranchProjectFactory":
                    try:
                        for child_element in element:
                            if child_element.tag == "scriptPath":
                                factory_scriptPath = child_element.text
                            elif child_element.tag == "remoteJenkinsFile":
                                factory_remoteJenkinsFile = child_element.text
                            elif child_element.tag == "remoteJenkinsFileSCM":

                                for fileSCM in child_element:

                                    if fileSCM.tag == "userRemoteConfigs":
                                        factory_UserRemoteConfig = fileSCM[0][0].text
                                    elif fileSCM.tag == "branches":
                                        factory_BranchSpec = fileSCM[0][0].text

                    except IndexError as ie:
                        print("factory - Script index error") 
                        print(ie)
                    except Exception as e:
                        print("factory - Script error")
                        print(e)

                    with open('result.txt', 'a') as file:
                        file.write( "remote," + str(factory_scriptPath) + "," + str(factory_remoteJenkinsFile) + "," + str(factory_UserRemoteConfig) + "," + str(factory_BranchSpec) + "\n")
                    print("is a remote jenkinsfile and add factory values")

                elif element.attrib['class'] == "org.jenkinsci.plugins.workflow.multibranch.WorkflowBranchProjectFactory":
                    for child_element in element:
                        if child_element.tag == "scriptPath":
                            factory_scriptPath = child_element.text

                    with open('result.txt', 'a') as file:
                        file.write( "local," + str(factory_scriptPath) + "\n")
                    print("is a local jenkinsfile and add factory values")
                            
            count = count + 1
        print("*********************************************************")


# account()
get_projects() 
# read_config()
