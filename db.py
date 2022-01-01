import mysql.connector
import config

mydb = mysql.connector.connect(
  host="localhost",
  user="db_user",
  password=config.db_password,
  database="news_db"
)

mycursor = mydb.cursor()

# TODO: Get oldest story already scraped 
# TODO: SELECT * FROM stories WHERE status = 'GPT' ORDER BY pubDate ASC LIMIT 1
mycursor.execute("SELECT * FROM stories LIMIT 1")

story = mycursor.fetchone()

# If there's no rows, the process is up to date with the data
if story is not None:

  # Generate prompt ############################################################

  # Retrieve title and first sentence from story
  title = story[7]
  sm_api_content = story[4].split('[BREAK] ')[0]

  # Generate prompt, separate title and content by paragraph break
  # TODO: Replace \" and \' escape characters
  # TODO: prompt is a triple quoted string
  #       https://stackoverflow.com/questions/24070819/concatenation-of-triple-quoted-strings
  prompt = title + '\n\n' + sm_api_content

  print(prompt)

  # Calculate original length ##################################################

  # Retrieve story length and percent reduced
  sm_api_character_count = story[5]
  sm_api_content_reduced = story[6]

  # Determine reduction factor so that we can reverse engineer original length
  reduction_factor = ((100 - sm_api_content_reduced) / 100)

  # Original length is reduced text size divided by reduction factor
  original_length = sm_api_character_count / reduction_factor

  mycursor.execute("SELECT * FROM tokens LIMIT 1")

  data = mycursor.fetchone()

  if data is not None:
    token_ratio = data[1] / data[0]
  else:
    token_ratio = 4
  
  output_length = round(original_length / token_ratio)

  print(output_length)

  