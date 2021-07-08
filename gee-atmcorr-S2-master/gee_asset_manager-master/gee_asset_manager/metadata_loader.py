__copyright__ = """

    Copyright 2016 Lukasz Tracewski

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
__license__ = "Apache 2.0"

import ast
import collections
import csv
import logging
import re

ValidationResult = collections.namedtuple('ValidationResult', ['success', 'keys'])


class IllegalPropertyName(Exception):
    pass


def validate_metadata_from_csv(path):
    """
    Check if metadata is ok
    :param path:
    :return: true / false
    """
    all_keys = []

    with open(path, mode='r') as metadata_file:
        logging.info('Running metatdata validator for %s', path)
        success = True
        reader = csv.reader(metadata_file)
        header = next(reader)

        if not properties_allowed(properties=header, validator=allowed_property_key):
            raise IllegalPropertyName('The header has illegal name.')

        for row in reader:
            all_keys.append(row[0])
            if not properties_allowed(properties=row, validator=allowed_property_value):
                success = False

        logging.info('Validation successful') if success else logging.error('Validation failed')

        return ValidationResult(success=success, keys=all_keys)


def load_metadata_from_csv(path):
    """
    Grabs properties from the give csv file. The csv should be organised as follows:
    filename (without extension), property1, property2, ...

    Example:
    id_no,class,category,binomial
    my_file_1,GASTROPODA,EN,Aaadonta constricta
    my_file_2,GASTROPODA,CR,Aaadonta irregularis

    The corresponding files are my_file_1.tif and my_file_2.tif.

    The program will turn the above into a json object:

    { id_no: my_file_1, class: GASTROPODA, category: EN, binomial: Aaadonta constricta},
    { id_no: my_file_2, class: GASTROPODA, category: CR, binomial: Aaadonta irregularis}

    :param path to csv:
    :return: dictionary of dictionaries
    """
    with open(path, mode='r') as metadata_file:
        reader = csv.reader(metadata_file)
        header = next(reader)

        if not properties_allowed(properties=header, validator=allowed_property_key):
            raise IllegalPropertyName()

        metadata = {}

        for row in reader:
#            if properties_allowed(properties=row, validator=allowed_property_value):
            values = []
            for item in row:
                try:
                    values.append(ast.literal_eval(item))
                except (ValueError, SyntaxError) as e:
                    values.append(item)
            metadata[row[0]] = dict(zip(header, values))

        return metadata


def properties_allowed(properties, validator):
    return all(validator(prop) for prop in properties)


def allowed_property_key(prop):
    google_special_properties = ('system:description',
                                 'system:provider_url',
                                 'system:tags',
                                 'system:time_end',
                                 'system:time_start',
                                 'system:title')

    if prop in google_special_properties or re.match("^[A-Za-z0-9_]+$", prop):
        return True
    else:
        logging.warning('Property name %s is invalid. Special properties [system:description, system:provider_url, '
                        'system:tags, system:time_end, system:time_start, system:title] are allowed; other property '
                        'keys must contain only letters, digits and underscores.')
        return False
