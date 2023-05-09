import threading
import torch
torch.set_default_tensor_type(torch.cuda.FloatTensor)
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import LlamaForCausalLM, LlamaTokenizer, GenerationConfig, pipeline
import textwrap
import pandas as pd
import queue
import openai
openai.api_key = "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"

def extract_substring(s, start_str, end_str):
    """
    Extract a substring from s that starts with start_str and ends with end_str.
    """
    start_index = s.find(start_str) + len(start_str)
    end_index = s.rfind(end_str, start_index)
    if start_index < 0 or end_index < 0:
        return ""
    return s[start_index-8:end_index+1]


def generation(input):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    temperature= 0,
    messages=[
    {"role": "system", "content": "You are a coding assistant and help the user."},
    {"role": "user", "content": "When I say complete a code, I want you to complete it and give back the function from the beginning."},
    {"role": "assistant", "content": "Sure! Please provide the code snippet that you want me to complete."},
    {"role": "", "content": "Sure! Please provide the code snippet that you want me to complete."},
    {"role": "user", "content": input}] )

    #print(response)
    if 'choices' in response:
        x = response['choices']
        #print( x[0]['message']['content'])
        answer = x[0]['message']['content']
        #code= extract_substring(answer,"#include","}")
        return answer





tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-multi")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-multi")


tokenizer_gpt4all = AutoTokenizer.from_pretrained("nomic-ai/gpt4all-j")
model_gpt4all = AutoModelForCausalLM.from_pretrained("nomic-ai/gpt4all-j",
                                             load_in_8bit=True,
                                             device_map="auto")

prompt= '''#include <stdio.h>
#include <stdlib.h>
int main(int argc, char *argv[]) {
    int value = 0;
    //read in the value from the command line
    if (argc > 1) {
        value = atoi(argv[1]);
    }
    //calculate the correct value with the offset of 1000 added'''

