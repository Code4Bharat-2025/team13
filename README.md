FunWithFlags Chatbot

    Challange -->

    Building a chatbot that turns national flags  into a  interactive gussing games . 
    Using FlagCDN,the bot randomly displays a  flag image and asks: " Which country  does this belong to ?"
    The user is given four optiokns to choose from - one correct, three randomized.
    Once user selects an answer, the bot provides instant feedback along with a funfact about the country/ the flag itself.
    the tone should be warm, cheerful and education - making each guess feel like a mini journey to a new place.
   
    Solution --> 
          
    A smart, interactive chatbot designed to provide a gaming environment to User. Whether you're a casual gamer or a hardcore player, 
    this bot enhances you Global knowledge about the countries flags , their capital and important facts about the country includes their cultural identity, famous places in the country etc .



🚀 Features
    🎮 Interactive chatbot for Gaming

    🏆 Score Tracking 

    🎭 Level-based Quiz Launch (e.g. Easy, Medium, Hard)

    🔀 Break predictable sequences to enhance engagement and reduce repetition


🛠️ Technologies

    Backend  : Python FastAPI

    Database  : Firebase 

    Flag Display : FlagCDN for crisp and  scalable flag images

    Trivia Data : restCountries API  for flag meaning an cultural flags

    Chat UI : SwiftChat SDK

🛠️ Setup Instructions
Follow the steps below to set up and run the Gaming Chatbot locally:

        1️⃣ Clone the Repository
       
        git clone https://github.com/Code4Bharat-2025/team13.git
        
        
        2️⃣ Software Installations
            1.Install Python 3 /MiniConda

                Create Enviornment
                    conda create -n funwithflags python=3.12

                Activate ENviornmnet
                    conda activate funwithflags

                Install modules using pip
                    pip install -r requirements.txt

                Run FastAPI
                    uvicorn main:app --reload

                Start the Ngrok tunnel
                    ngrok http 8000 # port is based on the FastAPI standard port

                Update bot webhook 
                    https://v1-api.swiftchat.ai/api/bots/0250054444411113/webhook-url
                    {
                        "webhook_url": "<yourngrok url>/webhook"
                    }



        
✅ Optional: Test the Setup

        1.In .env file API key need to be replaced with VALID API Key
        
        2.Run basic tests to ensure the chatbot is working using below chatbot URL-
        https://web.convegenius.ai/bots?botId=0250054444411113

📌 Notes
    Ensure Python 3.8+ is installed using installion steps above 
    Ensure Firebase 1.0.0 is installed.


    
