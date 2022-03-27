import datetime
import mysql.connector
from transformers import GPTNeoForCausalLM, GPT2Tokenizer
import config

print("Initiating GPT-Neo process")
print(datetime.datetime.now())

try:
    print("Opening database")

    # Establish database connection
    mydb = mysql.connector.connect(
    host="localhost",
    user="db_user",
    password=config.db_password,
    database="news_db"
    )

    # Initiate transaction
    # https://pynative.com/python-mysql-transaction-management-using-commit-rollback/
    # Accessed: 2022-03-26
    mydb.autocommit = False

    # Instantialize cursor
    mycursor = mydb.cursor()

    print("Querying content from oldest story in Story table")

    # TODO: Get oldest story already scraped via SMMRY API
    mycursor.execute("SELECT * FROM storyContent JOIN Story on Story.id = storyContent.id WHERE STATUS = 2 ORDER BY Story.id ASC LIMIT 1")

    story = mycursor.fetchone()

    # If there's no rows, the process is up to date with the data
    if story is not None:

        # Generate prompt ##########################################################

        # Retrieve id, title and list of sentences from story
        story_id = story[0]
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

        print("Querying historical data to calculate length of prompt to GPT-Neo")

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
        print("Generating output via GPT-Neo...\n")

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
        
        print("Successfully generated.")

        # Found data_type of sm_api_content and used for new column gpt_neo_content
        # Added gpt_neo_content with ALTER TABLE command
        # https://stackoverflow.com/questions/21772205/how-to-get-size-of-column-in-mysql-table
        # Accessed: 2022-03-26
        if gen_text is not None:

            print("Saving in database and updating status of Story")
            
            sql = "UPDATE storyContent SET gpt_neo_content = %s WHERE id = %s"

            affected_rows = mycursor.execute(sql, (gen_text, story_id))

            if affected_rows = 1:
                
                # Really should be paramaterized i.e., SET STATUS = %s
                sql = "UPDATE Story SET status = 4 where id = %s"
                
                affected_rows = mycursor.execute(sql, (id))

                if affected_rows = 1:
            
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

                    print("Successfully updated database with content")

    else:
        print("No content to process")


except ex as ex:
    print("Something error happens: ", ex)
    # reverting changes because of exception
    mydb.rollback()
finally:
    # closing database connection.
    if mydb.is_connected():
        mydb.close()
        mydb.close()
        print("connection is closed")

print("Process complete.")

print(datetime.datetime.now())
