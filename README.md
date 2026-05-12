# EmailParser
Analyze customer emails with AI

Outputs a JSON response displayed using Streamlit

Can work with multiple LLM models via LiteLLM

## How to run
I suggest making a Python virtual environment `python -m venv PROJECTNAME`, otherwise skip to the pip command

Activate the virtual environment:

`PROJECTNAME\Scripts\Activate`

Install the required packages with the following command:

`pip install -r requirements.txt`

Enter the API key in the `.env` file (refer to `.envsample` for the format)

>*I suggest using Gemini for its free and no-cost API key used for prototyping*

Run the program with this command:

`steamlit run app.py`

It will launch the browser and open the app page. Simply do `Ctrl+C` on the terminal to stop the program
