#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from .BuildDocumentLocatorFromYamlAst import create_document_locator_from_yaml_text


def get_path_document_coordinates_pseudo_json(path: list[object], document: str) -> dict[str, object]:
    try:
        return create_document_locator_from_yaml_text(document)(path)
    except Exception:
        return {'row': 1, 'col': 1}
