#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from .BuildDocumentLocatorFromYamlAst import create_document_locator_from_yaml_text


def create_path_document_yaml_coordinates_pseudo_json_locator(text: str):
    return create_document_locator_from_yaml_text(text)


def get_path_document_yaml_coordinates_pseudo_json(path: list[object], document: str) -> dict[str, object]:
    return create_path_document_yaml_coordinates_pseudo_json_locator(document)(path)
