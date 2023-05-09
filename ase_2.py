import torch
torch.set_default_tensor_type(torch.cuda.FloatTensor)
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import LlamaForCausalLM, LlamaTokenizer, GenerationConfig, pipeline
import textwrap
import pandas as pd

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
inputs = tokenizer(prompt, return_tensors="pt").to(0)
sample = model.generate(**inputs, max_length=300)
print(tokenizer.decode(sample[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"]))
path = "codegen.c"
f = open(path, "w")
f.write(tokenizer.decode(sample[0], truncate_before_pattern=[r"\n\n^#", "^'''", "\n\n\n"]))
f.close()


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
