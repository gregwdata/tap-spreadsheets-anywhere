'''Provides an object model for a our config file'''
import json
import logging

from voluptuous import Schema, Required, Any, Optional
LOGGER = logging.getLogger(__name__)

CONFIG_CONTRACT = Schema({
    Required('tables'): [{
        Required('path'): str,
        Required('name'): str,
        Required('pattern'): str,
        Required('start_date'): str,
        Required('key_properties'): [str],
        Required('format'): Any('csv', 'excel', 'json', 'detect'),
        Optional('invalid_format_action'): Any('ignore','fail'),
        Optional('universal_newlines'): bool,
        Optional('selected'): bool,
        Optional('field_names'): [str],
        Optional('search_prefix'): str,
        Optional('worksheet_name'): str,
        Optional('delimiter'): str,
        Optional('quotechar'): str,
        Optional('sample_rate'): int,
        Optional('max_sampling_read'): int,
        Optional('max_records_per_run'): int,
        Optional('max_sampled_files'): int,
        Optional('prefer_number_vs_integer'): bool,
        Optional('encoding'): str,
        Optional('encoding_errors'): str,
        Optional('schema_overrides'): {
            str: {
                Required('type'): Any(Any('null','string','integer','number','date-time'),
                                      [Any('null','string','integer','number','date-time')])
            }
        },
        Optional('sharepoint_credentials'): {
            Required('tenant_name'): str,
            Required('client_id'): str,
            Required('client_secret'): str,
            Required('site_name'): str,
            Required('document_library'): str,
            Required('file_path'): str
        }
    }]
})

class Config():

    @classmethod
    def dump(cls, config_json, ostream):
        json.dump(config_json, ostream, indent=2)

    @classmethod
    def validate(cls, config_json):
        CONFIG_CONTRACT(config_json)
        return config_json

    @classmethod
    def load(cls, filename):
        with open(filename) as fp:  # pylint: disable=invalid-name
            return Config.validate(json.load(fp))
