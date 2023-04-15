![GPTContext](https://user-images.githubusercontent.com/55434969/225579902-ffe9a506-3cc3-4bfa-aca3-e563bcfe87eb.png)


# GPTContext

The Flask backend for GPTContext app that allows user to upload context files and query chat GPT AI based on it.

## Technical Overview

The project leverages dataloaders from Llama Hub AI to create indices over the data that is being fed through the front-end. The files are stored in a directory in the server to be processed and deleted after 5 minutes. The Llama index library is used to process the data which is then passed into a GPTSimpleVectorIndex to create an index.

## Usage
- In the web application, drag your files into the blue zone, or select choose file and choose your files.
- Click submit.
- The files will be uploaded and processed.
- There should be a confirmation message prompting you to now start the conversation.
- The session would expire in 5 minutes and your files will be deleted from the server.
- The application will restart.
- You can always restart the session by clicking tthe refresh icon at the bottom left of the interface

## Follow this steps to setup and use locally

## Installation Backend

1. Download the project from github  
2. Make sure to set your OPEN_AI_KEY environment variable using keys.py or just storing it in the os.env.
3. Set your BEARER_TOKEN using the same keys.py file (uncomment the part of the code that imports and use keys.py) or set it using the os environment.
4. Get an OpenAI API key and store it in a file named `keys.py` at the root directory with the name `OPENAI_API_KEY` and store a random 'BEARER_TOKEN' variable. This will mathc 
5. Open a terminal and navigate to the project directory.
6. Install the Python dependencies by running the following command:
``` pip install -r requirements.txt ```
7. Run the flask server with the following command ``` python app.py ```

## Installation Frontend

1. Download the project from GitHub.
2. Open in a terminal.
3. ```npm install``` to install all dependencies
4. ```npm start``` to start the server.
5. Create a .env file and create a environmental variable 'REACT_APP_BEARER_TOKEN'. This would be the same with the BEARER_TOKEN at the flask backend for authentication purposes

### If you want to host it locally, follow the backend configurations above and get the locally hosted link and follow the steps below & set the frontend to use that route
1. In the frontend directory inside the utis/api, set the api to use your localhost
2. Restart the server.
3. Project should run locally now.


## Contributing

I welcome contributions from anyone! To contribute to this project, follow these steps:

1. Fork the repository to your own GitHub account.
2. Clone the forked repository to your local machine.
3. Create a new branch for your changes with a descriptive name (e.g., `fix-bug-123`).
4. Make your changes to the codebase.
5. Commit your changes with a clear and descriptive commit message.
6. Push your changes to your forked repository.
7. Create a pull request (PR) from your forked repository to the original repository's `master` branch.
8. Describe your changes in the PR description and link to any relevant issues or pull requests.
9. Wait for feedback.

Thank you for your interest in contributing to this project!




