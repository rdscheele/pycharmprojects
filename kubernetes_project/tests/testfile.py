import unittest
import queue_manager.podqueue as pq
import numpy

class TestDeconstructMessage(unittest.TestCase):

    def test_deconstruct_msg(self):
        # Message format is sub-domain;messageId;numberOfMessagesInBatch;fakeCpuValueToBeUsed;fakeMemoryValueToBeUsed
        fake_msg = 'blobcontainer753;789314;87;.3;649'

        container_name, blob_item, cpu_usage, memory_usage = pq.deconstruct_message(fake_msg)

        self.assertNotEqual(container_name, '')
        self.assertEqual(container_name, 'blobcontainer753')
        self.assertNotEqual(blob_item, '')
        self.assertEqual(blob_item, '789314')
        self.assertNotEqual(cpu_usage, '')
        self.assertEqual(cpu_usage, '.3')
        self.assertNotEqual(memory_usage, '')
        self.assertEqual(memory_usage, '649')


if __name__ == '__main__':
    unittest.main()

