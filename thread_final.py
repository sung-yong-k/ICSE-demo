import threading
import torch
torch.set_default_tensor_type(torch.cuda.FloatTensor)
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import LlamaForCausalLM, LlamaTokenizer, GenerationConfig, pipeline
import textwrap
import pandas as pd
import queue
import openai
from infer_test import*
from cppcheck_test import*
import os
import time

print("install openai and cppcheck and create production before before")
key = input("Enter a key: ")
openai.api_key = key

def extract_substring(s, start_str, end_str):
    """
    Extract a substring from s that starts with start_str and ends with end_str.
    """
    start_index = s.find(start_str) + len(start_str)
    end_index = s.rfind(end_str, start_index)
    if start_index < 0 or end_index < 0:
        return ""
    return s[start_index-8:end_index+1]


def generation(prompt, gpt_msg, user_prompt):
    prompt2 = "Complete this code \n"+prompt
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    temperature= 0,
    messages=[
    {"role": "system", "content": "You are a coding assistant and help the user."},
    {"role": "user", "content": "When I say complete a code, I want you to complete it and give back the function from the beginning."},
    {"role": "assistant", "content": "Sure! Please provide the code snippet that you want me to complete."},
    {"role": "user", "content": prompt2},
    {"role": "assistant", "content": gpt_msg},
    {"role": "user", "content": user_prompt+"\n"+prompt}] )

    #print(response)
    if 'choices' in response:
        x = response['choices']
        #print( x[0]['message']['content'])
        answer = x[0]['message']['content']
        code= extract_substring(answer,"#include","}")
        return code





#tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-multi")
#model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-multi")


tokenizer_gpt4all = AutoTokenizer.from_pretrained("nomic-ai/gpt4all-j")
model_gpt4all = AutoModelForCausalLM.from_pretrained("nomic-ai/gpt4all-j",
                                             load_in_8bit=True,
                                             device_map="auto")



