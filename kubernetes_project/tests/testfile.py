import unittest
import queue_manager.podqueue as pq


""" 
Series of tests.
Comment the while loop out when running the unit tests in podqueue.py
"""

# Creating a message object
def create_fake_message(message):
    class Message:
        def __init__(self, body):
            self.body = body

    fake_msg = Message
    # Message format is ![sub-domain;messageId;numberOfMessagesInBatch;fakeCpuValueToBeUsed;fakeMemoryValueToBeUsed]
    fake_msg.body = message

    return fake_msg


# Test message functions
class TestMessage(unittest.TestCase):

    # Test the deconstruct message function
    def test_deconstruct_msg(self):

        fake_msg = create_fake_message('![blobcontainer753;789314;87;.3;649]')
        container_name, blob_item, cpu_usage, memory_usage = pq.deconstruct_message(fake_msg)

        self.assertNotEqual(container_name, '')
        self.assertEqual(container_name, 'blobcontainer753')
        self.assertNotEqual(blob_item, '')
        self.assertEqual(blob_item, '789314')
        self.assertNotEqual(cpu_usage, '')
        self.assertEqual(cpu_usage, '.3')
        self.assertNotEqual(memory_usage, '')
        self.assertEqual(memory_usage, '649')


# Test container functions
class TestContainer(unittest.TestCase):

    # Test the creation of a container
    def test_make_container(self):
        # Test the creation of a pod config file
        fake_msg = create_fake_message('![blobcontainer23;14;3;.5;177]')
        fake_id = 'id154'

        container = pq.make_container(fake_msg, fake_id)

        self.assertIsNotNone(container)

    # Test if the vars are set correctly
    def test_container_vars(self):
        # Test the creation of a pod config file
        fake_msg = create_fake_message('![blobcontainer23;14;3;20;100000000]')
        fake_id = 'id154'

        container = pq.make_container(fake_msg, fake_id)

        self.assertIsNotNone(container.image)
        self.assertEqual(container.resources.requests['cpu'], '.5')
        self.assertEqual(container.resources.requests['memory'], '125Mi')

    # Test if the env vars are set correctly
    def test_container_env_vars(self):
        # Test the creation of a pod config file
        fake_msg = create_fake_message('![blobcontainer23;14;3;.5;177]')
        fake_id = 'id154'

        container = pq.make_container(fake_msg, fake_id)

        self.assertEqual(container.env[0].value, 'blobcontainer23')
        self.assertEqual(container.env[1].value, '14')
        self.assertEqual(container.env[4].value, '177')
        self.assertEqual(container.env[5].value, '.5')
        self.assertEqual(container.env[6].value, 'id154')
        self.assertIsNotNone(container.env[2].value)
        self.assertIsNotNone(container.env[3].value)
        self.assertIsNotNone(container.env[7].value)
        self.assertIsNotNone(container.env[8].value)
        self.assertNotEqual(container.env[2].value, '')
        self.assertNotEqual(container.env[3].value, '')
        self.assertNotEqual(container.env[7].value, '')
        self.assertNotEqual(container.env[8].value, '')


if __name__ == '__main__':
    unittest.main()
