import unittest
from unittest.mock import patch, mock_open
import os

from extract_versions import write_to_csv


class TestCSVWriting(unittest.TestCase):
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_to_csv_new_file(self, mock_file, mock_isfile):
        mock_isfile.return_value = False
        items = [{'id': 1, 'name': 'Test'}]
        fieldnames = ['id', 'name']
        filename = 'test.csv'
        
        result = write_to_csv(items, fieldnames, filename)
        self.assertTrue(result)
        mock_file.assert_called_with(filename, mode='a', newline='', encoding='utf-8')
        handle = mock_file()
        handle.write.assert_any_call('id,name\r\n')
        handle.write.assert_any_call('1,Test\r\n')
        # result = write_to_csv(items, fieldnames, filename)


    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open)
    def test_write_to_csv_existing_file(self, mock_file, mock_isfile):
        # mock_isfile.return_value = True
        items = [{'id': 2, 'name': 'Another Test'}]
        fieldnames = ['id', 'name']
        filename = 'test.csv'
        result = write_to_csv(items, fieldnames, filename)
        self.assertTrue(result)
        mock_file.assert_called_with(filename, mode='a', newline='', encoding='utf-8')
        handle = mock_file()
        handle.write.assert_any_call('2,Another Test\r\n')

if __name__ == '__main__':
    unittest.main()
    items = [{'id': 1, 'name': 'Test'}]
    fieldnames = ['id', 'name']
    filename = 'test.csv'
    
    result = write_to_csv(items, fieldnames, filename)
    print(result)   