def thread_func1(value,prompt):
    weight = 0
    print("Thread 1 is running...")
    inputs = tokenizer(prompt, return_tensors="pt").to(0)
    sample = model.generate(**inputs, max_length=300)
    print(tokenizer.decode(sample[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"]))
    path = "codegen.c"
    f = open(path, "w")
    f.write(tokenizer.decode(sample[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"]))
    f.close()
    
    create_command = "flawfinder --csv --minlevel=2 codegen.c 2> flawfinder1.csv
    print("launching flawfinder")
    print(create_command)
    os.system(create_command)
    
    create_command = "cppcheck --xml-version=2 --enable=all codegen.c 2> cpp1.xml"
    os.system(create_command)
    
    create_command = "infer run --bufferoverrun --pulse  -- gcc -c codegen.c"
    os.system(create_command)
    
    
    res = pd.read_csv("flawfinder1.csv", header=None)
    print("openning sucessful")
    for p in range(1,len(res)):
        ignore_list =[]
        
        #We get the error message
        error = res.iloc[p][7]
        print(error)

        #We get the vulnerable line
        line = int(res.iloc[p][1])
        print(line)
        print(file_length)
        vuln_line = line
        #We get the function name
        function_name = res.iloc[p][6]
        print(function_name)
        
        #delete la ligne
        #if function_name =="char":
           # continue
        if i == 0:
            previous_error_line = p
        #We get the suggestion
        print("we get the suggestion")
        
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
        '''
        if CWE == "CWE-362" or CWE=="CWE-120":
            for d in range (2,len(res)):
                if res.iloc[d][10] == "CWE-362" or res.iloc[d][10] == "CWE-120":
                    ignore_list.append(int(res.iloc[d][1]))
                    print("on ajoute une erreur répétée"
        '''
        for d in range (p+1,len(res)):
            if res.iloc[d][10] == CWE:
                ignore_list.append(int(res.iloc[d][1]))
                print("on ajoute une erreur répétée")
        
        #cppcheck
        try:
        #error_info.append([message,cwe,line])
            cpp_result = extract_error_info("cpp1.xml")
            print("cpp:")
            print(cpp_result)
            if len(cpp_result) == 0:
                print("hola")
                cpp_error=None
                cpp_cwe = None
                cpp_line = None
            else:
                cpp_error=cppcheck[0][0]
                cpp_cwe=cppcheck[0][1]
                cpp_line=cppcheck[0][2]
            
        except Exception as e:
            print(e)
        
        #infer
        bug_type, infer_msg, infer_line = extract_bug_details('infer-out/report.json')
        print("infer: ")
        print( bug_type, infer_msg, infer_line)
        
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
        
        value.put([weight,CWE,suggestion,vuln_line])
        break
       ''' try:
            #We get the appropriate comment for the error
            comment_error = "Avoid " + CWE + " "  + suggestion+ " at line: "+vuln_line
            print("comment build")
        except:
            print("comment creation error")
            comment_error ="Avoid " + CWE + " "+ error'''


    
    
    
    
    
    
def thread_func2(value,prompt):
    weight =0
    print("Thread 2 is running...")
    generate_text = pipeline(
        "text-generation",
        model=model_gpt4all,
        tokenizer=tokenizer_gpt4all,
        max_length=512,
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
    f.write(gpt4all_output[0]['generated_text'])
    f.close()
    

    create_command = "flawfinder --csv --minlevel=2 codegen.c 2> flawfinder2.csv
    print("launching flawfinder")
    print(create_command)
    os.system(create_command)
    
    create_command = "cppcheck --xml-version=2 --enable=all codegen.c 2> cpp2.xml"
    os.system(create_command)
    
    create_command = "infer run --bufferoverrun --pulse  -- gcc -c codegen.c"
    os.system(create_command)
    
    
    res = pd.read_csv("flawfinder2.csv", header=None)
    print("openning sucessful")
    for p in range(1,len(res)):
        ignore_list =[]
        
        #We get the error message
        error = res.iloc[p][7]
        print(error)

        #We get the vulnerable line
        line = int(res.iloc[p][1])
        print(line)
        print(file_length)
        vuln_line = line
        #We get the function name
        function_name = res.iloc[p][6]
        print(function_name)
        
        #delete la ligne
        #if function_name =="char":
           # continue
        if i == 0:
            previous_error_line = p
        #We get the suggestion
        print("we get the suggestion")
        
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
        '''
        if CWE == "CWE-362" or CWE=="CWE-120":
            for d in range (2,len(res)):
                if res.iloc[d][10] == "CWE-362" or res.iloc[d][10] == "CWE-120":
                    ignore_list.append(int(res.iloc[d][1]))
                    print("on ajoute une erreur répétée"
        '''
        for d in range (p+1,len(res)):
            if res.iloc[d][10] == CWE:
                ignore_list.append(int(res.iloc[d][1]))
                print("on ajoute une erreur répétée")
        
        #cppcheck
        try:
        #error_info.append([message,cwe,line])
            cpp_result = extract_error_info("cpp2.xml")
            print("cpp:")
            print(cpp_result)
            if len(cpp_result) == 0:
                print("hola")
                cpp_error=None
                cpp_cwe = None
                cpp_line = None
            else:
                cpp_error=cppcheck[0][0]
                cpp_cwe=cppcheck[0][1]
                cpp_line=cppcheck[0][2]
            
        except Exception as e:
            print(e)
        
        #infer
        bug_type, infer_msg, infer_line = extract_bug_details('infer-out/report.json')
        print("infer: ")
        print( bug_type, infer_msg, infer_line)
        
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
            
        value.put([weight,CWE,suggestion,vuln_line])
        break



if __name__ == "__main__":
#fix si flawfinder est null
    q1 = queue.Queue()
    q2 = queue.Queue()
    t1 = threading.Thread(target=thread_func1, args=(q1,prompt))
    t2 = threading.Thread(target=thread_func2, args=(q2,prompt))
    
    t1.start()
    t2.start()
    
    result1 = q1.get()
    result2 = q2.get()
    
    t1.join()
    t2.join()

    if result1[0] >= result2[0]:
        comment_error = "Write the following code and do not generate the vulnerability" + result1[1] + " "  + result1[2]+ " at line: "+result1[3]
    else:
        comment_error = "Write the following code and do not generate the vulnerability" + result2[1] + " "  + result2[2]+ " at line: "+result2[3]
    user_prompt = comment_error+"\n"+prompt
    print(generation(user_prompt))
