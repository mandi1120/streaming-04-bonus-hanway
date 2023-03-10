"""
Author: Amanda Hanway 
Assignment: Bonus - A4: Producer with Multiple Consumers
Date: 1/29/23
Purpose: 
    This program reads two columns of data from a csv file 
    then sends the data as a message to two queues on the RabbitMQ server    
Csv data source: insurance_data.csv
https://www.kaggle.com/datasets/thedevastator/insurance-claim-analysis-demographic-and-health?resource=download      
"""


import pika
import sys
import webbrowser
import csv
import time

def offer_rabbitmq_admin_site(show_offer):
    if show_offer == True:

        """Offer to open the RabbitMQ Admin website"""
        ans = input("Would you like to monitor RabbitMQ queues? y or n ")
        print()
        if ans.lower() == "y":
            webbrowser.open_new("http://localhost:15672/#/queues")
            print()

def send_message(host: str, queue_name: str, message: str):
    """
    Creates and sends a message to the queue each execution.
    This process runs and finishes.

    Parameters:
        host (str): the host name or IP address of the RabbitMQ server
        queue_name (str): the name of the queue
        message (str): the message to be sent to the queue
    """

    try:
        # create a blocking connection to the RabbitMQ server
        conn = pika.BlockingConnection(pika.ConnectionParameters(host))
        # use the connection to create a communication channel
        ch = conn.channel()
        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        ch.queue_declare(queue=queue_name, durable=True)
        # use the channel to publish a message to the queue
        # every message passes through an exchange
        ch.basic_publish(exchange="", routing_key=queue_name, body=message)
        # print a message to the console for the user
        print(f" [x] Sent {message}")
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error: Connection to RabbitMQ server failed: {e}")
        sys.exit(1)
    finally:
        # close the connection to the server
        conn.close()

def get_and_send_message_from_csv(input_file):
    """
    Opens the csv input file and reads each row as a message
    then sends the message to the queue
    """
    with open(input_file, 'r') as file:
        reader = csv.reader(file, delimiter=",")      
        for row in reader:

            # use an fstring to create a message from our data
            
            # get the "smoker" column  
            fstring_message_smoker = f"{row[8]}"
            # prepare a binary (1s and 0s) message to stream
            smoker_message = fstring_message_smoker.encode()    
            # send the message
            send_message(host, smoker_queue_name, smoker_message)

            # get the "region" column
            fstring_message_region = f"{row[9]}"
            # prepare a binary (1s and 0s) message to stream
            region_message = fstring_message_region.encode()   
            # send the message
            send_message(host, region_queue_name, region_message)
            
            # sleep for a second
            time.sleep(2)

# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":  

    # set host and queue name
    host = "localhost"
    smoker_queue_name = "task_queue_smoker"
    region_queue_name = "task_queue_region"

    # if show_offer is turned on (True) then
    # ask the user if they'd like to open the RabbitMQ Admin site 
    show_offer = False
    offer_rabbitmq_admin_site(show_offer) 

    # set input file 
    csv_file = 'data_insurance.csv'

    # get the message from an input file
    # send the message to the queue
    get_and_send_message_from_csv(csv_file)

