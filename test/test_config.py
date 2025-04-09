import unittest
from unittest.mock import patch, mock_open
import yaml
import json
import os
from pathlib import Path
from pynamixel.config import ConfigManager, YamlConfigLoader, JsonConfigLoader  

class TestConfigManager(unittest.TestCase):

    @patch('builtins.open', mock_open(read_data='{"key": "value"}'))
    @patch('os.path.exists', return_value=True)
    def test_load_config_from_file_json(self, *args, **kwargs):
        config_manager = ConfigManager(file_path='config.json', config_loader_=JsonConfigLoader())
        config_manager.load_config_from_file(file_path='config.json')
        
        # Check that config was loaded properly
        self.assertTrue(config_manager.is_config_initialized)
        self.assertEqual(config_manager['key'], 'value')

    @patch('builtins.open', mock_open(read_data='key: value\n'))
    @patch('os.path.exists', return_value=True)
    def test_load_config_from_file_yaml(self, *args, **kwargs):
        config_manager = ConfigManager(file_path='config.yaml', config_loader_=YamlConfigLoader())
        config_manager.load_config_from_file(file_path='config.yaml')

        # Check that config was loaded properly
        self.assertTrue(config_manager.is_config_initialized)
        self.assertEqual(config_manager['key'], 'value')

    def test_check_path(self):
        yaml_loader = YamlConfigLoader()
        yaml_loader._ConfigLoaderBase__file_path = 'test.yaml'
        
        # Check path from the file
        self.assertEqual(yaml_loader.check_path(None), 'test.yaml')
        
        # Check with provided path
        self.assertEqual(yaml_loader.check_path('config.yaml'), 'config.yaml')
        
        # Ensure it raises an assertion error if file_path is not a string or Path
        with self.assertRaises(AssertionError):
            yaml_loader.check_path(123)

    @patch('os.path.exists', return_value=False)
    def test_load_config_file_not_found(self, *args, **kwargs):
        config_manager = ConfigManager(file_path='config.json', config_loader_=JsonConfigLoader())
        
        with self.assertRaises(FileNotFoundError):
            config_manager.load_config_from_file()
    
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', mock_open())
    def test_save_config_fail(self, *args, **kwargs):
        config_manager = ConfigManager(file_path='config.json', config_loader_=JsonConfigLoader())
        config_manager['key'] = 'value'
        
        # Simulate an error while saving the file (e.g., permission denied)
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = OSError("Permission denied")
            result = config_manager.save_config_to_file()
            self.assertFalse(result)

    def test_invalid_loader_type(self):
        with self.assertRaises(ValueError):
            config_manager = ConfigManager(file_path='config.json', config_loader_="InvalidLoader")
            config_manager.load_config_from_file()


class TestJsonConfigLoader(unittest.TestCase):

    @patch('builtins.open', mock_open(read_data='{"key": "value"}'))
    @patch('os.path.exists', return_value=True)
    def test_load_config_json(self, *args, **kwargs):
        json_loader = JsonConfigLoader()
        json_loader._ConfigLoaderBase__file_path = 'config.json'
        
        config = json_loader.load_config(file_path='config.json')
        
        # Verify that the loaded config matches the expected data
        self.assertEqual(config, {"key": "value"})

    @patch('builtins.open', mock_open())
    def test_save_config_json(self, *args, **kwargs):
        json_loader = JsonConfigLoader()
        config_data = {'key': 'new_value'}

        expected_json = json.dumps(config_data, indent=4)

        with patch('builtins.open', mock_open()) as mock_file:
            json_loader.save_config(config_data, file_path='config.json')
            written_content = ''.join(call[0][0] for call in mock_file().write.call_args_list)
           
            self.assertEqual(written_content, expected_json)

    @patch('os.path.exists', return_value=False)
    def test_load_config_file_not_found(self, *args, **kwargs):
        json_loader = JsonConfigLoader()
        
        with self.assertRaises(FileNotFoundError):
            json_loader.load_config(file_path='non_existent_file.json')
    
    @patch('builtins.open', mock_open())
    def test_save_config_fail(self, *args, **kwargs):
        json_loader = JsonConfigLoader()
        config_data = {"key": "value"}
        
        # Simulate an error during saving (e.g., permission denied)
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = OSError("Permission denied")
            result = json_loader.save_config(config_data, file_path='config.json')
            self.assertFalse(result)

class TestYamlConfigLoader(unittest.TestCase):

    @patch('builtins.open', mock_open(read_data='key: value\n'))
    @patch('os.path.exists', return_value=True)
    def test_load_config_yaml(self, *args, **kwargs):
        yaml_loader = YamlConfigLoader()
        yaml_loader._ConfigLoaderBase__file_path = 'config.yaml'
        
        config = yaml_loader.load_config(file_path='config.yaml')
        
        # Verify that the loaded config matches the expected data
        self.assertEqual(config, {'key': 'value'})

    @patch('builtins.open', mock_open())
    def test_save_config_yaml(self, *args, **kwargs):
        yaml_loader = YamlConfigLoader()
        config_data = {'key': 'new_value'}
        expected_yaml = 'key: new_value\n'

        with patch('builtins.open', mock_open()) as mock_file:
            yaml_loader.save_config(config_data, file_path='config.yaml')
            written_content = ''.join(call[0][0] for call in mock_file().write.call_args_list)
          
            self.assertEqual(written_content, expected_yaml)

    @patch('os.path.exists', return_value=False)
    def test_load_config_file_not_found(self, *args, **kwargs):
        yaml_loader = YamlConfigLoader()
        
        # Check that FileNotFoundError is raised when the file doesn't exist
        with self.assertRaises(FileNotFoundError):
            yaml_loader.load_config(file_path='non_existent_file.yaml')

    @patch('builtins.open', mock_open())
    def test_save_config_fail(self):
        yaml_loader = YamlConfigLoader()
        config_data = {'key': 'value'}
        
        # Simulate an error during saving (e.g., permission denied)
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = OSError("Permission denied")
            result = yaml_loader.save_config(config_data, file_path='config.yaml')
            self.assertFalse(result)


class TestConfigLoaderBase(unittest.TestCase):

    def test_check_path_none(self):
        json_loader = JsonConfigLoader()
        json_loader._ConfigLoaderBase__file_path = 'config.json'
        
        # Test with None passed, it should return the file_path set in the loader
        self.assertEqual(json_loader.check_path(None), 'config.json')

    def test_check_path_invalid(self):
        yaml_loader = YamlConfigLoader()
        
        # Test with invalid file path type
        with self.assertRaises(AssertionError):
            yaml_loader.check_path(123)  # Pass an invalid path type (integer)


if __name__ == '__main__':
    unittest.main()