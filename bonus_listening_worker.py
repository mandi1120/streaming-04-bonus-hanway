"""
Author: Amanda Hanway 
Assignment: Bonus - A4: Producer with Multiple Consumers
Date: 1/29/23
Purpose: 
    This program continuously listens for messages on two queues
    When a message is received, it transforms the data and writes to an output file 
       
Csv data source: insurance_data.csv
https://www.kaggle.com/datasets/thedevastator/insurance-claim-analysis-demographic-and-health?resource=download      
"""

import pika
import sys
import time
import csv

# define a callback function to be called when a message is received
def callback1(ch, method, properties, body):
    """ Define behavior on getting a message."""
    # decode the binary message body to a string
    print(f" [x] Received {body.decode()}")
    # simulate work by sleeping for the number of dots in the message
    time.sleep(body.count(b"."))

    # process smoker column
    #if task_queue == "task_queue_smoker":
    # change yes/no to TRUE/FALSE, then write to output file 
    smoker_str = body.decode()
    smoker_list = [body.decode()]
    with open(smoker_output_file, "a", newline='') as output_file:
        writer_smoker = csv.writer(output_file, delimiter=',')  
        if smoker_str.lower() == "yes":
            smoker_list.append("TRUE")
        elif smoker_str.lower() == "no":
            smoker_list.append("FALSE")
        elif smoker_str.lower() == "smoker":
            smoker_list.append("NEW_SMOKER_COLUMN")
        else:
            smoker_list.append("UNKNOWN")
        writer_smoker.writerow(smoker_list)

    # when done with task, tell the user
    print(" [x] Done.")
    # acknowledge the message was received and processed 
    # (now it can be deleted from the queue)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# define a callback function to be called when a message is received
def callback2(ch, method, properties, body):
    """ Define behavior on getting a message."""
    # decode the binary message body to a string
    print(f" [x] Received {body.decode()}")
    # simulate work by sleeping for the number of dots in the message
    time.sleep(body.count(b"."))

    #process region column
    # change region to uppercase, then write to output file 
    region_str = body.decode()
    region_list = [body.decode()]
    with open(region_output_file, "a", newline='') as output_file:
        writer_region = csv.writer(output_file, delimiter=',')  
        if region_str.lower() == "region":
            region_list.append("NEW_REGION_COLUMN")
        elif region_str.lower() in ("southeast", "southwest", "northeast", "northwest"):
            region_list.append(region_str.upper())
        else:
            region_list.append("UNKNOWN")
        writer_region.writerow(region_list)

    # when done with task, tell the user
    print(" [x] Done.")
    # acknowledge the message was received and processed 
    # (now it can be deleted from the queue)
    ch.basic_ack(delivery_tag=method.delivery_tag)


# define a main function to run the program
def main(hn: str = "localhost", qn: str = "task_queue"):
    """ Continuously listen for task messages on a named queue."""

    # when a statement can go wrong, use a try-except block
    try:
        # try this code, if it works, keep going
        # create a blocking connection to the RabbitMQ server
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=hn))

    # except, if there's an error, do this
    except Exception as e:
        print()
        print("ERROR: connection to RabbitMQ server failed.")
        print(f"Verify the server is running on host={hn}.")
        print(f"The error says: {e}")
        print()
        sys.exit(1)

    try:
        # use the connection to create a communication channel for each queue
        channel1 = connection.channel()
        channel2 = connection.channel()

        # use the channel to declare a durable queue
        # a durable queue will survive a RabbitMQ server restart
        # and help ensure messages are processed in order
        # messages will not be deleted until the consumer acknowledges
        channel1.queue_declare(queue="task_queue_smoker", durable=True)
        channel2.queue_declare(queue="task_queue_region", durable=True)

        # The QoS level controls the # of messages
        # that can be in-flight (unacknowledged by the consumer)
        # at any given time.
        # Set the prefetch count to one to limit the number of messages
        # being consumed and processed concurrently.
        # This helps prevent a worker from becoming overwhelmed
        # and improve the overall system performance. 
        # prefetch_count = Per consumer limit of unaknowledged messages      
        channel1.basic_qos(prefetch_count=1) 
        channel2.basic_qos(prefetch_count=1) 

        # configure the channel to listen on a specific queue,  
        # use the callback function for the associated queue/channel,
        # and do not auto-acknowledge the message (let the callback handle it)
        channel1.basic_consume(queue="task_queue_smoker", on_message_callback=callback1)
        channel2.basic_consume(queue="task_queue_region", on_message_callback=callback2)

        # print a message to the console for the user
        print(" [*] Ready for work. To exit press CTRL+C")

        # start consuming messages via the communication channel
        channel1.start_consuming()
        channel2.start_consuming()

    # except, in the event of an error OR user stops the process, do this
    except Exception as e:
        print()
        print("ERROR: something went wrong.")
        print(f"The error says: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print()
        print(" User interrupted continuous listening process.")
        sys.exit(0)
    finally:
        print("\nClosing connection. Goodbye.\n")
        connection.close()


# Standard Python idiom to indicate main program entry point
# This allows us to import this module and use its functions
# without executing the code below.
# If this is the program being run, then execute the code below
if __name__ == "__main__":
    # call the main function with the information needed
    smoker_output_file = "data_smoker_output.csv"
    region_output_file = "data_region_output.csv"

    main("localhost", "task_queue_smoker")
    main("localhost", "task_queue_region")