def thread_func1(value,prompt):
    weight = 0
    print("Thread 1 is running...")
    inputs = tokenizer(prompt, return_tensors="pt").to(0)
    sample = model.generate(**inputs, max_length=600)
    print(tokenizer.decode(sample[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"]))
    path = "codegen.c"
    f = open(path, "w")
    f.write(tokenizer.decode(sample[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"]))
    f.close()
    
    create_command = "flawfinder --csv --minlevel=2 codegen.c > flawfinder1.csv"
    print("launching flawfinder")
    print(create_command)
    os.system(create_command)
    
    create_command = "cppcheck --xml-version=2 --enable=all codegen.c 2> cpp1.xml"
    os.system(create_command)
    '''
    create_command = "infer run --bufferoverrun --pulse  -- gcc -c codegen.c"
    os.system(create_command)
    '''
    
    res = pd.read_csv("flawfinder1.csv", header=None)
    print("openning sucessful")
    flawfinder_detected = True
    try:
        code = res.iloc[1][0]
        print(code)
    except Exception as e:
        print(e)
        print("Flawfinder null")
        flawfinder_detected = False
    for p in range(1,2):
        ignore_list =[]
        CWE = None
        if flawfinder_detected:
            #We get the error message
            error = res.iloc[p][7]
            print(error)

            #We get the vulnerable line
            line = int(res.iloc[p][1])
            print(line)
            vuln_line = line
            #We get the function name
            function_name = res.iloc[p][6]
            print(function_name)
            
            #delete la ligne
            #if function_name =="char":
               # continue

            
            try:
                print("we try to get the suggestion")
                suggestion = res.iloc[p][8]
                print("we get the suggestion")
            except :
                print("no suggestion")
                suggestion = error
            
            #We get the CWEs
            try:
                CWE = res.iloc[p][10]
                print(CWE)
            except:
                print("CWE get error")
                
            for d in range (p+1,len(res)):
                if res.iloc[d][10] == CWE:
                    ignore_list.append(int(res.iloc[d][1]))
                    print("on ajoute une erreur répétée")
        
        #cppcheck
        cpp_cwe = None
        try:
        #error_info.append([message,cwe,line])
            cpp_result = extract_error_info("cpp1.xml")
            print("cpp:")
            print(cpp_result)
            if len(cpp_result) == 0:
                print("cppcchekc empty")
                cpp_error=None
                cpp_cwe = None
                cpp_line = None
            else:
                print("cppcheck not empty")
                cpp_error=cpp_result[0][0]
                cpp_cwe=cpp_result[0][1]
                cpp_line=cpp_result[0][2]
        except Exception as e:
            print(e)
        
        #infer
        '''
        bug_type, infer_msg, infer_line = extract_bug_details('infer-out/report.json')
        print("infer: ")
        print( bug_type, infer_msg, infer_line)
        '''
        bug_type = None
        #Ranking error
        print("ranking")

      
        if bug_type != None:
            print("on est chez infer")
            CWE = bug_type
            suggestion= infer_msg
            vuln_line = infer_line
            weight=2
        elif cpp_cwe != None:
            print("on est chez cpp")
            CWE = cpp_cwe
            suggestion= cpp_error
            vuln_line = cpp_line
            weight=1
        elif CWE == None:
            print("no vuln detected")
            weight = 0
            CWE = None
            suggestion =""
            vuln_line = None

        print([weight,CWE,suggestion,vuln_line])
        time.sleep(5)
        value.put([weight,CWE,suggestion,vuln_line])
        break



    
    
    
    
    
    
def thread_func2(value,prompt):
    weight =0
    print("Thread 2 is running...")
    generate_text = pipeline(
        "text-generation",
        model=model_gpt4all,
        tokenizer=tokenizer_gpt4all,
        max_length=600,
        temperature=0.1,
        top_p=0.95,
        repetition_penalty=1.15
    )

    def wrap_text_preserve_newlines(text, width=110):
        # Split the input text into lines based on newline characters
        lines = text.split('\n')

        # Wrap each line individually
        wrapped_lines = [textwrap.fill(line, width=width) for line in lines]

        # Join the wrapped lines back together using newline characters
        wrapped_text = '\n'.join(wrapped_lines)

        return wrapped_text

    gpt4all_output = generate_text(prompt)
    #gpt4all_output = wrap_text_preserve_newlines(gpt4all_output[0]['generated_text'])
    print(wrap_text_preserve_newlines(gpt4all_output[0]['generated_text']))
    path = "gpt4all.c"
    f = open(path, "w")
    f.write(extract_substring(gpt4all_output[0]['generated_text'],"#include","}"))
    f.close()
    

    create_command = "flawfinder --csv --minlevel=2 gpt4all.c > flawfinder2.csv"
    print("launching flawfinder")
    print(create_command)
    os.system(create_command)
    
    create_command = "cppcheck --xml-version=2 --enable=all gpt4all.c 2> cpp2.xml"
    os.system(create_command)
    
    '''
    create_command = "infer run --bufferoverrun --pulse  -- gcc -c codegen.c"
    os.system(create_command)
    '''
    
    res = pd.read_csv("flawfinder2.csv", header=None)
    print("openning sucessful")
    flawfinder_detected = True
    try:
        code = res.iloc[1][0]
        print(code)
    except Exception as e:
        print(e)
        print("Flawfinder null")
        flawfinder_detected = False
    for p in range(1,2):
        ignore_list =[]
        
        CWE = None
        #We get the error message
        if flawfinder_detected:
            error = res.iloc[p][7]
            print(error)

            #We get the vulnerable line
            line = int(res.iloc[p][1])
            print(line)
            vuln_line = line
            #We get the function name
            function_name = res.iloc[p][6]
            print(function_name)
            
            #delete la ligne
            #if function_name =="char":
               # continue
            
            try:
                print("we try to get the suggestion")
                suggestion = res.iloc[p][8]
                print("we get the suggestion")
            except :
                print("no suggestion")
                suggestion = error
            
            #We get the CWEs
            try:
                CWE = res.iloc[p][10]
                print(CWE)
            except:
                print("CWE get error")

            for d in range (p+1,len(res)):
                if res.iloc[d][10] == CWE:
                    ignore_list.append(int(res.iloc[d][1]))
                    print("on ajoute une erreur répétée")
        
        #cppcheck
        cpp_cwe = None
        try:
        #error_info.append([message,cwe,line])
            cpp_result = extract_error_info("cpp2.xml")
            print("cpp:")
            print(cpp_result)
            if len(cpp_result) == 0:
                print("cppcheck empty")
                cpp_error=None
                cpp_cwe = None
                cpp_line = None
            else:
                print("cppcheck not empty")
                cpp_error=cpp_result[0][0]
                cpp_cwe=cpp_result[0][1]
                cpp_line=cpp_result[0][2]
            
        except Exception as e:
            print(e)
        
        #infer
        '''
        bug_type, infer_msg, infer_line = extract_bug_details('infer-out/report.json')
        print("infer: ")
        print( bug_type, infer_msg, infer_line)
        '''
        bug_type = None
        #Ranking error
        print("ranking")
        print(bug_type)
        print(cpp_cwe)
        if bug_type != None:
            print("on est chez infer")
            CWE = bug_type
            suggestion= infer_msg
            vuln_line = infer_line
            weight=2
        elif cpp_cwe != None:
            print("on est chez cpp")
            CWE = cpp_cwe
            suggestion= cpp_error
            vuln_line = cpp_line
            weight=1
        elif CWE == None:
            weight = 0
            CWE = None
            suggestion =""
            vuln_line = None
        
        gpt4all_output =extract_substring(gpt4all_output[0]['generated_text'],"#include","}")
        print([weight,CWE,suggestion,vuln_line])
        time.sleep(5)
        value.put([weight,CWE,suggestion,vuln_line, gpt4all_output])
        break



if __name__ == "__main__":
#fix si flawfinder est null
    report_text=""
    for root, dirs, files in os.walk("prompt"):
        for file_name in files:
            print("file name is: ")
            print(file_name)
            if file_name != ".DS_Store":
                file_path = os.path.join(root, file_name)
                input = open("prompt/"+file_name, "r",encoding='utf-8')
                line = input.readlines()
                input.close()
                total_lines = len(line)
                copy_lines = int(total_lines * 0.5)
                prompt = "".join(line[:copy_lines])
                start_time = time.time()
                #q1 = queue.Queue()
                q2 = queue.Queue()
                #t1 = threading.Thread(target=thread_func1, args=(q1,prompt))
                t2 = threading.Thread(target=thread_func2, args=(q2,prompt))
                
                #t1.start()
                t2.start()
                
                #result1 = q1.get()
                result2 = q2.get()
                
                #t1.join()
                t2.join()
'''
                if result1[1] == None and result2[1] == None:
                    print("pas eu de vuln detected")
                    break
                if result1[0] > result2[0]:
                    comment_error = "Complete the following code and do not generate the vulnerability" + result1[1] + " "  + result1[2]
                else:
                    comment_error = "Complete the following code and do not generate the vulnerability" + result2[1] + " "  + result2[2]
'''
                if result2[1] == None:
                    print("pas eu de vuln detected")
                    break
                else:
                    comment_error = "The previous code has the vulnerability" + result2[1] + " at line:"+result2[3]+". Complete again the following code from scratch without generating the vulnerability: "
                
                gpt_msg = result2[-1]
                user_prompt = comment_error
                print("on lance la generation")
                answer =  generation(prompt, gpt_msg, user_prompt)
                final_time = time.time()-start_time
                destination_file_path = os.path.join("production", file_name)
                code = open(destination_file_path,"w")
                code.write(answer)
                code.close()
                report_text=report_text+file_name+":"+comment_error+ "time : "+ str(final_time)+"\n"
    report=open("production/report.txt","w")
    report.write(report_text)
    report.close()
