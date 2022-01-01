import datetime
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import config

print(datetime.datetime.now())

# Followed tutorial by Blake M for using transformers and GPT Neo
# Source:   https://www.youtube.com/watch?v=d_ypajqmwcU
#           https://github.com/mallorbc/GPTNeo_notebook
# Accessed: 2021-12-30
# TODO: Allow use of CUDA capability
model_name = "EleutherAI/gpt-neo-2.7B"
model = GPTNeoForCausalLM.from_pretrained(model_name)

tokenizer = GPT2Tokenizer.from_pretrained(model_name)

prompt = config.prompt

# Calculate output length based on historical data
# output_length =   (desired output amount)
#                 ÷ (total character count ever produced) / (total length ever requested)
#                 -----------------------------------------------------------------------
# If historical data not available, assume 4 default ratio                 
output_length = 500

input_ids = tokenizer(prompt, return_tensors="pt").input_ids

gen_tokens = model.generate(input_ids, do_sample=True, temperature=0.9, max_length=output_length)

gen_text = tokenizer.batch_decode(gen_tokens)[0]
print(gen_text)

# Get length of text
len_text = len(gen_text)

# Save output length and generated length
print("Length of generated text: " + str(len_text))
print("Ratio ~=" + str(len_text/output_length))

print(datetime.datetime.now())
