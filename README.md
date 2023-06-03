# AutoGPT-RabbitMQ

This plugin allows you to communicate with your AutoGPT instance via microservice.

## 📚 Requirements

1. Python Package: Install the pika Python package: 

    ```pip3
    pip3 install pika
    ```

    or add `pika` module in the Auto-GPT `requirements.txt` file.

2. RabbitMQ: Just start one `RabbitMQ` server thanks to this download page https://www.rabbitmq.com/download.html

## ⚙️ Installation

Follow these steps to configure the AutoGPT RabbitMQ Plugin:

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

1. Use the same env var, but reverse their value between them

    ```sh
    RABBITMQ_HOST=localhost
    QUEUE_TO_RECEIVE_MESSAGE=autogpt-to-service
    QUEUE_TO_SEND_MESSAGE=service-to-autogpt
    ```

2. First Auto-GPT talks to you, so listen to it

    ```python
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    userReply = []
    channel.queue_declare(queue=QUEUE_TO_RECEIVE_MESSAGE)
    def callback(ch, method, properties, body):
            print(Fore.MAGENTA + "User replied: %r" % body.decode())
            userReply.append(body.decode())
            if body.decode()['role'] == "USER_INPUT":
                # Auto-GPT is asking you to reply, so kill this process and get back to your normal server tasks
                channel.stop_consuming()
    channel.basic_consume(queue=QUEUE_TO_RECEIVE_MESSAGE, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

    print(userReply.pop(0)) # you can do whatever you want with messages received from Auto-GPT
    ```

3. Finally Auto-GPT asks you to reply, so send a message

    ```python
    channel.queue_declare(queue=QUEUE_TO_SEND_MESSAGE)
    channel.basic_publish(exchange='', routing_key=QUEUE_TO_SEND_MESSAGE, body="Make a poem for my dog in a text file please")
    ```
