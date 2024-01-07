import time
import math
import random
import pdb
import traceback
import warnings
import json
import pickle
import telebot
import re
import requests
import undetected_chromedriver as uc
import demjson3
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import concurrent.futures
from gpt4_openai import GPT4OpenAI
import google.generativeai as genai
warnings.filterwarnings('ignore')
import sys

with open(f'{sys.argv[1]}.json', 'r') as file:
    data = json.load(file)

for key in data:
    globals()[key] = data[key]

name = username.split("@")[0]
with open(f'{name}.txt', 'r') as file:
    resume = file.read()

from datetime import datetime
today = datetime.today()
formatted_date = today.strftime("%B %d, %Y")
resume+=f"\n- Today's date is {formatted_date}" 

print(data)

def ask_gpt_gemini(prompt):
    global gemini_api_key
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-pro')
    result = model.generate_content(prompt,generation_config=genai.types.GenerationConfig(
        max_output_tokens=2048,
        temperature=0.3)).text
    return result

def run_with_timeout(func, timeout, *args, **kwargs):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            print("Function took longer than %d seconds" % timeout)
            return None

max_retries = 30
def ask_gpt(prompt):
    global llm, model_name,headless_mode_chatgpt,token_cookie_chatgpt,chatgpt_timeout,max_retries
    try:
        if GPT_backend_selection == "gemini":
            try:
                return ask_gpt_gemini(prompt)
            except Exception as e:
                message(f"Error in Gemini: {e}")
                return None
        
        for _ in range(1):
            llm = GPT4OpenAI(token=token_cookie_chatgpt, headless=headless_mode_chatgpt, model=model_name)
            response = run_with_timeout(llm, 60, prompt)
            llm.close()
            if response is not None:
                break
        if response is None:
            raise Exception(f"{model_name} is not working, Trying to use GPT-3.5 instead.")
        #time.sleep(5)
        return response
    except:
        try:
            try:
                llm.close()
            except:
                pass
            llm = GPT4OpenAI(token=token_cookie_chatgpt, headless=headless_mode_chatgpt, model="text-davinci-002-render-sha")
            for _ in range(max_retries):
                if max_retries == 1:
                    break
                response = run_with_timeout(llm, chatgpt_timeout, prompt)
                llm.close()
                if response is not None:
                    break
            #time.sleep(5)
            return response
        except:
            message("ChatGPT is not working, using Gemini pro instead")
            max_retries = 1
            try:
                return ask_gpt_gemini(prompt)
            except Exception as e:
                message(f"Error in Gemini: {e}")
                return None


def message(t):
    global name
    try:
        bot = telebot.TeleBot(telegram_token_id)
        bot.send_message(telegram_chat_id, f"{name}: "+t)
    except:
        pass
    print("srikar: "+t)
    

