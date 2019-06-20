import pika, random, time, json, os, yaml, tqdm
import pywren_ibm_cloud as pywren
from BarDisplay import BarDisplay

class MonitorCallback():
    def __init__ (self, progbars):
        self.progbars = progbars
        self.progbars.show()

    def __call__(self, ch, method, properties, body):
        
        msg = body.decode('utf-8')

        workerid = int(msg[:2])
        jobdone = int(msg[3:])

        #print('id:',workerid, 'job:',jobdone)
        self.progbars.update(workerid, jobdone)

        if progbars.isDone():
            ch.stop_consuming()

def worker(args):
    pw_config = json.loads(os.environ.get('PYWREN_CONFIG', ''))
    pika_params = pika.URLParameters(pw_config['rabbitmq']['amqp_url'])
    connection = pika.BlockingConnection(pika_params)
    channel = connection.channel()
    
    time_to_work = 100

    while time_to_work > 0:
        worksession = random.randint(0, time_to_work)
        time.sleep(worksession/10)
        channel.publish(exchange='', routing_key=args['qid'], body='{:02}:{}'.format(args['worker_id'], worksession))
        time_to_work = time_to_work - worksession

    channel.publish(exchange='', routing_key=args['qid'], body='{:02}:{}'.format(args['worker_id'], -1))

if __name__ == '__main__':
    with open(os.path.expanduser('~/.pywren_config'), 'r') as f:
        secret = yaml.safe_load(f)
    pika_params = pika.URLParameters(secret['rabbitmq']['amqp_url'])
    connection = pika.BlockingConnection(pika_params)
    channel = connection.channel()

    iterdata = [[{'worker_id':i*5, 'qid':'master-queue'}] for i in range(0, 5)]
    progbars = BarDisplay([i[0]['worker_id'] for i in iterdata])

    channel.queue_declare(queue='master-queue')
    try:
        pw = pywren.ibm_cf_executor(rabbitmq_monitor=True)
        pw.map(worker, iterdata)
        channel.basic_consume(consumer_callback=MonitorCallback(progbars), queue='master-queue')
        channel.start_consuming()
        #result = pw.get_result()
        #print(result)
    finally:
        channel.queue_delete(queue='master-queue')
        print('Deleted the queue.')
