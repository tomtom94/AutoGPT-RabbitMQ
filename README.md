# AutoGPT-RabbitMQ

This plugin allows you to communicate with your Auto-GPT instance via microservice.

## 📚 Requirements

1. Python Package: Install the pika Python package: 

    ```pip3
    pip3 install pika
    ```

    or add `pika` module in the Auto-GPT `requirements.txt` file.

2. RabbitMQ: Just start one `RabbitMQ` server thanks to this download page https://www.rabbitmq.com/download.html

## ⚙️ Installation

Follow these steps to configure the Auto-GPT RabbitMQ Plugin:

1. Clone this Repository

    ```git
    git clone https://github.com/tomtom94/AutoGPT-RabbitMQ.git
    ```

2. Navigate to the folder

    ```sh
    cd AutoGPT-RabbitMQ
    ```

3. Zip the `rabbitmq_plugin` folder

    - On MacOS, right click the `rabbitmq_plugin` folder and press `Compress`. 
    - On windows, right click the folder, and press `Send to > Compressed (zipped)`.

4. Move the zip file

    Move the new `rabbitmq_plugin.zip` file to the `Auto-GPT` plugins directory, there should already be a file there titled `__PUT_PLUGIN_ZIPS_HERE__`.

## 🔧 Configuration

1. Add new var env in the .env file in `Auto-GPT`:

    ```sh
    ################################################################################
    ### RABBITMQ PLUGIN SETTINGS
    ################################################################################
    RABBITMQ_HOST=localhost
    QUEUE_TO_RECEIVE_MESSAGE=service-to-autogpt
    QUEUE_TO_SEND_MESSAGE=autogpt-to-service
    ```

    - RABBITMQ_HOST: The RabbitMQ connection string
    - QUEUE_TO_RECEIVE_MESSAGE: Receive a message from the service to Auto-GPT via plugin
    - QUEUE_TO_SEND_MESSAGE: Send a message from Auto-GPT to the service via plugin

2. Update var env in the .env file in `Auto-GPT`:

    ```sh
    ################################################################################
    ### CHAT PLUGIN SETTINGS
    ################################################################################
    # CHAT_MESSAGES_ENABLED - Enable chat messages (Default: False)
    CHAT_MESSAGES_ENABLED=True
    ```

    - CHAT_MESSAGES_ENABLED: By default it's False, this plugin needs this var to be True otherwise this plugin would be useless

3. Update var env in the .env file in `Auto-GPT`:

    ```sh
    ################################################################################
    ALLOWLISTED PLUGINS
    ################################################################################

    #ALLOWLISTED_PLUGINS - Sets the listed plugins that are allowed (Example: plugin1,plugin2,plugin3)
    ALLOWLISTED_PLUGINS=AutoGPTRabbitMQ
    ```

## ► Listen RabbitMQ on your client microservice

1. Use the same env vars in your service, but reverse their value between `QUEUE_TO_RECEIVE_MESSAGE` & `QUEUE_TO_SEND_MESSAGE`

    ```sh
    RABBITMQ_HOST=localhost
    QUEUE_TO_RECEIVE_MESSAGE=autogpt-to-service
    QUEUE_TO_SEND_MESSAGE=service-to-autogpt
    ```

2. First Auto-GPT talks to you, so listen to it via a consumer in a thread

   This plugin RabbitMQ for AutoGPT has for mission to send all the ouput into the designed for `QUEUE_TO_SEND_MESSAGE`,
   The format sent are of type :

    ```
    {'role': 'POST_COMMAND', 'content': 'The message Auto-GPT has written, given line by line'}
    {'role': 'POST_INSTRUCTION', 'content': '...'}
    {'role': 'REPORT', 'content': '...'}
    ```

    Your service needs to work the same way the plugin works with RabbitMQ via pika.
   
   - It means you need to create a consumer of that kind [start_consumer](/rabbitmq_plugin/rabbitmq_plugin.py#L62) which will make a thread of this function [run_consumer](/rabbitmq_plugin/rabbitmq_plugin.py#L16). Insteand of this code [`userReply.append(body.decode())`](/rabbitmq_plugin/rabbitmq_plugin.py#L30) just use straight `body.decode()` to receive the prompt line by line, and do whatever you want with.
   - And then send message when you wanna reply to the prompt [send_message](/rabbitmq_plugin/rabbitmq_plugin.py#L58)
   - With the same env vars but remember we reversed their value, so just copy past these 3 functions, that's it.

    There are special kill codes, sent sometimes from one procuder to a consumer, depends which process triggers the end :
    - `SIGTERM_FROM_SERVICE`
    - `SIGTERM_FROM_AUTOGPT`

    It allows to kill the consumer in a thread from the inside properly.
    Just need to mirror this pattern on your service side.

4. Finally Auto-GPT asks you to reply, so send a message in the queue for that

    Once everything has been started properly, and is able to stop properly. Just send a message from your service to Auto-GPT like this function [send_message](/rabbitmq_plugin/rabbitmq_plugin.py#L58) does from Auto-GPT to your service.
    Just need to mirror this pattern on your service side.