class Linkedin:
    def __init__(self):

        global username, password , resume
        self.driver = uc.Chrome()
        time.sleep(1)
        self.driver.get('https://www.linkedin.com/login?emailAddress=&fromSignIn=&fromSignIn=true&session_redirect=https%3A%2F%2Fwww.linkedin.com%2Fjobs%2Fsearch%2F%3FcurrentJobId%3D3244103377%26f_AL%3Dtrue%26geoId%3D102713980%26keywords%3Ddata%2520scientist%26location%3DIndia%26refresh%3Dtrue&trk=public_jobs_nav-header-signin')
        self.driver.maximize_window()

        time.sleep(0.5)
        self.driver.find_element(By.XPATH,'//*[@id="username"]').send_keys(username)
        self.driver.find_element(By.XPATH,'//*[@id="password"]').send_keys(password)
        self.driver.find_element(By.XPATH,'//*[@id="organic-div"]/form/div[3]/button').click()
        try:
            verification =  self.driver.find_element(By.XPATH,'//*[@id="app__container"]/main/h1').text
        except:
            verification=None
        if verification == "Let's do a quick verification":
            message("Bot verification from Linkedin")
            import pdb;pdb.set_trace()
        
    def Link_job_apply(self):
        
        def fill_answers_by_gpt():
            try:
                def get_keys_from_gpt_response(final_answer):
                    import re
                    json_str = re.search(r'```json(.+?)```', final_answer, re.DOTALL)
                    if json_str:
                        cleaned_str = json_str.group(1).strip()
                    else:
                        final_answer = final_answer.replace('\n', '')
                        #final_answer = final_answer.replace(' ', '')
                        final_answer = re.sub(r'\s(?=(?:[^\'"]*[\'"][^\'"]*[\'"])*[^\'"]*$)', '', final_answer)
                        final_answer = re.sub(r'^.*?({)', r'\1', final_answer)
                        final_answer = re.sub(r'(}).*$', r'\1', final_answer) 
                        final_answer = final_answer.replace('True', 'true').replace('False', 'false')                       
                        cleaned_str = final_answer
                    try:
                        
                        data_dict = demjson3.decode(cleaned_str)
                        #data_dict = json.loads(cleaned_str)
                        if isinstance(data_dict, list):
                            final_box_answers = [list(item.values()) for item in data_dict]
                            final_box_answers = [item for sublist in final_box_answers for item in sublist]
                        else:
                            final_box_answers = list(data_dict.values())
                            try:
                                final=[]
                                for f in final_box_answers:
                                    final.append(f.split(":")[-1])
                                final_box_answers=final
                            except:
                                pass
                        return final_box_answers
                    except json.JSONDecodeError:
                        print("Could not decode JSON")
                        return []
                    
                def make_prompt(questions_set):
                        prompt = ""
                        prompt =f"""I have attached my resume below: ```"{resume}" 
                        ```. Read the above resume carefully and understand the information in it. You are applying for the job by answering the below questions behalf of the candidate in Linkedin website.
                        
                        Now, answer the following questions step by step:
                        """
                        count =0
                        for question in questions_set:
                            count +=1
                            prompt += f"Question {count}: {question}: \n"
                        prompt = prompt + """Begin by extracting pertinent information from the resume. Approach each question methodically, answering them one at a time using the information provided in the resume. If a question isn't directly answered in the resume, use creative thinking to provide an approximate answer based on the available information. Ensure to answer all questions in the order they are presented. Remember to first strategize each answer step by step before providing the final response. If the answer to the question is not given in the resume, Then you should estimate it creatively from the given information without saying that you don't know or not specified. 
                        Always remember to approximate answer creatively even if the answer is not mentioned in the resume.
                        Always remember that you should not say Not specified or provided in the given information, You have to estimate the answer creatively from the given information.
                        Answer it in good markdown format. with each question as side heading and it's explanation of answer below it. Also answer in the asked format (whole number as integer or float or string).                        
                        """
                        return prompt 
                def make_prompt2(questions_set , answer):
                        prompt =f"""
                        You are applying for the job by answering the below questions behalf of the candidate in Linkedin website. 
                        Take the information from the following ```{answer}``` and answer the below questions.
                        Here are the questions:
                        """
                        count =0
                        for question in questions_set:
                            count +=1
                            prompt += f"Question {count}: {question}: \n"
                        prompt = prompt + f""" Provide answers to the questions exclusively, formatted in valid Python Dictionary, with the question index as the key and the corresponding answer as the value. Exclude any explanations, extraneous details, or elements beyond the direct answer. Ensure the response conforms to the specified format, such as integer or whole number. When making assumptions for the answer, highlight positive and advantageous characteristics, taking into account the individual's comprehensive expertise and experience. Present the answer in Dictionary format, devoid of any additional explanations. Note that you are answering the question where you have to fill the answers in the box, So tell the exact answer. Read the question carefully and answer in required format (whole number as integer or float or string).If the answer to the question is not given in the information
                        , Then you should estimate it creatively from the given information without saying that you don't know or not specified. 
                        Remember to follow the correct dictionary format for the answer with the key as question number and value as the answer and don't use dictionary in the value. You should not use nested dictionary structure, you should only give key as the question number and value as the exact answer to the question in string.  If it was mentioned in the question to follow specific format like whole number or float number, then follow that carefully. 

                        """
                        return prompt
                
                def remove_duplicates(input_list):
                    result = []

                    for item in input_list:
                        if item not in result:
                            result.append(item)
                    
                    return result
                def make_prompt_radio(questions_set):
                    prompt = ""
                    prompt =f"""I have attached my resume below: ```"{resume}" 
                    ```
                    
                    Now, answer the following questions step by step by marking the appropriate radio button:
                    """
                    count =0
                    for question in questions_set:
                        count +=1
                        prompt += f"Question {count}: {question}: \n"
                    prompt = prompt + """Start by pulling out relevant information from the resume and approach each question systematically. Use the information from the resume to answer each question in sequence. If a question isn't directly addressed in the resume, use your creativity to provide a reasonable answer based on the available information. Ensure to answer all questions in the order they're given. Remember to strategize each answer step by step before providing the final response.Don't say that you don't know the answer or Not mentioned, estimate the answer according to the resume creatively. You have to only select the answer from the radio buttons and don't say that you don't know or not specified. If the answer is not present in the resume, then estimate it creatively and don't say it is not mentioned or not specified.

                    
                    """
                    return prompt 
                def make_prompt2_radio(questions_set , answer):
                    prompt =f"""
                    Take the information from the following ```{answer}``` and answer the below questions.
                    Here are the questions:
                    """
                    count =0
                    for question in questions_set:
                        count +=1
                        prompt += f"Question {count}: {question}: \n"
                    prompt = prompt + f"""Provide only the answers to the questions, formatted in valid Python Dictionary. Use the question index as the key and the corresponding answer as the value. Avoid including explanations, unnecessary details, or any elements beyond the direct answer. Ensure your response conforms to the specified format, such as integer or whole number. Present the answer in Dictionary format, without any additional explanations. Note that you are responding to a question with radio button options, so provide only the answer without additional explanations. If the answer is not specified, you can take assumptions on the answer based on the given information and you should not say that you don't know or not specified.  """
                    return prompt
                #import pdb;pdb.set_trace()
                try:
                                            
                    b=self.driver.find_elements(By.XPATH,'//*[contains(@class, "artdeco-text-input--label")]') # get box questions
                    box_questions=[]
                    for u in b: 
                        box_questions.append(u.text)
                        
                    if box_questions!=[]:
                        box_input_elements=self.driver.find_elements(By.XPATH,'//*[contains(@class, " artdeco-text-input--input")]') #box inputs
                        
                        for t in box_input_elements:
                            t.send_keys(Keys.CONTROL, 'a')
                            t.send_keys(Keys.DELETE)
                            #time.sleep(1)
                        try:
                            
                            self.driver.find_element(By.CSS_SELECTOR,
                                    "button[aria-label='Continue to next step']").click() #click next to get error titles again
                        except:
                            self.driver.find_element(By.CSS_SELECTOR,"button[aria-label='Review your application']").click()

                        b = self.driver.find_elements(By.XPATH,'//div[@class="artdeco-inline-feedback artdeco-inline-feedback--error ember-view mt1" and ancestor::div[@data-test-single-line-text-form-component]]') 

                        box_options=[]
                        for bo in b:
                            box_options.append(bo.text)
                        

                        final_box_questions=[]
                        try:
                            
                            for i in range(len(box_questions)):
                                final_box_questions.append(box_questions[i]+' .Answer this question in this format: '+ box_options[i])
                        except IndexError:
                            final_box_questions=box_questions
                            pass

                        ppp=(make_prompt(final_box_questions))
                        
                        if final_box_questions!=[]:
                            answer = ask_gpt(make_prompt(final_box_questions))
                            
                            final_answer = ask_gpt(make_prompt2(final_box_questions , answer))
                            final_box_answers = get_keys_from_gpt_response(final_answer)
                            message(f"Box Questions: {final_box_questions}, GPT answer : {final_box_answers}")

                            box_input_elements=self.driver.find_elements(By.XPATH,'//*[contains(@class, " artdeco-text-input--input")]') #box inputs
                            
                            for t in range(len(box_input_elements)):
                                box_input_elements[t].send_keys(final_box_answers[t])
                                time.sleep(0.1)
                except Exception as e:
                    pass
                    #print(f"An error occurred: {e}")
                    #print(traceback.format_exc())
                                        
                    
                try:
                    
                    radio_element = self.driver.find_elements(By.XPATH,"//*[contains(@id, 'radio-button-form-component-formElement-urn-li-jobs-applyfor')]")                                                        

                    radio_quesions=[]
                    old_ele=None
                    for r in radio_element:
                        if r.text == old_ele:
                            continue
                        r.text.split('\n')
                        appp = ' '.join(remove_duplicates(r.text.split("\n")))
                        if appp!="Please make a selection" and appp!='':
                            radio_quesions.append(appp)
                        old_ele = r.text
                    
                    
                    final_radio_questions = remove_duplicates(radio_quesions)
                    
                    if final_radio_questions!=[]:
                        answer = ask_gpt(make_prompt_radio(final_radio_questions))
                        final_answer = ask_gpt(make_prompt2_radio(final_radio_questions , answer))
                        final_radio_answers = get_keys_from_gpt_response(final_answer)
                        message(f"Radio Questions: {final_radio_questions}, GPT answer : {final_radio_answers}")
                        all_answers_list =[]
                        fieldsets = self.driver.find_elements(By.XPATH, '//fieldset[contains(@id, "radio-button-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement-")]')
                        for t in range(len(final_radio_answers)):
                            question = fieldsets[t].text
                            match = re.search("Required\n",question)
                            start,end = match.span()
                            answers = question[end:].split("\n")
                            #answers
                            #elements = self.driver.find_elements(By.XPATH,f'//label[@data-test-text-selectable-option__label]')
                            elements = self.driver.find_elements(By.XPATH,f'//label[@data-test-text-selectable-option__label="{final_radio_answers[t]}"]')
                            e=all_answers_list.count(final_radio_answers[t])
                            if elements==[]:
                                elements = self.driver.find_elements(By.XPATH,f'//label[@data-test-text-selectable-option__label="{final_radio_answers[t][:-1]}"]')
                                e=all_answers_list.count(final_radio_answers[t])
                            elements[e].click()
                            all_answers_list.extend(answers)

                except Exception as e:
                    pass
                    #print(f"An error occurred: {e}")
                    #print(traceback.format_exc())

                try:
                    
                    drawdown_read = self.driver.find_elements(By.XPATH,"//*[contains(@for, 'text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement')]")
                    drawdown_questions=[]
                    
                    for k in drawdown_read:
                        drawdown_questions.append(k.text.split('\n')[1])
                    if drawdown_questions!=[]:
                        drawdown_options_e=self.driver.find_elements(By.XPATH,"//*[contains(@id, 'text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement')]")
                        
                        drawdown_options=[]
                        for b in drawdown_options_e:
                            if b.text!='Please enter a valid answer':
                                drawdown_options.append(b.text)
                                
                                
                        final_drawdown_questions = []
                        for i in range(len(drawdown_questions)):
                            final_drawdown_questions.append(drawdown_questions[i]+' '+drawdown_options[i])
                            
                        answer = ask_gpt(make_prompt_radio(final_drawdown_questions))
                        final_answer = ask_gpt(make_prompt2_radio(final_drawdown_questions , answer))
                        final_drawdown_answers = get_keys_from_gpt_response(final_answer)
                        message(f"Drawdown Questions: {final_drawdown_questions}, GPT answer : {final_drawdown_answers}")
                        
                        elements = self.driver.find_elements(By.XPATH,"//*[contains(@id, 'text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement')]")
                        for trying in range(len(elements)):
                            try:
                                elements = self.driver.find_elements(By.XPATH,"//*[contains(@id, 'text-entity-list-form-component-formElement-urn-li-jobs-applyformcommon-easyApplyFormElement')]")
                                for t in range(len(elements)):
                                    from selenium.webdriver.support.ui import Select 
                                    Select(elements[t]).select_by_visible_text(final_drawdown_answers[t])
                                    time.sleep(0.5)
                            except:
                                pass
                            
                except Exception as e:
                    pass
                    #print(f"An error occurred: {e}")
                    #print(traceback.format_exc())
                    
                    
            except Exception as e:
                import traceback
                print(traceback.format_exc())
                print("some issue in GPT",e)


        try:
            def close_other_tabs():
                try:
                    chwd = self.driver.window_handles
                    for i in range(1,len(chwd)):
                        self.driver.switch_to.window(chwd[i])
                        self.driver.close()
                    self.driver.switch_to.window(chwd[0])
                except:
                    pass
            count_application = 0
            count_job = 0
            jobs_per_page = 25
            easy_apply = "?f_AL=true"
            #roles and location
            global roles1,not_roles1,locations,name
            try:
                with open(f'applied_job_id_{name}.pkl', 'rb') as f:
                    applied_job_ids = pickle.load(f)
            except FileNotFoundError:
                applied_job_ids = []
            

            for location in locations:
                print(f"Applying location at {location}")
                global keywords
                roles=[]
                not_roles=[]
                not_applied_roles=[]
                for i in roles1:
                    roles.append(i.lower())
                for i in not_roles1:
                    not_roles.append(i.lower())
                #random.shuffle(keywords) 
                for indexpag in range(len(keywords)):
                    time.sleep(8)
                    try:
                        try:
                            message(f"Started applying for the location {location} and role {keywords[indexpag]}")
                            global remote,hybrid
                            cons_page_mult = 0 #First page
                            if remote: 
                                url = 'https://www.linkedin.com/jobs/search/' + easy_apply +"&f_WT=2&"+ '&keywords=' + keywords[indexpag] + "&" + location + "&start=" + str(cons_page_mult)
                            else:
                                url = 'https://www.linkedin.com/jobs/search/' + easy_apply +'&keywords=' + keywords[indexpag] + "&" + location + "&start=" + str(cons_page_mult)
                            if remote and hybrid:
                                url = 'https://www.linkedin.com/jobs/search/' + easy_apply +"&f_WT=1&"+ '&keywords=' + keywords[indexpag] + "&" + location + "&start=" + str(cons_page_mult)
                            close_other_tabs()
                            self.driver.get(url)
                            for k in range(40):
                                self.driver.find_element(By.XPATH,"//input[@class='jobs-search-box__text-input' and @autocomplete='address-level2']").send_keys("\b")                                    
                            from selenium.webdriver.common.keys import Keys
                            self.driver.find_element(By.XPATH,"//input[@class='jobs-search-box__text-input' and @autocomplete='address-level2']").send_keys(location+Keys.ENTER)
                            
                            time.sleep(5)
                            url_with_location = self.driver.current_url
                        except:
                            message("Maybe linkedin verification")
                            continue
                        numofjobs = self.driver.find_element(By.XPATH,'//small').text  # get number of results
                        space_ind = numofjobs.index(' ')
                        total_jobs = (numofjobs[0:space_ind])
                        total_jobs_int = int(total_jobs.replace(',', ''))
                        number_of_pages = math.ceil(total_jobs_int/jobs_per_page)
                        print(number_of_pages)
                        for current_page_no in range(1,number_of_pages):
                            try:      
                                if current_page_no>40: # Usually Jobs after 40 pages are not that relevant to the role
                                    break
                                
                                self.driver.get(url_with_location)
                                time.sleep(random.randint(4,6))
                                cons_page_mult = 25 * current_page_no
                                try:
                                    page1_button = self.driver.find_element(By.XPATH,f'//li[@data-test-pagination-page-btn="{current_page_no}"]/button')
                                    page1_button.click()
                                    time.sleep(5)
                                    url_with_location = self.driver.current_url
                                except:
                                    element = self.driver.find_elements(By.XPATH,'//button[span="…"]')
                                    element[-1].click()
                                    page1_button = self.driver.find_element(By.XPATH,f'//li[@data-test-pagination-page-btn="{current_page_no}"]/button')
                                    page1_button.click()
                                    time.sleep(5)
                                    url_with_location = self.driver.current_url
                                time.sleep(5)
                                
                                
                                try:
                                    
                                    scroll_element = self.driver.find_element(By.XPATH,"/html/body/div[5]/div[3]/div[4]/div/div/main/div/div[1]/div")
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    actions = ActionChains(self.driver)
                                    # Move the mouse to the element
                                    actions.move_to_element(scroll_element).perform()
                            
                                    # Scroll down by 500 pixels
                                    for sc in range(10):
                                        self.driver.execute_script("arguments[0].scrollTop += 500;", scroll_element)
                                except:
                                    print("Warning!!! Unable to scroll down")
                                    page1_button = self.driver.find_element(By.XPATH,f'//li[@data-test-pagination-page-btn="{current_page_no}"]/button')
                                    page1_button.click()
                                    time.sleep(5)
                                    
                                
                                links = self.driver.find_elements(By.XPATH,'//div[@data-job-id]')  # needs to be scrolled down
                                IDs = []
                                for link in links:
                                    temp = link.get_attribute("data-job-id")
                                    jobID = temp.split(":")[-1]
                                    IDs.append(int(jobID))
                                IDs = set(IDs)
                                jobIDs = [x for x in IDs]
                                for jobID in jobIDs:
                                    try:     
                                        job_page = 'https://www.linkedin.com/jobs/view/' + \
                                            str(jobID)
                                        if jobID in applied_job_ids:
                                            print("Already applied to this job according to the given JobID")
                                            continue
                                        
                                        self.driver.get(job_page)
                                        close_other_tabs()
                                        count_job += 1
                                        time.sleep(random.randint(5,10))
                                        try:
                                            role=self.driver.find_elements(By.CSS_SELECTOR,".t-24")[0].text
                                            not_my_role=True
                                            for i in roles:
                                                if i.lower() in role.lower() :
                                                    not_my_role=False
                                            if not_my_role:
                                                print(f"{role} is not related to my role")
                                                applied_job_ids.append(jobID)
                                                with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                    pickle.dump(applied_job_ids,f)
                                                not_applied_roles.append(role)
                                                continue
                                            for i in not_roles:
                                                if i.lower() in role.lower():
                                                    not_my_role=True
                                            if not_my_role:
                                                print(f"{role} is not related to my role")
                                                applied_job_ids.append(jobID)
                                                with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                    pickle.dump(applied_job_ids,f)
                                                not_applied_roles.append(role)
                                                continue

                                            #pdb.set_trace()
                                        except Exception as error:
                                            print(error)
                                            print("I don't know the role that i was applying !!")
                                            continue
                                        try:
                                            EasyApplyButton = self.driver.find_element(By.CSS_SELECTOR,".jobs-s-apply.jobs-s-apply--fadein.inline-flex.mr2")
                                        except:
                                            EasyApplyButton = False
                                        button = EasyApplyButton
                                        if button is not False:
                                            string_easy = "* has Easy Apply Button"
                                            button.click()
                                            try:
                                                self.driver.find_element(By.CSS_SELECTOR,
                                                    "button[aria-label='Submit application']").click()
                                                applied_job_ids.append(jobID)
                                                with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                    pickle.dump(applied_job_ids,f)
                                                #time.sleep(random.randint(2,5))
                                                count_application += 1
                                                print("* Just Applied to this job!")
                                                applied_job_ids.append(jobID)
                                                with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                    pickle.dump(applied_job_ids,f)
                                                time.sleep(5)
                                            except:
                                                try:
                                                
                                                    ####Logic 1 start#######
                                                    
                                                    for g in range(5):
                                                        really_applied=False
                                                        try:
                                                            for i in range(10):
                                                                
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                    "button[aria-label='Continue to next step']").click() #click next
                                                                time.sleep(2)
                                                        except:
                                                            pass
                                                        try:
                                                            self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Submit application']").click()
                                                            applied_job_ids.append(jobID)
                                                            with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                                pickle.dump(applied_job_ids,f)
                                                            really_applied=True
                                                            time.sleep(5)
                                                            break
                                                        except:
                                                            pass
                                                        try:
                                                            self.driver.find_element(By.CSS_SELECTOR,
                                                                    "button[aria-label='Review your application']").click()
                                                        except:
                                                            pass
                                                        try:
                                                            self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Submit application']").click()
                                                            applied_job_ids.append(jobID)
                                                            with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                                pickle.dump(applied_job_ids,f)
                                                            really_applied=True
                                                            time.sleep(5)
                                                            break
                                                        except:
                                                            pass
                                                        
                                                        try:
                                                            #import pdb;pdb.set_trace()
                                                            fill_answers_by_gpt()
                                                            time.sleep(8)
                                                        except:
                                                            pass
                                                        
                                                        try:
                                                            self.driver.find_element(By.CSS_SELECTOR,
                                                                    "button[aria-label='Review your application']").click()
                                                        except:
                                                            pass
                                                        try:
                                                            application_sent = self.driver.find_element(By.CSS_SELECTOR, ".artdeco-modal__header.ember-view").text 
                                                            if application_sent == 'Application sent':
                                                                print("* Just Applied to this job!")
                                                                applied_job_ids.append(jobID)
                                                                with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                                    pickle.dump(applied_job_ids,f)
                                                                really_applied=True
                                                                count_application += 1
                                                                break
                                                        except:
                                                            pass                                               
                                                        try:
                                                            
                                                            self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Submit application']").click()
                                                            applied_job_ids.append(jobID)
                                                            with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                                pickle.dump(applied_job_ids,f)
                                                            really_applied=True
                                                            time.sleep(5)
                                                            break
                                                        except:
                                                            pass
                                                        
                                                    if not really_applied:
                                                        message(f"Cannot apply to this Job: {job_page}")
                                                        
                                                        
                                                    
                                                    
                                                    
                                                    ####Logic 1 end#######
                                                    
                                                    if not really_applied:

                                                        percen = self.driver.find_element(By.XPATH,"/html/body/div[3]/div/div/div[2]/div/div/span").text
                                                        percen_numer = int(percen[0:percen.index("%")])
                                                        if int(percen_numer) < 25:
                                                            print(
                                                                "*More than 5 pages,wont apply to this job! Link: " +job_page)
                                                            message(job_page)    
                                                        elif int(percen_numer) < 30:
                                                            try:
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Continue to next step']").click()
                                                                time.sleep(random.randint(3,5))
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Continue to next step']").click()
                                                                time.sleep(random.randint(3,5))
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Review your application']").click()
                                                                time.sleep(random.randint(3,5))
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Submit application']").click()
                                                                applied_job_ids.append(jobID)
                                                                with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                                    pickle.dump(applied_job_ids,f)
                                                                count_application += 1
                                                                print("* Just Applied to this job!")
                                                            except:
                                                                print(
                                                                    "*4 Pages,wont apply to this job! Extra info needed. Link: " +job_page)
                                                                message(job_page) 
                                                        elif int(percen_numer) < 40:
                                                            try: 
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Continue to next step']").click()
                                                                time.sleep(random.randint(3,6))
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Review your application']").click()
                                                                time.sleep(random.randint(3,6))
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Submit application']").click()
                                                                applied_job_ids.append(jobID)
                                                                with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                                    pickle.dump(applied_job_ids,f)
                                                                count_application += 1
                                                                print("* Just Applied to this job!")
                                                            except:
                                                                print(
                                                                    "*3 Pages,wont apply to this job! Extra info needed. Link: " +job_page)
                                                                message(job_page) 
                                                        elif int(percen_numer) < 60:
                                                            try:
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Review your application']").click()
                                                                time.sleep(random.randint(3,6))
                                                                self.driver.find_element(By.CSS_SELECTOR,
                                                                "button[aria-label='Submit application']").click()
                                                                applied_job_ids.append(jobID)
                                                                with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                                    pickle.dump(applied_job_ids,f)
                                                                count_application += 1
                                                                print("* Just Applied to this job!")
                                                            except:
                                                                print(
                                                                    "* 2 Pages,wont apply to this job! Unknown.  Link: " +job_page)
                                                                message(job_page) 
                                                except:
                                                    message(f"Cannot apply to this Job: {job_page}") 
                                        else:
                                            print("* Already applied!")
                                            try:
                                                applied_job_ids.append(jobID)
                                                with open(f'applied_job_id_{name}.pkl','wb') as f:
                                                    pickle.dump(applied_job_ids,f)
                                            except:
                                                message("Unable to save applied job id at Already applied position")
                                    except Exception as error:
                                        continue
                            except Exception as error:
                                message(error)
                                time.sleep(random.randint(2,20))
                                continue
                    except Exception as error:
                        continue    
                    print("Category: " + keywords[indexpag] + " ,applied: " + str(count_application) +
                        " jobs out of " + str(count_job) + ".")
                    message("Category: " + keywords[indexpag] + " ,applied: " + str(count_application) +
                        " jobs out of " + str(count_job) + ".")
                    message(f'not_applied_roles:{not_applied_roles}')
        except:
            message("Category: " + keywords[indexpag] + " ,applied: " + str(count_application) +
                " jobs out of " + str(count_job) + ".")
            message(f'not_applied_roles:{not_applied_roles}')


if __name__ == "__main__":
    try:
        start_time = time.time()
        message('Started applying jobs in linkedIn')
        ed = Linkedin()
        ed.Link_job_apply()
        end = time.time()
        message("---Took: " + str(round((time.time() - start_time)/60)) + " minute(s).")
    except Exception as error :
        message(f"error occured in linkedin job applying {error}")
        print(traceback.format_exc())
        applied_to_all=False
        while True:
            if applied_to_all:
                break
            try:
                ed.driver.close()
                ed = Linkedin()
                ed.Link_job_apply()
                applied_to_all=True
            except Exception as error:
                message(f"Error in linkedin easy apply {error}")
                break
    message("Stopped applying to LinkedIn")
    
