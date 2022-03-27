import datetime
import mysql.connector
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import config

print(datetime.datetime.now())

# Establish database connection
mydb = mysql.connector.connect(
  host="localhost",
  user="db_user",
  password=config.db_password,
  database="news_db"
)

# Instantialize cursor
mycursor = mydb.cursor()

# TODO: Get oldest story already scraped via SMMRY API
mycursor.execute("SELECT * FROM storyContent WHERE STATUS = 2 ORDER BY ID ASC LIMIT 1")

story = mycursor.fetchone()

# If there's no rows, the process is up to date with the data
if story is not None:

    # Generate prompt ##########################################################

    # Retrieve title and list of sentences from story
    title = story[6].strip()
    sentences = story[3].split('[BREAK]')

    sm_api_content = sentences[0].strip()

    # Check that title and zeroth sentence are different
    if(title.lower() in sm_api_content.lower() or sm_api_content.lower() in title.lower()):
        # TODO: Detect sentences that are highly similar yet not identical to title
        sm_api_content = sentences[1].strip()

    # Generate prompt, separate title and content by paragraph break
    # Concatenate triple quoted string with title and content
    # Source:   https://stackoverflow.com/questions/24070819/concatenation-of-triple-quoted-strings
    # Accessed: 2021-12-31
    prompt = f'''{title}\n\n{sm_api_content}'''

    print(prompt)

    # Calculate original length of story #######################################

    # Retrieve story length and percent reduced
    sm_api_character_count = story[4]
    sm_api_content_reduced = story[5]

    # Determine reduction factor so that we can reverse engineer original length
    reduction_factor = ((100 - sm_api_content_reduced) / 100)

    # Original length is reduced text size divided by reduction factor
    original_length = sm_api_character_count / reduction_factor

    # Calculate prompt_length ##################################################
    # prompt_length =   (desired output amount)
    #                 ÷ ((total character count ever produced) / (total length ever requested))
    #                 ------------------------------------------------------------------------

    # Retrieve available historical data
    mycursor.execute("SELECT * FROM tokens LIMIT 1")

    token_data = mycursor.fetchone()

    if token_data is not None:
        avg_output_length = token_data[1]
        avg_prompt_length = token_data[0]
    else:
        avg_output_length = 9
        avg_prompt_length = 2
    
    token_ratio = avg_output_length / avg_prompt_length

    prompt_length = round(original_length / token_ratio)

    # Use GPT-Neo to generate text from prompt #################################

    # Followed tutorial by Blake M for using transformers and GPT Neo
    # Source:   https://www.youtube.com/watch?v=d_ypajqmwcU
    #           https://github.com/mallorbc/GPTNeo_notebook
    # Accessed: 2021-12-30
    # TODO: Allow use of CUDA capability
    model_name = "EleutherAI/gpt-neo-2.7B"
    model = GPTNeoForCausalLM.from_pretrained(model_name)

    tokenizer = GPT2Tokenizer.from_pretrained(model_name)

    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

    gen_tokens = model.generate(input_ids, do_sample=True, temperature=0.9, max_length=prompt_length)

    gen_text = tokenizer.batch_decode(gen_tokens)[0]
    print(gen_text)

    # Get length of text
    # TODO: Detect unusually short output length
    output_length = len(gen_text)

    # Save prompt length and generated length
    if token_data is None:
        sql = "INSERT INTO tokens (prompt_length, output_length) VALUES (%s, %s)"
    else:
        sql = "UPDATE tokens SET prompt_length = %s, output_length = %s"

        output_length += avg_output_length
        prompt_length += avg_prompt_length

    val = (prompt_length, output_length)

    mycursor.execute(sql, val)

    mydb.commit()

else:
    print("No content to process")

print(datetime.datetime.now())
